from __future__ import annotations

import time
from typing import Optional, Sequence, Callable, Any

import numpy as np

from netcl.core.tensor import Tensor
from netcl import autograd as ag
from netcl.optim import AMPGradScaler
from netcl.amp import autocast
from netcl.utils import ProgressBar
from netcl.core.device import manager
from netcl import autograd as ag
from netcl.core.tensor import Tensor


class Trainer:
    def __init__(
        self,
        model: Callable,
        optimizer,
        device_queue=None,
        mixed_precision: bool = False,
        grad_clip: Optional[float] = None,
        loss_fn: Callable | None = None,
    ):
        self.model = model
        self.optimizer = optimizer
        if device_queue is None:
            dev = manager.default()
            if dev is None:
                raise RuntimeError("No OpenCL device available")
            self.queue = dev.queue
        else:
            self.queue = device_queue
        self.mixed_precision = mixed_precision
        self.grad_clip = grad_clip
        self.scaler = AMPGradScaler(init_scale=2.0**12) if mixed_precision else None
        self.loss_fn = loss_fn

    def fit(
        self,
        train_loader,
        val_loader=None,
        epochs: int = 1,
        loss_fn: Callable = None,
        log_every: int = 1,
    ):
        if loss_fn is None:
            loss_fn = self.loss_fn
        if loss_fn is None:
            from netcl.nn import functional

            loss_fn = functional.cross_entropy
        for epoch in range(1, epochs + 1):
            t0 = time.perf_counter()
            # set model to training mode if present
            if hasattr(self.model, "training"):
                self.model.training = True
            pb = ProgressBar(total=len(train_loader), epoch=epoch)
            train_loss = 0.0
            total = 0
            correct = 0
            for i, (xb, yb) in enumerate(train_loader):
                logits, loss, tape = self._forward_backward(xb, yb, loss_fn)
                self._step()
                train_loss += float(loss.value.to_host()[0])
                preds = np.argmax(logits.value.to_host(), axis=1)
                labels = yb if yb.ndim == 1 else np.argmax(yb, axis=1)
                correct += int((preds == labels).sum())
                total += labels.size
                pb.update(i + 1, {"loss": f"{loss.value.to_host()[0]:.3f}", "acc": f"{(preds==labels).mean()*100:.1f}%"})
            pb.close()
            elapsed = time.perf_counter() - t0
            acc = correct / max(1, total)
            print(f"Epoch {epoch}: train_loss={train_loss/len(train_loader):.4f} acc={acc*100:.2f}% throughput={total/elapsed:.1f} img/s")
            if val_loader and epoch % log_every == 0:
                self.evaluate(val_loader, loss_fn=loss_fn)

    def evaluate(self, data_loader, loss_fn: Callable):
        if hasattr(self.model, "training"):
            prev = getattr(self.model, "training")
            self.model.training = False
        else:
            prev = None
        if loss_fn is None:
            loss_fn = self.loss_fn
        if loss_fn is None:
            from netcl.nn import functional

            loss_fn = functional.cross_entropy
        total = 0
        correct = 0
        loss_total = 0.0
        for xb, yb in data_loader:
            logits, loss, _ = self._forward(xb, yb, loss_fn)
            loss_total += float(loss.value.to_host()[0])
            preds = np.argmax(logits.value.to_host(), axis=1)
            labels = yb if yb.ndim == 1 else np.argmax(yb, axis=1)
            correct += int((preds == labels).sum())
            total += labels.size
        print(f"Val: loss={loss_total/len(data_loader):.4f} acc={correct/max(1,total)*100:.2f}%")
        if prev is not None:
            self.model.training = prev

    def _forward(self, xb, yb, loss_fn: Callable):
        tape = ag.Tape()
        ag.set_current_tape(tape)
        try:
            x_node = ag.tensor(Tensor.from_host(self.queue, xb))
            with autocast(enabled=self.mixed_precision):
                logits_raw = self.model(x_node)
                # accept Tensor or Node
                if hasattr(logits_raw, "value"):
                    logits_tensor = logits_raw.value
                    logits_node = logits_raw
                    logits_node.requires_grad = True
                else:
                    logits_tensor = logits_raw
                    logits_node = ag.tensor(logits_tensor, requires_grad=True)
                # allow integer labels; convert to one-hot using logits dim
                y_array = yb
                if y_array.ndim == 1:
                    num_classes = logits_tensor.shape[1]
                    y_oh = np.eye(num_classes, dtype=np.float32)[y_array.astype(np.int64)]
                    y_onehot = ag.tensor(Tensor.from_host(self.queue, y_oh))
                else:
                    y_onehot = ag.tensor(Tensor.from_host(self.queue, y_array))
                loss = loss_fn(logits_node, y_onehot)
            if self.mixed_precision and self.scaler:
                scaled_loss = self.scaler.scale_loss(loss.value)
                loss = ag.tensor(scaled_loss)
            return logits_node, loss, tape
        finally:
            ag.set_current_tape(None)

    def _forward_backward(self, xb, yb, loss_fn: Callable):
        logits, loss, tape = self._forward(xb, yb, loss_fn)
        tape.backward(loss)
        return logits, loss, tape

    def _step(self):
        if self.mixed_precision and self.scaler:
            self.scaler.step(self.optimizer, [])  # optimizer holds params
        else:
            self.optimizer.step()
        self.optimizer.zero_grad()

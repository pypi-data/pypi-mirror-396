from __future__ import annotations

from typing import List, Tuple, Callable, Any

from netcl.core.tensor import Tensor


class Module:
    def parameters(self) -> List[Tensor]:
        params = []
        for v in self.__dict__.values():
            if isinstance(v, Tensor):
                params.append(v)
            elif isinstance(v, Module):
                params.extend(v.parameters())
            elif isinstance(v, (list, tuple)):
                for it in v:
                    if isinstance(it, Tensor):
                        params.append(it)
                    elif isinstance(it, Module):
                        params.extend(it.parameters())
        return params

    def train(self):
        if hasattr(self, "training"):
            self.training = True
        for v in self.__dict__.values():
            if isinstance(v, Module):
                v.train()
        return self

    def eval(self):
        if hasattr(self, "training"):
            self.training = False
        for v in self.__dict__.values():
            if isinstance(v, Module):
                v.eval()
        return self

    def state_dict(self):
        state = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Tensor):
                state[k] = v.to_host()
            elif isinstance(v, Module):
                state[k] = v.state_dict()
        return state

    def load_state_dict(self, state):
        for k, v in state.items():
            if k not in self.__dict__:
                continue
            cur = self.__dict__[k]
            if isinstance(cur, Tensor):
                import pyopencl as cl
                cl.enqueue_copy(cur.queue, cur.buffer, v.astype(cur.to_host().dtype)).wait()
            elif isinstance(cur, Module):
                cur.load_state_dict(v)
        return self


class Sequential(Module):
    def __init__(self, *layers):
        self.layers = list(layers)

    def __call__(self, x):
        out = x
        for layer in self.layers:
            # unwrap Node to Tensor if needed
            val = out.value if hasattr(out, "value") else out
            out = layer(val)
        return out


class Callback:
    def on_epoch_start(self, epoch: int, logs: dict[str, Any] | None = None):
        ...

    def on_epoch_end(self, epoch: int, logs: dict[str, Any] | None = None):
        ...

    def on_batch_end(self, batch: int, logs: dict[str, Any] | None = None):
        ...


class CallbackList:
    def __init__(self, callbacks: List[Callback]):
        self.callbacks = callbacks

    def epoch_start(self, epoch, logs=None):
        for cb in self.callbacks:
            cb.on_epoch_start(epoch, logs)

    def epoch_end(self, epoch, logs=None):
        for cb in self.callbacks:
            cb.on_epoch_end(epoch, logs)

    def batch_end(self, batch, logs=None):
        for cb in self.callbacks:
            cb.on_batch_end(batch, logs)

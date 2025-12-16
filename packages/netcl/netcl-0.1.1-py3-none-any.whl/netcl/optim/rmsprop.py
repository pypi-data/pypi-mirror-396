from __future__ import annotations

from typing import Iterable

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor
from netcl.amp import master_param


class RMSProp:
    def __init__(self, params: Iterable[Tensor], lr: float = 1e-3, alpha: float = 0.99, eps: float = 1e-8, weight_decay: float = 0.0, momentum: float = 0.0):
        self.params = [master_param(p) for p in params]
        if lr <= 0:
            raise ValueError("lr must be positive")
        self.lr = lr
        self.alpha = alpha
        if eps <= 0:
            raise ValueError("eps must be positive")
        self.eps = eps
        self.weight_decay = weight_decay
        self.momentum = momentum
        self.square_avg = {id(p): np.zeros(p.shape, dtype=np.float32) for p in self.params}
        self.mom = {id(p): np.zeros(p.shape, dtype=np.float32) for p in self.params} if momentum > 0 else None

    def zero_grad(self):
        for p in self.params:
            p.grad = None

    def step(self):
        for p in self.params:
            if p.grad is None:
                continue
            g = p.grad.to_host()
            if self.weight_decay != 0.0:
                g = g + self.weight_decay * p.to_host()
            pid = id(p)
            sq = self.square_avg[pid] = self.alpha * self.square_avg[pid] + (1 - self.alpha) * (g * g)
            denom = np.sqrt(sq) + self.eps
            step = g / denom
            if self.mom is not None:
                m = self.mom[pid] = self.momentum * self.mom[pid] + self.lr * step
                update = m
            else:
                update = self.lr * step
            new_val = p.to_host() - update
            cl.enqueue_copy(p.queue, p.buffer, new_val).wait()
            model_p = getattr(p, "_model_param", p)
            if model_p is not p:
                cl.enqueue_copy(model_p.queue, model_p.buffer, new_val.astype(np.float16)).wait()

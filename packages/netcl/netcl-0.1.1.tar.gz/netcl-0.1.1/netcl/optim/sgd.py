from __future__ import annotations

from typing import Iterable

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor
from netcl.amp import master_param


class SGD:
    def __init__(self, params: Iterable[Tensor], lr: float = 1e-2, momentum: float = 0.0, weight_decay: float = 0.0):
        self.params = [master_param(p) for p in params]
        if lr <= 0:
            raise ValueError("lr must be positive")
        self.lr = lr
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.velocity = {id(p): np.zeros(p.shape, dtype=np.float32) for p in self.params}

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
            v = self.velocity[id(p)]
            if self.momentum != 0.0:
                v = self.momentum * v + g
                self.velocity[id(p)] = v
                g = v
            new_val = p.to_host() - self.lr * g
            cl.enqueue_copy(p.queue, p.buffer, new_val).wait()
            model_p = getattr(p, "_model_param", p)
            if model_p is not p:
                # cast back to model dtype if needed
                cl.enqueue_copy(model_p.queue, model_p.buffer, new_val.astype(np.float16)).wait()

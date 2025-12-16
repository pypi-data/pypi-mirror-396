from __future__ import annotations

from typing import Iterable

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor
from netcl.amp import master_param


class Momentum:
    def __init__(self, params: Iterable[Tensor], lr: float = 0.01, momentum: float = 0.9, nesterov: bool = False, weight_decay: float = 0.0):
        self.params = [master_param(p) for p in params]
        self.lr = lr
        self.momentum = momentum
        self.nesterov = nesterov
        self.weight_decay = weight_decay
        self.vel = {id(p): np.zeros(p.shape, dtype=np.float32) for p in self.params}

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
            v = self.vel[id(p)] = self.momentum * self.vel[id(p)] + g
            if self.nesterov:
                update = g + self.momentum * v
            else:
                update = v
            new_val = p.to_host() - self.lr * update
            cl.enqueue_copy(p.queue, p.buffer, new_val).wait()

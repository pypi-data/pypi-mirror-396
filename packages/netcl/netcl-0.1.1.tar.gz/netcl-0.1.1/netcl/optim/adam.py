from __future__ import annotations

from typing import Iterable

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor
from netcl.amp import master_param


class Adam:
    def __init__(
        self,
        params: Iterable[Tensor],
        lr: float = 1e-3,
        betas=(0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.0,
    ):
        self.params = [master_param(p) for p in params]
        self.lr = lr
        if len(betas) != 2:
            raise ValueError("betas must be a tuple of (beta1, beta2)")
        self.beta1, self.beta2 = betas
        if eps <= 0:
            raise ValueError("eps must be positive")
        self.eps = eps
        self.weight_decay = weight_decay
        self.m = {id(p): np.zeros(p.shape, dtype=np.float32) for p in self.params}
        self.v = {id(p): np.zeros(p.shape, dtype=np.float32) for p in self.params}
        self.t = 0

    def zero_grad(self):
        for p in self.params:
            p.grad = None

    def step(self):
        self.t += 1
        for p in self.params:
            if p.grad is None:
                continue
            g = p.grad.to_host()
            if self.weight_decay != 0.0:
                g = g + self.weight_decay * p.to_host()
            pid = id(p)
            m = self.m[pid] = self.beta1 * self.m[pid] + (1 - self.beta1) * g
            v = self.v[pid] = self.beta2 * self.v[pid] + (1 - self.beta2) * (g * g)
            m_hat = m / (1 - self.beta1**self.t)
            v_hat = v / (1 - self.beta2**self.t)
            new_val = p.to_host() - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
            cl.enqueue_copy(p.queue, p.buffer, new_val).wait()
            model_p = getattr(p, "_model_param", p)
            if model_p is not p:
                cl.enqueue_copy(model_p.queue, model_p.buffer, new_val.astype(np.float16)).wait()

from __future__ import annotations

from typing import Iterable

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor


class GradScaler:
    """
    Minimal grad scaler for AMP-like workflow (loss scaling). Does not convert kernels to fp16; scales grads host-side.
    """

    def __init__(self, scale: float = 1024.0, growth_factor: float = 2.0, backoff_factor: float = 0.5, growth_interval: int = 2000):
        self.scale = scale
        self.growth_factor = growth_factor
        self.backoff_factor = backoff_factor
        self.growth_interval = growth_interval
        self._good_steps = 0

    def unscale_(self, params: Iterable[Tensor]):
        for p in params:
            if p.grad is None:
                continue
            g = p.grad.to_host() / self.scale
            cl.enqueue_copy(p.queue, p.grad.buffer, g).wait()

    def update(self, overflow: bool):
        if overflow:
            self.scale *= self.backoff_factor
            self._good_steps = 0
        else:
            self._good_steps += 1
            if self._good_steps % self.growth_interval == 0:
                self.scale *= self.growth_factor

    def scale_loss(self, loss: Tensor) -> Tensor:
        # loss is 1-element tensor
        scaled = loss.to_host() * self.scale
        return Tensor.from_host(loss.queue, scaled.astype(np.float32))

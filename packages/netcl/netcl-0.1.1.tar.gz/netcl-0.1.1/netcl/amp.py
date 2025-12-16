from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

from netcl.core.tensor import Tensor
from netcl.core.tensor import _np_dtype  # type: ignore

_AUTOCAST_ENABLED = False


@dataclass
class GradScaler:
    init_scale: float = 2.0**16
    growth_factor: float = 2.0
    backoff_factor: float = 0.5
    growth_interval: int = 2000
    enabled: bool = True

    def __post_init__(self):
        self._scale = self.init_scale
        self._growth_tracker = 0

    @property
    def scale(self) -> float:
        return self._scale

    def scale_loss(self, loss: Tensor) -> Tensor:
        if not self.enabled:
            return loss
        from netcl.ops.elementwise import elementwise_binary

        return elementwise_binary(loss, loss, expression=f"MUL(v0, {float(self._scale)})")

    def unscale_grads(self, params: Sequence[Tensor]):
        if not self.enabled:
            return False
        found_inf = False
        for p in params:
            if p.grad is None:
                continue
            g = p.grad.to_host()
            if np.any(~np.isfinite(g)):
                found_inf = True
                break
        if not found_inf:
            inv_scale = 1.0 / self._scale
            from netcl.ops.elementwise import elementwise_binary

            for p in params:
                if p.grad is None:
                    continue
                p.grad = elementwise_binary(p.grad, p.grad, expression=f"MUL(v0, {inv_scale})")
        return found_inf

    def step(self, optimizer, params: Sequence[Tensor]):
        if not self.enabled:
            optimizer.step()
            return
        found_inf = self.unscale_grads(params)
        if not found_inf:
            optimizer.step()
            self._growth_tracker += 1
            if self._growth_tracker % self.growth_interval == 0:
                self._scale *= self.growth_factor
        else:
            self._scale *= self.backoff_factor
            self._growth_tracker = 0

    def update(self):
        # no-op kept for API compatibility
        pass


def supports_fp16(queue) -> bool:
    """
    Check device extensions for cl_khr_fp16 support.
    """
    try:
        return "cl_khr_fp16" in queue.device.extensions
    except Exception:
        return False


def autocast_enabled(profile_supports_fp16: bool) -> bool:
    return profile_supports_fp16


class autocast:
    """
    Context manager for autocast. Enables casting only if underlying device supports fp16.
    """

    def __init__(self, enabled: bool = True, device_queue=None):
        self.enabled = enabled
        self.device_queue = device_queue
        self.prev = False
        self._capable = True

    def __enter__(self):
        global _AUTOCAST_ENABLED
        self.prev = _AUTOCAST_ENABLED
        if not self.enabled:
            _AUTOCAST_ENABLED = False
            return self
        if self.device_queue is not None:
            self._capable = supports_fp16(self.device_queue)
        _AUTOCAST_ENABLED = self.enabled and self._capable
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _AUTOCAST_ENABLED
        _AUTOCAST_ENABLED = self.prev
        return False


def is_autocast_enabled() -> bool:
    return _AUTOCAST_ENABLED


def maybe_cast_tensor(t: Tensor) -> Tensor:
    if not _AUTOCAST_ENABLED:
        return t
    if t.dtype in ("float", "float32"):
        # only cast if device can handle fp16
        if supports_fp16(t.queue):
            arr = t.to_host().astype(np.float16)
            return Tensor.from_host(t.queue, arr, dtype="float16")
        return t
    return t


def master_param(param: Tensor) -> Tensor:
    """
    Keep master weights in FP32 for optimizers.
    """
    if param.dtype in ("float16", "half"):
        master = Tensor.from_host(param.queue, param.to_host().astype(np.float32), dtype="float32")
        setattr(master, "_model_param", param)
        return master
    setattr(param, "_model_param", param)
    return param

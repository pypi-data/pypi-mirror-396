from __future__ import annotations

import math

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor


def _fill_tensor(tensor: Tensor, data: np.ndarray) -> None:
    cl.enqueue_copy(tensor.queue, tensor.buffer, data.astype(np.float32)).wait()


def xavier_uniform(tensor: Tensor) -> None:
    if tensor.dtype not in ("float", "float32"):
        raise ValueError("xavier_uniform supports float32")
    if len(tensor.shape) < 2:
        # fallback
        scale = math.sqrt(6.0 / max(1, sum(tensor.shape)))
    else:
        fan_in, fan_out = tensor.shape[0], tensor.shape[1]
        scale = math.sqrt(6.0 / float(fan_in + fan_out))
    data = np.random.uniform(-scale, scale, size=tensor.shape).astype(np.float32)
    _fill_tensor(tensor, data)


def kaiming_uniform(tensor: Tensor, a: float = math.sqrt(5.0)) -> None:
    if tensor.dtype not in ("float", "float32"):
        raise ValueError("kaiming_uniform supports float32")
    fan_in = tensor.shape[1] if len(tensor.shape) >= 2 else tensor.shape[0]
    bound = math.sqrt(3.0) * math.sqrt(2.0 / fan_in)
    data = np.random.uniform(-bound, bound, size=tensor.shape).astype(np.float32)
    _fill_tensor(tensor, data)

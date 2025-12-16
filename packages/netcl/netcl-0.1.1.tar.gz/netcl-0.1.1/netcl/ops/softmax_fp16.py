"""
FP16-tolerant softmax wrapper: accumulates in float32 for stability.
"""

from __future__ import annotations

from typing import Optional

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

from netcl.core.tensor import Tensor


def softmax_fp16_safe(x: Tensor) -> Tensor:
    """
    Convert to fp32, run softmax, cast back to fp16.
    """
    if x.dtype not in ("half", "float16"):
        raise ValueError("softmax_fp16_safe expects fp16 input")
    x32 = Tensor.from_host(x.queue, x.to_host().astype(np.float32))
    from netcl.ops.softmax import softmax

    out32 = softmax(x32)
    out16 = Tensor.from_host(out32.queue, out32.to_host().astype(np.float16), dtype="float16")
    return out16

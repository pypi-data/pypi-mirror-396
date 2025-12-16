from __future__ import annotations

import numpy as np

from netcl.core.tensor import Tensor
from netcl.ops.reduction import reduce_sum
from netcl.ops.elementwise import elementwise_binary


def clip_grad_norm(params, max_norm: float):
    """
    Clip gradients of params to max_norm (L2). Operates host-side norm, scales on device.
    """
    grads = [p.grad for p in params if getattr(p, "grad", None) is not None]
    if not grads:
        return 0.0
    # host norm
    total = 0.0
    for g in grads:
        gh = g.to_host()
        total += float(np.sum(gh * gh))
    norm = np.sqrt(total)
    if norm <= max_norm or norm == 0:
        return norm
    scale = max_norm / norm
    for g in grads:
        elementwise_binary(g, g, expression=f"MUL(v0, {scale})", out=g)
    return norm

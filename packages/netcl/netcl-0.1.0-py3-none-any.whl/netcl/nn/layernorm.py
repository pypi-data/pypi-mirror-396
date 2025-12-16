from __future__ import annotations

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor

_DTYPE_CNAME = {"float": "float", "float32": "float"}


def layer_norm(x: Tensor, gamma: Tensor, beta: Tensor, eps: float = 1e-5):
    """
    LayerNorm over last dimension. mean/var computed on host for simplicity.
    """
    if x.dtype != "float32":
        raise ValueError("layer_norm supports float32")
    x_host = x.to_host()
    mean = x_host.mean(axis=-1, keepdims=True)
    var = x_host.var(axis=-1, keepdims=True)
    norm = (x_host - mean) / np.sqrt(var + eps)
    out_host = norm * gamma.to_host() + beta.to_host()
    return Tensor.from_host(x.queue, out_host.astype(np.float32)), Tensor.from_host(x.queue, mean.astype(np.float32)), Tensor.from_host(x.queue, var.astype(np.float32))


def layer_norm_backward(x: Tensor, gamma: Tensor, grad_out: Tensor, mean: Tensor, var: Tensor, eps: float = 1e-5):
    xh = x.to_host()
    go = grad_out.to_host()
    mean_h = mean.to_host()
    var_h = var.to_host()
    inv = 1.0 / np.sqrt(var_h + eps)
    xn = (xh - mean_h) * inv
    grad_gamma = (go * xn).sum(axis=tuple(range(len(xh.shape)-1)))
    grad_beta = go.sum(axis=tuple(range(len(xh.shape)-1)))
    # grad_x
    d_y = go * gamma.to_host()
    N = xh.shape[-1]
    dvar = (-0.5) * np.sum(d_y * (xh - mean_h) * inv**3, axis=-1, keepdims=True)
    dmean = -np.sum(d_y * inv, axis=-1, keepdims=True) - 2.0 * dvar * np.mean(xh - mean_h, axis=-1, keepdims=True)
    grad_x = d_y * inv + dvar * 2 * (xh - mean_h) / N + dmean / N
    q = x.queue
    return Tensor.from_host(q, grad_x.astype(np.float32)), Tensor.from_host(q, grad_gamma.astype(np.float32)), Tensor.from_host(q, grad_beta.astype(np.float32))

from __future__ import annotations

import numpy as np

from netcl.core.tensor import Tensor


def group_norm(x: Tensor, gamma: Tensor, beta: Tensor, groups: int, eps: float = 1e-5):
    """
    GroupNorm over NCHW, groups divides C. Host-based mean/var per group.
    """
    N, C, H, W = x.shape
    if C % groups != 0:
        raise ValueError("channels not divisible by groups")
    xh = x.to_host()
    xh = xh.reshape(N, groups, C // groups, H, W)
    mean = xh.mean(axis=(2, 3, 4), keepdims=True)
    var = xh.var(axis=(2, 3, 4), keepdims=True)
    norm = (xh - mean) / np.sqrt(var + eps)
    norm = norm.reshape(N, C, H, W)
    out = norm * gamma.to_host().reshape(1, C, 1, 1) + beta.to_host().reshape(1, C, 1, 1)
    return Tensor.from_host(x.queue, out.astype(np.float32)), Tensor.from_host(x.queue, mean.reshape(groups).astype(np.float32)), Tensor.from_host(x.queue, var.reshape(groups).astype(np.float32))


def group_norm_backward(x: Tensor, gamma: Tensor, grad_out: Tensor, mean: Tensor, var: Tensor, groups: int, eps: float = 1e-5):
    N, C, H, W = x.shape
    xh = x.to_host().reshape(N, groups, C // groups, H, W)
    go = grad_out.to_host().reshape(N, groups, C // groups, H, W)
    mean_h = mean.to_host().reshape(groups, 1, 1, 1)
    var_h = var.to_host().reshape(groups, 1, 1, 1)
    inv = 1.0 / np.sqrt(var_h + eps)
    xn = (xh - mean_h) * inv
    grad_gamma = (go * xn).sum(axis=(0, 3, 4)).reshape(-1)
    grad_beta = go.sum(axis=(0, 3, 4)).reshape(-1)
    # grad_x (simplified per group)
    g = C // groups
    d_y = go * gamma.to_host().reshape(1, groups, g, 1, 1)
    dvar = (-0.5) * np.sum(d_y * (xh - mean_h) * inv**3, axis=(2, 3, 4), keepdims=True)
    dmean = -np.sum(d_y * inv, axis=(2, 3, 4), keepdims=True) - 2.0 * dvar * np.mean(xh - mean_h, axis=(2, 3, 4), keepdims=True)
    grad_x = d_y * inv + dvar * 2 * (xh - mean_h) / (g * H * W) + dmean / (g * H * W)
    grad_x = grad_x.reshape(N, C, H, W)
    q = x.queue
    from netcl.core.tensor import Tensor as T

    return T.from_host(q, grad_x.astype(np.float32)), T.from_host(q, grad_gamma.astype(np.float32)), T.from_host(q, grad_beta.astype(np.float32))

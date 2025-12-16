"""
GPU-side data augmentation helpers (NCHW).
Randomness is supplied from host (masks/factors) to keep kernels simple/deterministic for testing.
"""

from __future__ import annotations

from typing import Optional, Tuple

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

from netcl.core.tensor import Tensor


def flip_horizontal(x: Tensor, mask: np.ndarray, out: Optional[Tensor] = None) -> Tensor:
    """
    Flip images horizontally where mask[n] == 1. mask shape: (N,), dtype uint8/bool.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for gpu augmentation")
    if mask.shape[0] != x.shape[0]:
        raise ValueError("mask length must equal batch size")
    N, C, H, W = x.shape
    ctx = x.context
    q = x.queue
    mask_dev = Tensor.from_host(q, mask.astype(np.uint8), dtype="float32")  # store as float for simplicity
    ksrc = f"""
    __kernel void flip_h(__global const float* x, __global const float* mask, __global float* out,
                         const int N, const int C, const int H, const int W) {{
        int idx = get_global_id(0);
        int total = N*C*H*W;
        if (idx >= total) return;
        int w = idx % W;
        int h = (idx / W) % H;
        int c = (idx / (H*W)) % C;
        int n = idx / (C*H*W);
        float m = mask[n];
        int w_src = (m > 0.5f) ? (W - 1 - w) : w;
        int src_idx = ((n*C + c)*H + h)*W + w_src;
        out[idx] = x[src_idx];
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    if out is None:
        out = Tensor.from_shape(q, x.shape, dtype=x.dtype)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    prg.flip_h(q, gsize, (256,), x.buffer, mask_dev.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return out


def apply_color_jitter(x: Tensor, brightness: np.ndarray, contrast: np.ndarray, out: Optional[Tensor] = None) -> Tensor:
    """
    Apply per-sample brightness (add) and contrast (mul) factors.
    brightness/contrast shape: (N,), dtype float32.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for gpu augmentation")
    N, C, H, W = x.shape
    if brightness.shape[0] != N or contrast.shape[0] != N:
        raise ValueError("brightness/contrast must match batch size")
    q = x.queue
    b_dev = Tensor.from_host(q, brightness.astype(np.float32), dtype="float32")
    c_dev = Tensor.from_host(q, contrast.astype(np.float32), dtype="float32")
    ctx = x.context
    ksrc = f"""
    __kernel void color_jit(__global const float* x, __global const float* b, __global const float* c, __global float* out,
                            const int N, const int C, const int H, const int W) {{
        int idx = get_global_id(0);
        int total = N*C*H*W;
        if (idx >= total) return;
        int n = idx / (C*H*W);
        float v = x[idx];
        float scale = c[n];
        float shift = b[n];
        out[idx] = v * scale + shift;
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    if out is None:
        out = Tensor.from_shape(q, x.shape, dtype=x.dtype)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    prg.color_jit(q, gsize, (256,), x.buffer, b_dev.buffer, c_dev.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return out


def cutout(x: Tensor, centers: np.ndarray, size: int, out: Optional[Tensor] = None) -> Tensor:
    """
    Zero out a square patch per sample.
    centers shape: (N, 2) (h, w). size: side length.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for gpu augmentation")
    N, C, H, W = x.shape
    if centers.shape[0] != N or centers.shape[1] != 2:
        raise ValueError("centers must be (N,2)")
    q = x.queue
    centers_dev = Tensor.from_host(q, centers.astype(np.int32), dtype="float32")
    ctx = x.context
    ksrc = f"""
    __kernel void cutout_kernel(__global const float* x, __global const float* centers, __global float* out,
                                const int N, const int C, const int H, const int W, const int size) {{
        int idx = get_global_id(0);
        int total = N*C*H*W;
        if (idx >= total) return;
        int w = idx % W;
        int h = (idx / W) % H;
        int c = (idx / (H*W)) % C;
        int n = idx / (C*H*W);
        int ch = (int)centers[2*n + 0];
        int cw = (int)centers[2*n + 1];
        int hmin = ch - size / 2;
        int hmax = ch + size / 2;
        int wmin = cw - size / 2;
        int wmax = cw + size / 2;
        int inside = (h >= hmin && h <= hmax && w >= wmin && w <= wmax) ? 1 : 0;
        out[idx] = inside ? 0.0f : x[idx];
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    if out is None:
        out = Tensor.from_shape(q, x.shape, dtype=x.dtype)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    prg.cutout_kernel(q, gsize, (256,), x.buffer, centers_dev.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(size))
    return out

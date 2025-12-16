from __future__ import annotations

from typing import List

from netcl.core.tensor import Tensor
import numpy as np
import pyopencl as cl

_DTYPE_CNAME = {"float32": "float", "float": "float"}


def max_pool2d(x: Tensor, kernel_size: int = 2, stride: int = 2) -> Tensor:
    """
    Simple NCHW max-pool (no padding). Assumes stride == kernel_size for non-overlap.
    """
    N, C, H, W = x.shape
    out_h = (H - kernel_size) // stride + 1
    out_w = (W - kernel_size) // stride + 1
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype} for max_pool2d")
    ksrc = f"""
    __kernel void max_pool2d(__global const {dtype_c}* x, __global {dtype_c}* out,
                             const int N, const int C, const int H, const int W,
                             const int KH, const int KW, const int stride, const int OH, const int OW) {{
        int gid = get_global_id(0);
        int total = N * C * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int c = (gid / (OH * OW)) % C;
        int n = gid / (C * OH * OW);
        int hstart = oh * stride;
        int wstart = ow * stride;
        {dtype_c} m = x[((n*C + c)*H + hstart)*W + wstart];
        for (int kh = 0; kh < KH; ++kh) {{
            for (int kw = 0; kw < KW; ++kw) {{
                int ih = hstart + kh;
                int iw = wstart + kw;
                int idx = ((n*C + c)*H + ih)*W + iw;
                {dtype_c} v = x[idx];
                if (v > m) m = v;
            }}
        }}
        out[gid] = m;
    }}
    """
    program = cl.Program(ctx, ksrc).build()
    kernel = program.max_pool2d
    out = Tensor.from_shape(x.queue, (N, C, out_h, out_w), dtype=x.dtype)
    total = N * C * out_h * out_w
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(kernel_size), np.int32(kernel_size), np.int32(stride), np.int32(out_h), np.int32(out_w))
    return out


def max_pool2d_backward(x: Tensor, grad_out: Tensor, kernel_size: int = 2, stride: int = 2) -> Tensor:
    """
    Backward for max-pool. Assumes stride == kernel_size (non-overlapping windows).
    """
    N, C, H, W = x.shape
    _, _, OH, OW = grad_out.shape
    if stride != kernel_size:
        raise ValueError("max_pool2d_backward assumes stride == kernel_size (non-overlap)")
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    ksrc = f"""
    __kernel void max_pool2d_bwd(__global const {dtype_c}* x, __global const {dtype_c}* grad_out, __global {dtype_c}* grad_in,
                                 const int N, const int C, const int H, const int W,
                                 const int KH, const int KW, const int OH, const int OW, const int stride) {{
        int gid = get_global_id(0);
        int total = N * C * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int c = (gid / (OH * OW)) % C;
        int n = gid / (C * OH * OW);
        int hstart = oh * stride;
        int wstart = ow * stride;
        {dtype_c} maxv = x[((n*C + c)*H + hstart)*W + wstart];
        int max_h = hstart;
        int max_w = wstart;
        for (int kh = 0; kh < KH; ++kh) {{
            for (int kw = 0; kw < KW; ++kw) {{
                int ih = hstart + kh;
                int iw = wstart + kw;
                int idx = ((n*C + c)*H + ih)*W + iw;
                {dtype_c} v = x[idx];
                if (v > maxv) {{
                    maxv = v;
                    max_h = ih;
                    max_w = iw;
                }}
            }}
        }}
        int out_idx = ((n*C + c)*OH + oh)*OW + ow;
        int in_idx = ((n*C + c)*H + max_h)*W + max_w;
        grad_in[in_idx] = grad_out[out_idx];
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.max_pool2d_bwd
    grad_in = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    cl.enqueue_fill_buffer(x.queue, grad_in.buffer, np.float32(0), 0, grad_in.buffer.size)  # type: ignore
    total = N * C * OH * OW
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(
        x.queue,
        gsize,
        (256,),
        x.buffer,
        grad_out.buffer,
        grad_in.buffer,
        np.int32(N),
        np.int32(C),
        np.int32(H),
        np.int32(W),
        np.int32(kernel_size),
        np.int32(kernel_size),
        np.int32(OH),
        np.int32(OW),
        np.int32(stride),
    )
    return grad_in


def avg_pool2d(x: Tensor, kernel_size: int = 2, stride: int = 2) -> Tensor:
    """
    Average pool NCHW. No padding. Assumes stride >= 1.
    """
    N, C, H, W = x.shape
    out_h = (H - kernel_size) // stride + 1
    out_w = (W - kernel_size) // stride + 1
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype} for avg_pool2d")
    ksrc = f"""
    __kernel void avg_pool2d(__global const {dtype_c}* x, __global {dtype_c}* out,
                             const int N, const int C, const int H, const int W,
                             const int KH, const int KW, const int stride, const int OH, const int OW) {{
        int gid = get_global_id(0);
        int total = N * C * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int c = (gid / (OH * OW)) % C;
        int n = gid / (C * OH * OW);
        int hstart = oh * stride;
        int wstart = ow * stride;
        float acc = 0.0f;
        for (int kh = 0; kh < KH; ++kh) {{
            for (int kw = 0; kw < KW; ++kw) {{
                int ih = hstart + kh;
                int iw = wstart + kw;
                int idx = ((n*C + c)*H + ih)*W + iw;
                acc += x[idx];
            }}
        }}
        out[gid] = acc / (KH * KW);
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.avg_pool2d
    out = Tensor.from_shape(x.queue, (N, C, out_h, out_w), dtype=x.dtype)
    total = N * C * out_h * out_w
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(kernel_size), np.int32(kernel_size), np.int32(stride), np.int32(out_h), np.int32(out_w))
    return out


def avg_pool2d_backward(x: Tensor, grad_out: Tensor, kernel_size: int = 2, stride: int = 2) -> Tensor:
    """
    Backward for average pool. Distributes grad_out equally to contributing inputs.
    """
    N, C, H, W = x.shape
    _, _, OH, OW = grad_out.shape
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    ksrc = f"""
    __kernel void avg_pool2d_bwd(__global const {dtype_c}* grad_out, __global {dtype_c}* grad_in,
                                 const int N, const int C, const int H, const int W,
                                 const int KH, const int KW, const int OH, const int OW, const int stride) {{
        int gid = get_global_id(0);
        int total = N * C * H * W;
        if (gid >= total) return;
        int wcoord = gid % W;
        int hcoord = (gid / W) % H;
        int c = (gid / (H * W)) % C;
        int n = gid / (C * H * W);
        float acc = 0.0f;
        for (int oh = 0; oh < OH; ++oh) {{
            int hstart = oh * stride;
            if (hcoord < hstart || hcoord >= hstart + KH) continue;
            for (int ow = 0; ow < OW; ++ow) {{
                int wstart = ow * stride;
                if (wcoord < wstart || wcoord >= wstart + KW) continue;
                int out_idx = ((n*C + c)*OH + oh)*OW + ow;
                acc += grad_out[out_idx] / (KH * KW);
            }}
        }}
        grad_in[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.avg_pool2d_bwd
    grad_in = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    cl.enqueue_fill_buffer(x.queue, grad_in.buffer, np.float32(0), 0, grad_in.buffer.size)  # type: ignore
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(
        x.queue,
        gsize,
        (256,),
        grad_out.buffer,
        grad_in.buffer,
        np.int32(N),
        np.int32(C),
        np.int32(H),
        np.int32(W),
        np.int32(kernel_size),
        np.int32(kernel_size),
        np.int32(grad_out.shape[2]),
        np.int32(grad_out.shape[3]),
        np.int32(stride),
    )
    return grad_in


def global_avg_pool2d(x: Tensor) -> Tensor:
    """
    Global average over H,W -> output N x C x 1 x 1
    """
    N, C, H, W = x.shape
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    ksrc = f"""
    __kernel void gap2d(__global const {dtype_c}* x, __global {dtype_c}* out,
                        const int N, const int C, const int H, const int W) {{
        int gid = get_global_id(0);
        int c = gid % C;
        int n = gid / C;
        if (n >= N) return;
        float acc = 0.0f;
        for (int h = 0; h < H; ++h) {{
            for (int w = 0; w < W; ++w) {{
                int idx = ((n*C + c)*H + h)*W + w;
                acc += x[idx];
            }}
        }}
        out[gid] = acc / (H * W);
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.gap2d
    out = Tensor.from_shape(x.queue, (N, C, 1, 1), dtype=x.dtype)
    total = N * C
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return out

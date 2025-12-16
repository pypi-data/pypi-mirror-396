from __future__ import annotations

import os
from typing import Optional, Tuple

from netcl.core.tensor import Tensor
from netcl.core.memory import BufferPool

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl
except ImportError:  # pragma: no cover
    cl = None

_DTYPE_CNAME = {"float": "float", "float32": "float"}
_ENV_DW_ALGO = os.environ.get("NETCL_DWCONV_ALGO", "").lower()


def _resolve_algo(algo: Optional[str]) -> str:
    if algo:
        algo = algo.lower()
    if not algo or algo == "":
        algo = _ENV_DW_ALGO or "naive"
    if algo == "auto":
        algo = "naive"
    if algo in ("naive", "tile"):
        return algo
    raise ValueError(f"unsupported depthwise conv algo {algo}")


def _build_dw_forward_tiled(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void dw_conv2d_tiled(__global const {dtype_c}* x, __global const {dtype_c}* w, __global const {dtype_c}* b, __global {dtype_c}* out,
                                  const int N, const int C, const int H, const int W,
                                  const int KH, const int KW, const int OH, const int OW, const int stride, const int pad) {{
        int ow = get_global_id(0);
        int oh = get_global_id(1);
        int nc = get_global_id(2);
        if (ow >= OW || oh >= OH) return;
        int n = nc / C;
        int c = nc - n * C;
        if (n >= N) return;
        float acc = 0.0f;
        for (int kh = 0; kh < KH; ++kh) {{
            int ih = oh * stride + kh - pad;
            if (ih < 0 || ih >= H) continue;
            for (int kw = 0; kw < KW; ++kw) {{
                int iw = ow * stride + kw - pad;
                if (iw < 0 || iw >= W) continue;
                int x_idx = ((n*C + c)*H + ih)*W + iw;
                int w_idx = (c*KH + kh)*KW + kw;
                acc += x[x_idx] * w[w_idx];
            }}
        }}
        if (b != 0) acc += b[c];
        int out_idx = ((n*C + c)*OH + oh)*OW + ow;
        out[out_idx] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.dw_conv2d_tiled


def depthwise_conv2d(x: Tensor, w: Tensor, bias: Optional[Tensor] = None, stride: int = 1, pad: int = 0, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None, algo: Optional[str] = None) -> Tensor:
    """
    Depthwise conv NCHW. w shape: C x 1 x KH x KW
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for depthwise_conv2d")
    algo_name = _resolve_algo(algo)
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError("unsupported dtype")
    N, C, H, W = x.shape
    Cw, one, KH, KW = w.shape
    if Cw != C:
        raise ValueError("channel mismatch for depthwise conv")
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W + 2 * pad - KW) // stride + 1
    ctx = x.context
    if algo_name == "tile":
        kernel = _build_dw_forward_tiled(ctx, dtype_c)
        if out is None:
            out = Tensor.from_shape(x.queue, (N, C, OH, OW), dtype=x.dtype, pool=pool)
        gsize = (int(np.ceil(OW / 8.0)) * 8, int(np.ceil(OH / 8.0)) * 8, N * C)
        lsize = (8, 8, 1)
        kernel(
            x.queue,
            gsize,
            lsize,
            x.buffer,
            w.buffer,
            bias.buffer if bias is not None else None,
            out.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(stride),
            np.int32(pad),
        )
        return out
    else:
        ksrc = f"""
        __kernel void dw_conv2d(__global const {dtype_c}* x, __global const {dtype_c}* w, __global const {dtype_c}* b, __global {dtype_c}* out,
                                const int C, const int H, const int W, const int KH, const int KW, const int OH, const int OW, const int stride, const int pad) {{
            int gid = get_global_id(0);
            int ow_idx = gid % OW;
            int oh_idx = (gid / OW) % OH;
            int c = (gid / (OH*OW)) % C;
            int n = gid / (C*OH*OW);
            int total = C * OH * OW * 1;
            if (gid >= total) return;
            float acc = 0.0f;
            for (int kh = 0; kh < KH; ++kh) {{
                int ih = oh_idx * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int iw = ow_idx * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int w_idx = ((c)*KH + kh)*KW + kw;
                    acc += x[x_idx] * w[w_idx];
                }}
            }}
            if (b != 0) acc += b[c];
            int out_idx = ((n*C + c)*OH + oh_idx)*OW + ow_idx;
            out[out_idx] = acc;
        }}
        """
        prg = cl.Program(ctx, ksrc).build()
        kernel = prg.dw_conv2d
        if out is None:
            out = Tensor.from_shape(x.queue, (N, C, OH, OW), dtype=x.dtype, pool=pool)
        total = N * C * OH * OW
        gsize = (int(np.ceil(total / 256.0)) * 256,)
        kernel(x.queue, gsize, (256,), x.buffer, w.buffer, bias.buffer if bias is not None else None, out.buffer, np.int32(C), np.int32(H), np.int32(W), np.int32(KH), np.int32(KW), np.int32(OH), np.int32(OW), np.int32(stride), np.int32(pad))
        return out


def depthwise_conv2d_backward(x: Tensor, w: Tensor, grad_out: Tensor, bias: Optional[Tensor] = None, stride: int = 1, pad: int = 0, pool: Optional[BufferPool] = None) -> Tuple[Tensor, Tensor, Optional[Tensor]]:
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for depthwise_conv2d backward")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError("unsupported dtype")
    N, C, H, W = x.shape
    _, _, KH, KW = w.shape
    _, _, OH, OW = grad_out.shape
    ctx = x.context
    q = x.queue
    # grad_input
    ksrc_in = f"""
    __kernel void dw_conv2d_grad_input(__global const {dtype_c}* grad_out, __global const {dtype_c}* w, __global {dtype_c}* grad_in,
                                       const int C, const int H, const int W, const int KH, const int KW, const int OH, const int OW, const int stride, const int pad) {{
        int gid = get_global_id(0);
        int wcoord = gid % W;
        int hcoord = (gid / W) % H;
        int c = (gid / (H*W)) % C;
        int n = gid / (C*H*W);
        float acc = 0.0f;
        for (int kh = 0; kh < KH; ++kh) {{
            int oh_num = hcoord + pad - kh;
            if (oh_num < 0) continue;
            if (oh_num % stride != 0) continue;
            int oh = oh_num / stride;
            if (oh < 0 || oh >= OH) continue;
            for (int kw = 0; kw < KW; ++kw) {{
                int ow_num = wcoord + pad - kw;
                if (ow_num < 0) continue;
                if (ow_num % stride != 0) continue;
                int ow = ow_num / stride;
                if (ow < 0 || ow >= OW) continue;
                int go_idx = ((n*C + c)*OH + oh)*OW + ow;
                int w_idx = ((c)*KH + kh)*KW + kw;
                acc += grad_out[go_idx] * w[w_idx];
            }}
        }}
        int idx = ((n*C + c)*H + hcoord)*W + wcoord;
        grad_in[idx] = acc;
    }}
    """
    prg_in = cl.Program(ctx, ksrc_in).build()
    kernel_in = prg_in.dw_conv2d_grad_input
    grad_in = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
    total_in = N * C * H * W
    gsize_in = (int(np.ceil(total_in / 256.0)) * 256,)
    kernel_in(q, gsize_in, (256,), grad_out.buffer, w.buffer, grad_in.buffer, np.int32(C), np.int32(H), np.int32(W), np.int32(KH), np.int32(KW), np.int32(OH), np.int32(OW), np.int32(stride), np.int32(pad))
    # grad_weight
    ksrc_w = f"""
    __kernel void dw_conv2d_grad_weight(__global const {dtype_c}* x, __global const {dtype_c}* grad_out, __global {dtype_c}* grad_w,
                                        const int C, const int H, const int W, const int KH, const int KW, const int OH, const int OW, const int stride, const int pad) {{
        int gid = get_global_id(0);
        int kw = gid % KW;
        int kh = (gid / KW) % KH;
        int c = gid / (KH*KW);
        float acc = 0.0f;
        for (int n = 0; n < {N}; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int ow = 0; ow < OW; ++ow) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int go_idx = ((n*C + c)*OH + oh)*OW + ow;
                    acc += x[x_idx] * grad_out[go_idx];
                }}
            }}
        }}
        grad_w[gid] = acc;
    }}
    """
    prg_w = cl.Program(ctx, ksrc_w).build()
    kernel_w = prg_w.dw_conv2d_grad_weight
    grad_w = Tensor.from_shape(q, w.shape, dtype=w.dtype, pool=pool)
    total_w = C * KH * KW
    gsize_w = (int(np.ceil(total_w / 256.0)) * 256,)
    kernel_w(q, gsize_w, (256,), x.buffer, grad_out.buffer, grad_w.buffer, np.int32(C), np.int32(H), np.int32(W), np.int32(KH), np.int32(KW), np.int32(OH), np.int32(OW), np.int32(stride), np.int32(pad))
    grad_b_out = None
    if bias is not None:
        grad_b_out = Tensor.from_shape(q, bias.shape, dtype=bias.dtype, pool=pool)
        # reduce grad_out over N,H,W per channel on host for simplicity
        go = grad_out.to_host()
        gb = go.sum(axis=(0, 2, 3))
        cl.enqueue_copy(q, grad_b_out.buffer, gb.astype(np.float32)).wait()
    return grad_in, grad_w, grad_b_out

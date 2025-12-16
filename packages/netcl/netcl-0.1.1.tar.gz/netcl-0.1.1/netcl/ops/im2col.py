from __future__ import annotations

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


def im2col(x: Tensor, KH: int, KW: int, stride: int = 1, pad: int = 0, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tuple[Tensor, Tuple[int, int, int, int]]:
    """
    im2col for NCHW. Returns (col, (N, C, OH, OW)) where col shape = (N, OH, OW, C*KH*KW).
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for im2col")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    N, C, H, W = x.shape
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W + 2 * pad - KW) // stride + 1
    ctx = x.context
    q = x.queue
    ksrc = f"""
    __kernel void im2col(__global const {dtype_c}* x, __global {dtype_c}* out,
                         const int N, const int C, const int H, const int W,
                         const int KH, const int KW, const int OH, const int OW, const int stride, const int pad) {{
        int gid = get_global_id(0);
        int total = N * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int n = gid / (OH * OW);
        int out_base = gid * C * KH * KW;
        for (int c = 0; c < C; ++c) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int ih = oh * stride + kh - pad;
                for (int kw = 0; kw < KW; ++kw) {{
                    int iw = ow * stride + kw - pad;
                    int out_idx = out_base + ((c*KH + kh)*KW + kw);
                    if (ih >=0 && ih < H && iw >=0 && iw < W) {{
                        int x_idx = ((n*C + c)*H + ih)*W + iw;
                        out[out_idx] = x[x_idx];
                    }} else {{
                        out[out_idx] = 0;
                    }}
                }}
            }}
        }}
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.im2col
    out_shape = (N, OH, OW, C * KH * KW)
    if out is None:
        out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
    total = N * OH * OW
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(q, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(KH), np.int32(KW), np.int32(OH), np.int32(OW), np.int32(stride), np.int32(pad))
    return out, (N, C, OH, OW)


def col2im(col: Tensor, x_shape: Tuple[int, int, int, int], KH: int, KW: int, stride: int = 1, pad: int = 0, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    """
    Inverse of im2col for NCHW. col shape (N, OH, OW, C*KH*KW)
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for col2im")
    dtype_c = _DTYPE_CNAME.get(col.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {col.dtype}")
    N, C, H, W = x_shape
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W + 2 * pad - KW) // stride + 1
    ctx = col.context
    q = col.queue
    ksrc = f"""
    __kernel void col2im(__global const {dtype_c}* col, __global {dtype_c}* x,
                         const int N, const int C, const int H, const int W,
                         const int KH, const int KW, const int OH, const int OW, const int stride, const int pad) {{
        int gid = get_global_id(0);
        int total = N * C * H * W;
        if (gid >= total) return;
        int w = gid % W;
        int h = (gid / W) % H;
        int c = (gid / (H*W)) % C;
        int n = gid / (C*H*W);
        float acc = 0.0f;
        for (int oh = 0; oh < OH; ++oh) {{
            int hstart = oh * stride - pad;
            if (h < hstart || h >= hstart + KH) continue;
            for (int ow = 0; ow < OW; ++ow) {{
                int wstart = ow * stride - pad;
                if (w < wstart || w >= wstart + KW) continue;
                int kh = h - hstart;
                int kw = w - wstart;
                int col_idx = ((n*OH + oh)*OW + ow)*(C*KH*KW) + (c*KH + kh)*KW + kw;
                acc += col[col_idx];
            }}
        }}
        x[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.col2im
    if out is None:
        out = Tensor.from_shape(q, x_shape, dtype=col.dtype, pool=pool)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(q, gsize, (256,), col.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(KH), np.int32(KW), np.int32(OH), np.int32(OW), np.int32(stride), np.int32(pad))
    return out

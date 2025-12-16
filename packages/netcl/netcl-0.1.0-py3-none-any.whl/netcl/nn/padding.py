from __future__ import annotations

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor

_DTYPE_CNAME = {"float": "float", "float32": "float"}


def pad2d(x: Tensor, pad: int = 1, mode: str = "zero") -> Tensor:
    """
    Simple 2D padding (NCHW). mode: 'zero' or 'reflect' (basic).
    """
    if pad <= 0:
        return x
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    ctx = x.context
    N, C, H, W = x.shape
    out_h = H + 2 * pad
    out_w = W + 2 * pad
    ksrc = f"""
    __kernel void pad2d(__global const {dtype_c}* x, __global {dtype_c}* out,
                        const int N, const int C, const int H, const int W,
                        const int pad, const int OH, const int OW) {{
        int gid = get_global_id(0);
        int total = N * C * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int c = (gid / (OH * OW)) % C;
        int n = gid / (C * OH * OW);
        int ih = oh - pad;
        int iw = ow - pad;
        {dtype_c} val = 0;
        if (ih >=0 && ih < H && iw >=0 && iw < W) {{
            int idx = ((n*C + c)*H + ih)*W + iw;
            val = x[idx];
        }} else if ({1 if mode=='reflect' else 0}) {{
            // basic reflect: clamp to border
            int rih = ih < 0 ? -ih - 1 : (ih >= H ? 2*H - ih - 1 : ih);
            int riw = iw < 0 ? -iw - 1 : (iw >= W ? 2*W - iw - 1 : iw);
            int idx = ((n*C + c)*H + rih)*W + riw;
            val = x[idx];
        }}
        out[gid] = val;
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.pad2d
    out = Tensor.from_shape(x.queue, (N, C, out_h, out_w), dtype=x.dtype)
    total = N * C * out_h * out_w
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(pad), np.int32(out_h), np.int32(out_w))
    return out

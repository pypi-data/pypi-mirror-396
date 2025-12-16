from __future__ import annotations

from typing import Optional

from netcl.core.tensor import Tensor
from netcl.core.memory import BufferPool
from netcl.ops.conv2d import _build_grad_bias_kernel, _build_grad_input_kernel, _DTYPE_CNAME
import numpy as np

try:
    import pyopencl as cl
except ImportError:  # pragma: no cover
    cl = None


def conv_transpose2d(x: Tensor, w: Tensor, bias: Optional[Tensor] = None, stride: int = 1, pad: int = 0, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    """
    ConvTranspose2d via conv grad_input kernel. x: N,F,OH,OW; w: F,C,KH,KW -> out: N,C,H,W
    """
    if cl is None:
        raise ImportError("pyopencl required for conv_transpose2d")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError("unsupported dtype")
    N, F, OH, OW = x.shape
    Fw, C, KH, KW = w.shape
    if F != Fw:
        raise ValueError("channel mismatch")
    H = (OH - 1) * stride - 2 * pad + KH
    W = (OW - 1) * stride - 2 * pad + KW
    ctx = x.context
    q = x.queue
    grad_in = Tensor.from_shape(q, (N, C, H, W), dtype=x.dtype, pool=pool) if out is None else out
    kernel_in = _build_grad_input_kernel(ctx, dtype_c)
    total_in = N * C * H * W
    gsize_in = (int(np.ceil(total_in / 256.0)) * 256,)
    kernel_in(
        q,
        gsize_in,
        (256,),
        x.buffer,
        w.buffer,
        grad_in.buffer,
        np.int32(N),
        np.int32(C),
        np.int32(H),
        np.int32(W),
        np.int32(KH),
        np.int32(KW),
        np.int32(OH),
        np.int32(OW),
        np.int32(F),
        np.int32(stride),
        np.int32(pad),
    )
    if bias is not None:
        kernel_b = _build_grad_bias_kernel(ctx, dtype_c)
        gsize_b = (int(np.ceil(C / 256.0)) * 256,)
        tmp = Tensor.from_shape(q, (C,), dtype=x.dtype, pool=pool)
        kernel_b(q, gsize_b, (256,), grad_in.buffer, tmp.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
        # add bias
        bh = bias.to_host()
        out_host = grad_in.to_host()
        out_host += bh.reshape(1, C, 1, 1)
        cl.enqueue_copy(q, grad_in.buffer, out_host.astype(np.float32)).wait()
    return grad_in


def conv_transpose2d_backward(x: Tensor, w: Tensor, grad_out: Tensor, bias: Optional[Tensor] = None, stride: int = 1, pad: int = 0, pool: Optional[BufferPool] = None):
    """
    Backward for conv_transpose2d: returns (grad_x, grad_w, grad_b)
    """
    if cl is None:
        raise ImportError("pyopencl required for conv_transpose2d backward")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError("unsupported dtype")
    N, F, OH, OW = x.shape
    _, C, KH, KW = w.shape
    H = (OH - 1) * stride - 2 * pad + KH
    W = (OW - 1) * stride - 2 * pad + KW
    ctx = x.context
    q = x.queue

    ksrc_dx = f"""
    __kernel void convt_grad_input(__global const {dtype_c}* grad_out, __global const {dtype_c}* w, __global {dtype_c}* grad_x,
                                   const int N, const int F, const int C,
                                   const int OH, const int OW, const int H, const int W,
                                   const int KH, const int KW, const int stride, const int pad) {{
        int ow = get_global_id(0);
        int oh = get_global_id(1);
        int nf = get_global_id(2);
        if (ow >= OW || oh >= OH) return;
        int n = nf / F;
        int f = nf - n * F;
        if (n >= N) return;
        float acc = 0.0f;
        for (int c = 0; c < C; ++c) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int h = oh * stride - pad + kh;
                if (h < 0 || h >= H) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int wcol = ow * stride - pad + kw;
                    if (wcol < 0 || wcol >= W) continue;
                    int go_idx = ((n*C + c)*H + h)*W + wcol;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += grad_out[go_idx] * w[w_idx];
                }}
            }}
        }}
        int out_idx = ((n*F + f)*OH + oh)*OW + ow;
        grad_x[out_idx] = acc;
    }}
    """
    prg_dx = cl.Program(ctx, ksrc_dx).build()
    k_dx = prg_dx.convt_grad_input
    grad_x = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
    gsize_dx = (int(np.ceil(OW / 8.0)) * 8, int(np.ceil(OH / 8.0)) * 8, N * F)
    lsize_dx = (8, 8, 1)
    k_dx(
        q,
        gsize_dx,
        lsize_dx,
        grad_out.buffer,
        w.buffer,
        grad_x.buffer,
        np.int32(N),
        np.int32(F),
        np.int32(C),
        np.int32(OH),
        np.int32(OW),
        np.int32(H),
        np.int32(W),
        np.int32(KH),
        np.int32(KW),
        np.int32(stride),
        np.int32(pad),
    )

    ksrc_dw = f"""
    __kernel void convt_grad_weight(__global const {dtype_c}* x, __global const {dtype_c}* grad_out, __global {dtype_c}* grad_w,
                                    const int N, const int F, const int C,
                                    const int OH, const int OW, const int H, const int W,
                                    const int KH, const int KW, const int stride, const int pad) {{
        int kw = get_global_id(0);
        int kh = get_global_id(1);
        int fc = get_global_id(2);
        if (kw >= KW || kh >= KH) return;
        int f = fc / C;
        int c = fc - f * C;
        if (f >= F || c >= C) return;
        float acc = 0.0f;
        for (int n = 0; n < N; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                int h = oh * stride - pad + kh;
                if (h < 0 || h >= H) continue;
                for (int ow = 0; ow < OW; ++ow) {{
                    int wcol = ow * stride - pad + kw;
                    if (wcol < 0 || wcol >= W) continue;
                    int x_idx = ((n*F + f)*OH + oh)*OW + ow;
                    int go_idx = ((n*C + c)*H + h)*W + wcol;
                    acc += x[x_idx] * grad_out[go_idx];
                }}
            }}
        }}
        int w_idx = ((f*C + c)*KH + kh)*KW + kw;
        grad_w[w_idx] = acc;
    }}
    """
    prg_dw = cl.Program(ctx, ksrc_dw).build()
    k_dw = prg_dw.convt_grad_weight
    grad_w = Tensor.from_shape(q, w.shape, dtype=w.dtype, pool=pool)
    gsize_dw = (int(np.ceil(KW / 4.0)) * 4, int(np.ceil(KH / 4.0)) * 4, F * C)
    lsize_dw = (4, 4, 1)
    k_dw(
        q,
        gsize_dw,
        lsize_dw,
        x.buffer,
        grad_out.buffer,
        grad_w.buffer,
        np.int32(N),
        np.int32(F),
        np.int32(C),
        np.int32(OH),
        np.int32(OW),
        np.int32(H),
        np.int32(W),
        np.int32(KH),
        np.int32(KW),
        np.int32(stride),
        np.int32(pad),
    )
    gb = None
    if bias is not None:
        gb = Tensor.from_shape(q, bias.shape, dtype=bias.dtype, pool=pool)
        k_b = _build_grad_bias_kernel(ctx, dtype_c)
        gsize_b = (int(np.ceil(C / 256.0)) * 256,)
        k_b(q, gsize_b, (256,), grad_out.buffer, gb.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return grad_x, grad_w, gb

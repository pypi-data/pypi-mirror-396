"""
Softmax along the last dimension (axis=1 for 2D) using simple kernels.
"""

from __future__ import annotations

from typing import Optional

from netcl.core.tensor import Tensor
from netcl.core.memory import BufferPool

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

_DTYPE_CNAME = {"float": "float", "float32": "float", "half": "half", "float16": "half"}


def softmax(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for softmax")
    if x.dtype not in _DTYPE_CNAME:
        raise ValueError("softmax supports float32/float16")
    if len(x.shape) != 2:
        raise ValueError("softmax currently supports 2D tensors along axis=1")
    # fp16: use safe path -> compute in fp32 then cast back
    if x.dtype in ("half", "float16"):
        from netcl.ops.softmax_fp16 import softmax_fp16_safe

        return softmax_fp16_safe(x)
    dtype_c = _DTYPE_CNAME[x.dtype]
    ctx = x.context
    q = x.queue
    M, N = x.shape

    # Buffers
    max_buf = Tensor.from_shape(q, (M,), dtype=x.dtype, pool=pool)
    sum_buf = Tensor.from_shape(q, (M,), dtype=x.dtype, pool=pool)
    if out is None:
        out = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)

    # Kernel to compute row-wise max
    k_max_src = f"""
    __kernel void row_max(__global const {dtype_c}* x, __global {dtype_c}* rowmax, const int M, const int N) {{
        int row = get_global_id(0);
        if (row >= M) return;
        {dtype_c} m = x[row * N];
        for (int c = 1; c < N; ++c) {{
            {dtype_c} v = x[row * N + c];
            if (v > m) m = v;
        }}
        rowmax[row] = m;
    }}
    """
    k_sum_src = f"""
    __kernel void row_sumexp(__global const {dtype_c}* x, __global const {dtype_c}* rowmax, __global {dtype_c}* rowsum, const int M, const int N) {{
        int row = get_global_id(0);
        if (row >= M) return;
        {dtype_c} m = rowmax[row];
        {dtype_c} s = 0;
        for (int c = 0; c < N; ++c) {{
            s += exp(x[row * N + c] - m);
        }}
        rowsum[row] = s;
    }}
    """
    k_soft_src = f"""
    __kernel void softmax_apply(__global const {dtype_c}* x, __global const {dtype_c}* rowmax, __global const {dtype_c}* rowsum, __global {dtype_c}* out, const int M, const int N) {{
        int gid = get_global_id(0);
        int row = gid / N;
        int col = gid % N;
        if (row >= M) return;
        {dtype_c} m = rowmax[row];
        {dtype_c} s = rowsum[row];
        out[gid] = exp(x[gid] - m) / s;
    }}
    """
    p_max = cl.Program(ctx, k_max_src).build()
    p_sum = cl.Program(ctx, k_sum_src).build()
    p_soft = cl.Program(ctx, k_soft_src).build()
    g_rows = (int(np.ceil(M / 64.0)) * 64,)
    l_rows = (64,)
    p_max.row_max(q, g_rows, l_rows, x.buffer, max_buf.buffer, np.int32(M), np.int32(N))
    p_sum.row_sumexp(q, g_rows, l_rows, x.buffer, max_buf.buffer, sum_buf.buffer, np.int32(M), np.int32(N))
    total = M * N
    g_total = (int(np.ceil(total / 256.0)) * 256,)
    p_soft.softmax_apply(
        q, g_total, (256,), x.buffer, max_buf.buffer, sum_buf.buffer, out.buffer, np.int32(M), np.int32(N)
    )
    return out

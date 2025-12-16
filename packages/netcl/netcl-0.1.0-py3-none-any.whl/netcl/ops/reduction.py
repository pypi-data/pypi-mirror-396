"""
Reduction kernels (sum) and softmax built from simple OpenCL kernels.
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

_DTYPE_CNAME = {"float": "float", "float32": "float"}


def reduce_sum(x: Tensor, axis: Optional[int] = None, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy are required for reduce_sum")
    if x.dtype not in _DTYPE_CNAME:
        raise ValueError("reduce_sum supports float32 for now")
    dtype_c = _DTYPE_CNAME[x.dtype]
    ctx = x.context
    q = x.queue

    if axis is None:
        total = int(np.prod(x.shape))
        src = f"""
        __kernel void reduce_all(__global const {dtype_c}* x, __global {dtype_c}* out, const int n) {{
            int gid = get_global_id(0);
            {dtype_c} acc = 0;
            for (int i = gid; i < n; i += get_global_size(0)) {{
                acc += x[i];
            }}
            // single group reduction: assume one work-group
            __local {dtype_c} shared[256];
            int lid = get_local_id(0);
            shared[lid] = acc;
            barrier(CLK_LOCAL_MEM_FENCE);
            for (int stride = get_local_size(0) / 2; stride > 0; stride >>= 1) {{
                if (lid < stride) shared[lid] += shared[lid + stride];
                barrier(CLK_LOCAL_MEM_FENCE);
            }}
            if (lid == 0) out[0] = shared[0];
        }}
        """
        program = cl.Program(ctx, src).build()
        kernel = program.reduce_all
        if out is None:
            out = Tensor.from_shape(q, (1,), dtype=x.dtype, pool=pool)
        lsize = (256,)
        gsize = (256,)
        kernel(q, gsize, lsize, x.buffer, out.buffer, np.int32(total))
        return out

    # Axis reduction for 2D tensors along axis 0 or 1
    if len(x.shape) != 2:
        raise ValueError("reduce_sum axis-specific currently supports 2D tensors")
    M, N = x.shape
    if axis == 0:
        out_shape = (N,)
        src = f"""
        __kernel void reduce_axis0(__global const {dtype_c}* x, __global {dtype_c}* out, const int M, const int N) {{
            int col = get_global_id(0);
            if (col >= N) return;
            {dtype_c} acc = 0;
            for (int r = 0; r < M; ++r) acc += x[r * N + col];
            out[col] = acc;
        }}
        """
        gsize = (int(np.ceil(N / 256.0)) * 256,)
        lsize = (256,)
    elif axis == 1:
        out_shape = (M,)
        src = f"""
        __kernel void reduce_axis1(__global const {dtype_c}* x, __global {dtype_c}* out, const int M, const int N) {{
            int row = get_global_id(0);
            if (row >= M) return;
            {dtype_c} acc = 0;
            for (int c = 0; c < N; ++c) acc += x[row * N + c];
            out[row] = acc;
        }}
        """
        gsize = (int(np.ceil(M / 256.0)) * 256,)
        lsize = (256,)
    else:
        raise ValueError("axis must be None, 0, or 1")

    program = cl.Program(ctx, src).build()
    kernel = program.reduce_axis0 if axis == 0 else program.reduce_axis1
    if out is None:
        out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
    kernel(q, gsize, lsize, x.buffer, out.buffer, np.int32(M), np.int32(N))
    return out

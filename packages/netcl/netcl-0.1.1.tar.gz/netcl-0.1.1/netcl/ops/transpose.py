from __future__ import annotations

from typing import Optional

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


def transpose2d(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    """
    Tiled 2D transpose on device. x shape [M, N] -> [N, M].
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for transpose2d")
    if len(x.shape) != 2:
        raise ValueError("transpose2d expects 2D tensor")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    M, N = x.shape
    ctx = x.context
    tile = 16
    ksrc = f"""
    __kernel void transpose2d(__global const {dtype_c}* x, __global {dtype_c}* out, const int M, const int N) {{
        __local {dtype_c} tile[{tile}][{tile}+1];
        int gx = get_global_id(0);
        int gy = get_global_id(1);
        int lx = get_local_id(0);
        int ly = get_local_id(1);
        if (gy < M && gx < N) {{
            tile[ly][lx] = x[gy * N + gx];
        }}
        barrier(CLK_LOCAL_MEM_FENCE);
        int ox = get_group_id(1) * {tile} + lx;
        int oy = get_group_id(0) * {tile} + ly;
        if (oy < N && ox < M) {{
            out[oy * M + ox] = tile[lx][ly];
        }}
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.transpose2d
    if out is None:
        out = Tensor.from_shape(x.queue, (N, M), dtype=x.dtype, pool=pool)
    gsize = (int(np.ceil(N / tile)) * tile, int(np.ceil(M / tile)) * tile)
    lsize = (tile, tile)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(M), np.int32(N))
    return out

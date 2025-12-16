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


def _prep_strides(shape: Tuple[int, ...], target_ndim: int) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """
    Returns (dims, strides) padded to target_ndim for row-major layout.
    """
    dims = (1,) * (target_ndim - len(shape)) + tuple(shape)
    # compute C-order strides
    strides = [0] * target_ndim
    stride = 1
    for i in range(target_ndim - 1, -1, -1):
        strides[i] = 0 if dims[i] == 1 else stride
        stride *= dims[i]
    return tuple(dims), tuple(strides)


def broadcast_binary(a: Tensor, b: Tensor, op: str, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    """
    Broadcasted binary op for up to 4D tensors. Supports ADD/SUB only.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for broadcast ops")
    if a.queue != b.queue:
        raise ValueError("queues must match")
    if op not in ("ADD", "SUB"):
        raise ValueError("op must be ADD or SUB")
    dtype_c = _DTYPE_CNAME.get(a.dtype)
    if dtype_c is None or b.dtype != a.dtype:
        raise ValueError("dtype mismatch or unsupported")
    ndim = max(len(a.shape), len(b.shape))
    ndim = max(ndim, 1)
    if ndim > 4:
        raise ValueError("broadcast_binary supports up to 4D")
    adims, astrides = _prep_strides(a.shape, ndim)
    bdims, bstrides = _prep_strides(b.shape, ndim)
    out_shape = []
    for da, db in zip(adims, bdims):
        if da == db:
            out_shape.append(da)
        elif da == 1:
            out_shape.append(db)
        elif db == 1:
            out_shape.append(da)
        else:
            raise ValueError("shapes not broadcastable")
    out_shape = tuple(out_shape)
    ctx = a.context
    op_expr = "va + vb" if op == "ADD" else "va - vb"
    ksrc = f"""
    __kernel void bcast_bin(__global const {dtype_c}* a, __global const {dtype_c}* b, __global {dtype_c}* out,
                            const int ndim, __constant int* adims, __constant int* bdims,
                            __constant int* astrides, __constant int* bstrides, __constant int* odims) {{
        int gid = get_global_id(0);
        int total = 1;
        for (int i=0;i<ndim;++i) total *= odims[i];
        if (gid >= total) return;
        int idx = gid;
        int a_idx = 0;
        int b_idx = 0;
        for (int i = ndim-1; i >=0; --i) {{
            int coord = idx % odims[i];
            idx = idx / odims[i];
            int ca = (adims[i] == 1) ? 0 : coord;
            int cb = (bdims[i] == 1) ? 0 : coord;
            a_idx += ca * astrides[i];
            b_idx += cb * bstrides[i];
        }}
        float va = a[a_idx];
        float vb = b[b_idx];
        out[gid] = {op_expr};
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.bcast_bin
    if out is None:
        out = Tensor.from_shape(a.queue, out_shape, dtype=a.dtype, pool=pool)
    total = int(np.prod(out_shape))
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    adims_buf = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=np.int32(adims))
    bdims_buf = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=np.int32(bdims))
    astrides_buf = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=np.int32(astrides))
    bstrides_buf = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=np.int32(bstrides))
    odims_buf = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=np.int32(out_shape))
    kernel(a.queue, gsize, (256,), a.buffer, b.buffer, out.buffer, np.int32(ndim), adims_buf, bdims_buf, astrides_buf, bstrides_buf, odims_buf)
    return out

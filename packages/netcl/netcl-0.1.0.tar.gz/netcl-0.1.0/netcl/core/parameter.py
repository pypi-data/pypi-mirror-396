from __future__ import annotations

from typing import Optional, Sequence

from netcl.core.tensor import Tensor, _np_dtype, _dtype_nbytes

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


class Parameter(Tensor):
    """
    Thin subclass of Tensor that defaults to requires_grad=True and is used for Module params.
    """

    @classmethod
    def from_host(cls, queue: "cl.CommandQueue", data, dtype: Optional[str] = None) -> "Parameter":
        if cl is None or np is None:
            raise ImportError("pyopencl and numpy required to create parameters from host")
        dtype_str = dtype or "float32"
        arr = np.array(data, dtype=_np_dtype(dtype_str), copy=False)
        ctx = queue.context
        mf = cl.mem_flags
        buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=arr)
        return cls(buffer=buf, shape=arr.shape, dtype=dtype_str, context=ctx, queue=queue, requires_grad=True)

    @classmethod
    def from_shape(
        cls, queue: "cl.CommandQueue", shape: Sequence[int], dtype: str = "float32", pool=None
    ) -> "Parameter":
        if cl is None:
            raise ImportError("pyopencl required to create parameters")
        ctx = queue.context
        n_elems = 1
        for d in shape:
            n_elems *= int(d)
        nbytes = n_elems * _dtype_nbytes(dtype)
        if pool is not None:
            handle = pool.allocate(nbytes)
            buf = handle.buffer
        else:
            mf = cl.mem_flags
            buf = cl.Buffer(ctx, mf.READ_WRITE, nbytes)
            handle = None
        return cls(
            buffer=buf,
            shape=tuple(int(d) for d in shape),
            dtype=dtype,
            context=ctx,
            queue=queue,
            pool_handle=handle,
            requires_grad=True,
        )

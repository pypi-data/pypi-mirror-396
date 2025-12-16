"""
Minimal tensor wrapper around PyOpenCL buffers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, Any

from netcl.core.memory import BufferHandle

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


def _np_dtype(dtype: str):
    if np is None:
        raise ImportError("numpy required for host-backed tensors")
    mapping = {
        "float": np.float32,
        "float32": np.float32,
        "half": np.float16,
        "float16": np.float16,
        "float64": np.float64,
        "double": np.float64,
    }
    if dtype not in mapping:
        raise ValueError(f"unsupported dtype {dtype}")
    return mapping[dtype]


def _dtype_nbytes(dtype: str) -> int:
    if dtype in ("float", "float32"):
        return 4
    if dtype in ("half", "float16"):
        return 2
    if dtype in ("double", "float64"):
        return 8
    raise ValueError(f"unsupported dtype {dtype}")


@dataclass
class Tensor:
    buffer: "cl.Buffer"
    shape: Tuple[int, ...]
    dtype: str
    context: "cl.Context"
    queue: "cl.CommandQueue"
    pool_handle: Optional[BufferHandle] = None
    persistent: bool = False
    requires_grad: bool = False
    grad: Optional["Tensor"] = None
    grad_fn: Optional[Any] = None  # typically a callable producing grads

    @property
    def size(self) -> int:
        total = 1
        for d in self.shape:
            total *= d
        return total

    @classmethod
    def from_host(cls, queue: "cl.CommandQueue", data, dtype: Optional[str] = None) -> "Tensor":
        if cl is None or np is None:
            raise ImportError("pyopencl and numpy required to create tensors from host")
        dtype_str = dtype or "float32"
        arr = np.array(data, dtype=_np_dtype(dtype_str), copy=False)
        ctx = queue.context
        mf = cl.mem_flags
        buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=arr)
        return cls(buffer=buf, shape=arr.shape, dtype=dtype_str, context=ctx, queue=queue)

    @classmethod
    def from_shape(
        cls, queue: "cl.CommandQueue", shape: Sequence[int], dtype: str = "float32", pool: Optional["BufferPool"] = None
    ) -> "Tensor":
        if cl is None:
            raise ImportError("pyopencl required to create tensors")
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
        )

    def to_host(self):
        if np is None or cl is None:
            raise ImportError("pyopencl and numpy required for host transfer")
        out = np.empty(self.shape, dtype=_np_dtype(self.dtype))
        cl.enqueue_copy(self.queue, out, self.buffer).wait()  # type: ignore
        return out


def reshape(t: Tensor, shape: Tuple[int, ...]) -> Tensor:
    """
    Return a view Tensor sharing the same buffer with a new shape.
    """
    return Tensor(
        buffer=t.buffer,
        shape=shape,
        dtype=t.dtype,
        context=t.context,
        queue=t.queue,
        pool_handle=t.pool_handle,
        persistent=t.persistent,
        requires_grad=t.requires_grad,
        grad=t.grad,
        grad_fn=t.grad_fn,
    )

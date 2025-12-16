"""
Memory helpers and a simple buffer pool skeleton.

This is a placeholder aligned with the planning document: it will evolve to
include bucketed pools, pinned host buffers, and sub-buffer management.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


@dataclass
class BufferHandle:
    buffer: "cl.Buffer"
    nbytes: int


class BufferPool:
    """
    Simple bucketed buffer pool to reduce allocation overhead.

    Buckets are power-of-two sizes; buffers are reused on release.
    """

    def __init__(self, context: Optional["cl.Context"]) -> None:
        self.context = context
        self._free: Dict[int, list[BufferHandle]] = {}

    @staticmethod
    def _bucket_size(nbytes: int) -> int:
        size = 1
        while size < nbytes:
            size <<= 1
        return size

    def allocate(self, nbytes: int, flags: Optional[int] = None) -> BufferHandle:
        if cl is None:
            raise ImportError("pyopencl required for BufferPool")
        if self.context is None:
            raise ValueError("BufferPool has no context")
        bucket = self._bucket_size(nbytes)
        free_list = self._free.get(bucket)
        if free_list:
            return free_list.pop()
        mf = cl.mem_flags
        use_flags = flags if flags is not None else (mf.READ_WRITE)
        buf = cl.Buffer(self.context, use_flags, bucket)
        return BufferHandle(buffer=buf, nbytes=bucket)

    def release(self, handle: BufferHandle) -> None:
        bucket = self._bucket_size(handle.nbytes)
        self._free.setdefault(bucket, []).append(handle)

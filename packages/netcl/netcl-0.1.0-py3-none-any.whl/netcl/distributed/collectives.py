"""
Collective communication placeholders.
"""

from __future__ import annotations

from typing import Any, List
import numpy as np
import threading

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


def all_reduce(tensors: List[Any], op: str = "sum", overlap: bool = False):
    """
    Host-based all-reduce for a list of Tensor objects across devices.
    Pulls to host, reduces, then scatters back.
    """
    if len(tensors) == 0:
        return
    op = op.lower()
    contexts = set(getattr(t, "context", None) for t in tensors)
    if len(contexts) > 1 and cl is not None:
        print("[distributed] all_reduce: mixed contexts -> host fallback (no P2P).")
    if cl is None:
        print("[distributed] all_reduce: pyopencl missing -> host fallback.")
    host_vals = [t.to_host() for t in tensors]
    if op == "sum":
        reduced = np.sum(host_vals, axis=0)
    elif op == "mean":
        reduced = np.mean(host_vals, axis=0)
    else:
        raise ValueError(f"unsupported all_reduce op {op}")
    def _scatter(t):
        # Try device copy; fall back to host assignment.
        if cl is not None and hasattr(t, "queue") and hasattr(t, "buffer"):
            try:
                cl.enqueue_copy(t.queue, t.buffer, reduced.astype(np.float32)).wait()
                return
            except Exception:
                pass
        try:
            t.buffer[...] = reduced.astype(np.float32)
        except Exception:
            pass

    if overlap and len(tensors) > 1:
        threads = [threading.Thread(target=_scatter, args=(t,)) for t in tensors]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
    else:
        for t in tensors:
            _scatter(t)
    return tensors


def broadcast(tensor: Any, root: int = 0):
    """
    Host-based broadcast: copy root tensor to others.
    """
    if not isinstance(tensor, list):
        return tensor
    src = tensor[root].to_host()
    for i, t in enumerate(tensor):
        if i == root:
            continue
        t.queue.enqueue_copy(t.buffer, src.astype(np.float32))
    return tensor


def scatter(tensor: Any, chunks: int):
    """
    Host-based scatter: split along first dim.
    """
    arr = tensor.to_host()
    splits = np.array_split(arr, chunks, axis=0)
    return splits


def gather(tensors: List[Any]):
    """
    Host-based gather: concat along first dim.
    """
    host_vals = [t.to_host() for t in tensors]
    return np.concatenate(host_vals, axis=0)


def all_reduce_p2p(tensors: List[Any], op: str = "sum"):
    """
    Device-side reduction when all tensors share the same context.
    Falls back to host all_reduce if contexts differ or pyopencl missing.
    """
    if cl is None or len(tensors) == 0:
        return all_reduce(tensors, op=op)
    ctxs = [t.context for t in tensors]
    if len(set(ctxs)) != 1:
        return all_reduce(tensors, op=op)
    ctx = ctxs[0]
    dtype_c = "float"
    ksrc = f"""
    __kernel void ar_sum(__global const {dtype_c}* in0, __global const {dtype_c}* in1, __global {dtype_c}* out, const int total) {{
        int gid = get_global_id(0);
        if (gid >= total) return;
        out[gid] = in0[gid] + in1[gid];
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    q = tensors[0].queue
    total = int(np.prod(tensors[0].shape))
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    tmp = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, size=tensors[0].buffer.size)
    # reduce pairwise; for >2 tensors, iteratively reduce into tmp
    acc = tensors[0].buffer
    for t in tensors[1:]:
        prg.ar_sum(q, gsize, (256,), acc, t.buffer, tmp, np.int32(total))
        acc = tmp
    # copy result back to all tensors
    for t in tensors:
        cl.enqueue_copy(q, t.buffer, tmp)
    return tensors

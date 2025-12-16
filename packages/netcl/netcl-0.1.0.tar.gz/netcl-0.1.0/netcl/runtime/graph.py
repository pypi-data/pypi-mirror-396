"""
Graph and executor for building a pipeline of ops with buffer reuse.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Union

from netcl.core.memory import BufferPool
from netcl.core.tensor import Tensor


OpFn = Callable[[List[Tensor], Tensor], None]


@dataclass(frozen=True)
class TensorRef:
    shape: Tuple[int, ...]
    dtype: str
    key: int = 0

    def __post_init__(self):
        # Ensure key is unique per instance by default
        object.__setattr__(self, "key", id(self))


@dataclass
class OpRecord:
    name: str
    fn: OpFn
    inputs: List[Union[Tensor, TensorRef]]
    shape: Tuple[int, ...]
    dtype: str
    output: TensorRef
    idx: int = 0


class Graph:
    def __init__(self) -> None:
        self.ops: List[OpRecord] = []
        self.outputs: Optional[TensorRef] = None

    def add_op(
        self, name: str, fn: OpFn, inputs: List[Union[Tensor, TensorRef]], shape: Tuple[int, ...], dtype: str
    ) -> TensorRef:
        ref = TensorRef(shape=shape, dtype=dtype)
        op = OpRecord(name=name, fn=fn, inputs=inputs, shape=shape, dtype=dtype, output=ref, idx=len(self.ops))
        self.ops.append(op)
        self.outputs = ref
        return ref


class GraphExecutor:
    """
    Executes a graph sequentially while reusing buffers via BufferPool.
    """

    def __init__(self, pool: BufferPool) -> None:
        self.pool = pool
        self.fusion_hook: Optional[Callable[[List[OpRecord]], List[OpRecord]]] = None
        self.async_queues: bool = False

    def _refcounts(self, graph: Graph) -> Dict[int, int]:
        counts: Dict[int, int] = {}
        for op in graph.ops:
            for t in op.inputs:
                if isinstance(t, TensorRef):
                    counts[t.key] = counts.get(t.key, 0) + 1
        return counts

    def _topological_order(self, graph: Graph) -> List[OpRecord]:
        # Build producer map for TensorRefs
        producer: Dict[int, int] = {}
        for op in graph.ops:
            producer[op.output.key] = op.idx
        indegree: Dict[int, int] = {op.idx: 0 for op in graph.ops}
        adj: Dict[int, List[int]] = {op.idx: [] for op in graph.ops}
        for op in graph.ops:
            for inp in op.inputs:
                if isinstance(inp, TensorRef) and inp.key in producer:
                    prev_idx = producer[inp.key]
                    adj[prev_idx].append(op.idx)
                    indegree[op.idx] += 1
        queue: List[int] = [op.idx for op in graph.ops if indegree[op.idx] == 0]
        order_idx: List[int] = []
        while queue:
            node = queue.pop(0)
            order_idx.append(node)
            for nxt in adj[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        if len(order_idx) != len(graph.ops):
            raise ValueError("graph has cycles or unresolved deps")
        idx_to_op = {op.idx: op for op in graph.ops}
        return [idx_to_op[i] for i in order_idx]

    def run(self, graph: Graph) -> Tensor:
        if not graph.ops:
            raise ValueError("graph is empty")
        ops = self._topological_order(graph)
        if self.fusion_hook is not None:
            ops = self.fusion_hook(ops)
        refcounts = self._refcounts(graph)
        produced: Dict[int, Tensor] = {}
        last_output: Optional[Tensor] = None
        for op in ops:
            resolved_inputs: List[Tensor] = []
            for inp in op.inputs:
                if isinstance(inp, TensorRef):
                    if inp.key not in produced:
                        raise ValueError(f"input {inp} has no produced tensor")
                    resolved_inputs.append(produced[inp.key])
                else:
                    resolved_inputs.append(inp)
            out = Tensor.from_shape(queue=resolved_inputs[0].queue, shape=op.shape, dtype=op.dtype, pool=self.pool)
            op.fn(resolved_inputs, out)
            last_output = out
            produced[op.output.key] = out
            # Release inputs if refcount drops to zero
            for t in op.inputs:
                if isinstance(t, TensorRef):
                    refcounts[t.key] -= 1
                    if refcounts[t.key] == 0:
                        tin = produced.get(t.key)
                        if tin is not None and tin.pool_handle is not None and not tin.persistent:
                            self.pool.release(tin.pool_handle)
        if last_output is None:
            raise RuntimeError("execution produced no output")
        return last_output

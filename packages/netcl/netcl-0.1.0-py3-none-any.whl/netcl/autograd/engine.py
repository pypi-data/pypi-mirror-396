"""
Minimal autograd backbone (placeholders).

To be extended with full gradient tracking and backward kernels per op.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional
import threading

from netcl.core.tensor import Tensor


GradFn = Callable[[Any], List[Optional[Tensor]]]


@dataclass
class Node:
    value: Tensor
    grad_fn: Optional[GradFn] = None
    parents: List["Node"] = field(default_factory=list)
    grad: Optional[Tensor] = None
    requires_grad: bool = False


class Tape:
    """
    Records operations for backward.
    """

    def __init__(self) -> None:
        self.nodes: List[Node] = []
        self.enabled: bool = True

    def record(self, node: Node) -> Node:
        if self.enabled:
            self.nodes.append(node)
        return node

    def backward(self, loss: Node, grad: Optional[Tensor] = None) -> None:
        if grad is None:
            # seed with ones
            loss.grad = ones_like(loss.value)
        else:
            loss.grad = grad
        # Reverse topological order (here: recorded order)
        for node in reversed(self.nodes):
            if node.grad is None or node.grad_fn is None:
                continue
            grads = node.grad_fn(node.grad)
            for parent, g in zip(node.parents, grads):
                if g is None:
                    continue
                if parent.grad is None:
                    parent.grad = g
                else:
                    parent.grad = add_inplace(parent.grad, g)
                # propagate to underlying Tensor for optimizers
                if parent.value.grad is None:
                    parent.value.grad = parent.grad
                else:
                    parent.value.grad = add_inplace(parent.value.grad, g)


# thread-local current tape for tape-free APIs
_tls = threading.local()


def set_current_tape(tape: Optional[Tape]):
    _tls.current_tape = tape


def get_current_tape() -> Optional[Tape]:
    return getattr(_tls, "current_tape", None)


def ones_like(t: Tensor) -> Tensor:
    from netcl.core.tensor import Tensor as T
    if t.dtype not in ("float", "float32", "double", "float64"):
        raise ValueError("ones_like supports float tensors")
    import numpy as np

    data = np.ones(t.shape, dtype=np.float32 if "32" in t.dtype or t.dtype == "float" else np.float64)
    return T.from_host(t.queue, data, dtype=t.dtype)


def add_inplace(dst: Tensor, src: Tensor) -> Tensor:
    from netcl.ops.elementwise import elementwise_binary

    return elementwise_binary(dst, src, expression="ADD(v0, v1)", out=dst)


def no_grad():
    """
    Context manager placeholder to disable gradient tracking.
    """

    class _NoGrad:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    return _NoGrad()


def apply_op(fn: Callable[..., Tensor], grad_fn: Optional[GradFn], *args: Node, tape: Optional[Tape] = None) -> Node:
    tape = tape or get_current_tape()
    out_value = fn(*[a.value if isinstance(a, Node) else a for a in args])
    node = Node(
        value=out_value,
        grad_fn=grad_fn,
        parents=[a for a in args if isinstance(a, Node)],
        requires_grad=any(getattr(a, "requires_grad", False) for a in args),
    )
    if tape is not None:
        tape.record(node)
    return node

from __future__ import annotations

import numpy as np

from netcl.core.tensor import Tensor
from netcl.ops.elementwise import elementwise_binary
from netcl.ops.reduction import reduce_sum
from netcl.ops.softmax import softmax


def mse_loss(pred: Tensor, target: Tensor) -> Tensor:
    diff = elementwise_binary(pred, target, expression="SUB(v0, v1)")
    sq = elementwise_binary(diff, diff, expression="MUL(v0, v1)")
    return reduce_sum(sq, axis=None)


def cross_entropy(logits: Tensor, targets: Tensor) -> Tensor:
    """
    Cross-entropy using host-side log/gather (no external frameworks).
    """
    probs = softmax(logits)
    probs_host = probs.to_host()
    targets_host = targets.to_host()
    gather = -np.log(probs_host[np.arange(targets_host.shape[0]), targets_host.astype(np.int64)])
    from netcl.core.tensor import Tensor as T

    return T.from_host(logits.queue, np.array([gather.mean()], dtype=np.float32))

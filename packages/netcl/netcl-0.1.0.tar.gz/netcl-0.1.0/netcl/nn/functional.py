from __future__ import annotations

from netcl import autograd as ag


def relu(x, tape=None):
    return ag.relu(x, tape=tape)


def leaky_relu(x, negative_slope=0.01, tape=None):
    return ag.leaky_relu(x, negative_slope=negative_slope, tape=tape)


def sigmoid(x, tape=None):
    return ag.sigmoid(x, tape=tape)


def tanh(x, tape=None):
    return ag.tanh(x, tape=tape)


def cross_entropy(logits, targets, tape=None):
    # accept int labels or one-hot
    import numpy as np
    from netcl.core.tensor import Tensor
    if hasattr(targets, "value"):
        tgt_val = targets.value
    else:
        tgt_val = targets
    if len(tgt_val.shape) == 1:
        num_classes = logits.value.shape[1] if hasattr(logits, "value") else logits.shape[1]
        tgt_host = tgt_val.to_host() if hasattr(tgt_val, "to_host") else np.array(tgt_val)
        y_oh = np.eye(num_classes, dtype=np.float32)[tgt_host.astype(np.int64)]
        queue = logits.value.queue if hasattr(logits, "value") else tgt_val.queue
        tgt_tensor = ag.tensor(Tensor.from_host(queue, y_oh))
        return ag.cross_entropy(logits, tgt_tensor, tape=tape)
    return ag.cross_entropy(logits, targets, tape=tape)


def mse_loss(pred, target, tape=None):
    return ag.mse_loss(pred, target, tape=tape)


def flatten(x, shape, tape=None):
    return ag.flatten(x, shape, tape=tape)

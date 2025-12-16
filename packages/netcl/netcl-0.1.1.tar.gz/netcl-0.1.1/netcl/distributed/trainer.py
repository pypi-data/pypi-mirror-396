from __future__ import annotations

from typing import Callable, List, Sequence, Tuple, Any

import numpy as np

from netcl.distributed.data_parallel import shard_batch, sync_grads
from netcl.core.tensor import Tensor


def prepare_replicas(params: Sequence[Tensor], queues) -> List[List[Tensor]]:
    """
    Create parameter replicas on each device/queue.
    """
    replicas: List[List[Tensor]] = []
    for q in queues:
        replicas.append([Tensor.from_host(q, p.to_host(), dtype=p.dtype) for p in params])
    return replicas


def data_parallel_step(
    forward_fn: Callable[[Any, np.ndarray, np.ndarray, Sequence[Tensor]], Tuple[Any, Any]],
    params_replicas: List[List[Tensor]],
    optimizers: List[Any],
    batch: Tuple[np.ndarray, np.ndarray],
    *,
    pre_shard_hook: Callable[[np.ndarray, np.ndarray], None] | None = None,
    post_sync_hook: Callable[[List[List[Tensor]]], None] | None = None,
    post_step_hook: Callable[[int], None] | None = None,
):
    """
    Minimal data-parallel training step:
    - shards batch across devices
    - runs forward/backward per device via forward_fn(queue, xb, yb, params)
    - syncs gradients (mean)
    - optimizer step per device

    forward_fn should return (loss_node, tape) with autograd tape supporting backward(loss_node).
    """
    num_devices = len(params_replicas)
    queues = [p[0].queue for p in params_replicas]
    xb, yb = batch
    if pre_shard_hook:
        pre_shard_hook(xb, yb)
    shards_x = shard_batch(xb, num_devices)
    shards_y = shard_batch(yb, num_devices)
    # forward/backward per device
    for dev_idx in range(num_devices):
        q = queues[dev_idx]
        params = params_replicas[dev_idx]
        loss_node, tape = forward_fn(q, shards_x[dev_idx], shards_y[dev_idx], params)
        tape.backward(loss_node)
    # sync grads (in-place on replicas)
    sync_grads(params_replicas)
    if post_sync_hook:
        post_sync_hook(params_replicas)
    # optimizer step per device
    for dev_idx in range(num_devices):
        opt = optimizers[dev_idx]
        opt.step()
        opt.zero_grad()
        if post_step_hook:
            post_step_hook(dev_idx)

from __future__ import annotations

from typing import List, Sequence

import numpy as np

from netcl.distributed.collectives import all_reduce, broadcast
from netcl.core.tensor import Tensor


def shard_batch(x: np.ndarray, num_shards: int) -> List[np.ndarray]:
    """
    Split batch along axis 0 into num_shards chunks.
    """
    return np.array_split(x, num_shards, axis=0)


def replicate_params(params: Sequence[Tensor], queues) -> List[List[Tensor]]:
    """
    Copy parameter tensors to each queue/device.
    """
    replicas: List[List[Tensor]] = []
    for q in queues:
        replicas.append([Tensor.from_host(q, p.to_host(), dtype=p.dtype) for p in params])
    return replicas


def sync_grads(param_replicas: List[List[Tensor]]):
    """
    All-reduce gradients (mean) across devices for each param replica.
    Expects .grad to be populated.
    """
    if len(param_replicas) <= 1:
        return
    num_devices = len(param_replicas)
    num_params = len(param_replicas[0])
    for p_idx in range(num_params):
        grads = []
        for dev_idx in range(num_devices):
            g = param_replicas[dev_idx][p_idx].grad
            if g is None:
                raise ValueError("sync_grads expects grad populated")
            grads.append(g)
        all_reduce(grads, op="mean")


def broadcast_params(src_params: Sequence[Tensor], dst_param_groups: List[List[Tensor]], root: int = 0):
    """
    Broadcast parameters from root group to others.
    """
    src = dst_param_groups[root] if src_params is None else src_params  # type: ignore
    for idx in range(len(dst_param_groups[0])):
        tensors = [group[idx] for group in dst_param_groups]
        tensors[root] = src[idx]
        broadcast(tensors, root=root)

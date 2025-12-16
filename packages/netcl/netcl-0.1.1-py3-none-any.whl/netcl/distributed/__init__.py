"""
Distributed utilities (host-based MVP).
"""

from .collectives import all_reduce, broadcast, scatter, gather
from .device_manager import DeviceManager
from .data_parallel import shard_batch, replicate_params, sync_grads, broadcast_params
from .trainer import prepare_replicas, data_parallel_step

__all__ = [
    "all_reduce",
    "broadcast",
    "scatter",
    "gather",
    "DeviceManager",
    "shard_batch",
    "replicate_params",
    "sync_grads",
    "broadcast_params",
    "prepare_replicas",
    "data_parallel_step",
]

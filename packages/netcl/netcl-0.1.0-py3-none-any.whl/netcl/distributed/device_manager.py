from __future__ import annotations

from typing import List, Optional

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

from netcl.core.device import manager


class DeviceManager:
    """
    Simple multi-queue manager for data-parallel runs.
    """

    def __init__(self, devices: Optional[List["cl.Device"]] = None):
        if cl is None:
            raise ImportError("pyopencl required for DeviceManager")
        if devices is None:
            ctx = manager.default().context
            devices = ctx.devices
        self.devices = devices
        self.contexts = [cl.Context([d]) for d in self.devices]
        self.queues = [cl.CommandQueue(ctx) for ctx in self.contexts]

    def num_devices(self) -> int:
        return len(self.devices)

    def get_queues(self) -> List["cl.CommandQueue"]:
        return self.queues


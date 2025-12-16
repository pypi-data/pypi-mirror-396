"""
Device discovery and context/queue helpers for PyOpenCL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    cl = None


@dataclass
class DeviceHandle:
    platform_name: str
    device_name: str
    context: "cl.Context"
    queue: "cl.CommandQueue"


class DeviceManager:
    """
    Lightweight device manager to obtain a default context/queue.
    """

    def __init__(self) -> None:
        self._default: Optional[DeviceHandle] = None

    def discover(self) -> List[Tuple["cl.Platform", "cl.Device"]]:
        if cl is None:
            return []
        try:
            platforms = cl.get_platforms()
        except Exception:
            return []
        pairs: List[Tuple["cl.Platform", "cl.Device"]] = []
        for plat in platforms:
            try:
                devices = plat.get_devices()
            except Exception:
                continue
            for dev in devices:
                pairs.append((plat, dev))
        return pairs

    def default(self) -> Optional[DeviceHandle]:
        if self._default is not None:
            return self._default
        if cl is None:
            return None
        pairs = self.discover()
        if not pairs:
            return None
        plat, dev = pairs[0]
        ctx = cl.Context(devices=[dev])
        queue = cl.CommandQueue(ctx, dev)
        self._default = DeviceHandle(
            platform_name=plat.name, device_name=dev.name, context=ctx, queue=queue
        )
        return self._default


manager = DeviceManager()

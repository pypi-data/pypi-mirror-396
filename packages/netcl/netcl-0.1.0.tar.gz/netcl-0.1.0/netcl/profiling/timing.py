"""
Timing helpers for OpenCL events (placeholder implementation).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


@dataclass
class ProfileRecord:
    name: str
    duration_ms: float


class EventTimer:
    def __init__(self, queue: Optional["cl.CommandQueue"] = None) -> None:
        self.queue = queue

    def time_event(self, event: "cl.Event", name: str = "") -> ProfileRecord:
        if cl is None:
            raise ImportError("pyopencl required for event timing")
        event.wait()
        start = event.profile.start
        end = event.profile.end
        duration_ms = (end - start) * 1e-6
        return ProfileRecord(name=name, duration_ms=duration_ms)

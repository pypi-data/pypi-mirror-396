from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def debug_tape(tape):
    """
    Context manager to expose a tape for debugging/inspection.
    """
    yield tape

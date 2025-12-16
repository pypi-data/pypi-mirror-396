from __future__ import annotations

import sys
import time
from typing import Dict, Optional


class ProgressBar:
    """
    Lightweight text progress bar with it/s, epoch, ETA.
    """

    def __init__(self, total: int, epoch: Optional[int] = None, width: int = 30, enable: bool = True) -> None:
        self.total = max(1, total)
        self.epoch = epoch
        self.width = width
        self.enable = enable
        self.start_time = time.perf_counter()
        self.last_time = self.start_time
        self.last_print = ""

    def _format_line(self, step: int, info: Dict[str, float]) -> str:
        step = min(step, self.total)
        frac = step / self.total
        filled = int(frac * self.width)
        bar = "[" + "#" * filled + "-" * (self.width - filled) + "]"
        now = time.perf_counter()
        elapsed = now - self.start_time
        it_s = step / elapsed if elapsed > 0 else 0.0
        eta = (self.total - step) / it_s if it_s > 0 else 0.0
        parts = []
        if self.epoch is not None:
            parts.append(f"epoch {self.epoch}")
        parts.append(f"{step}/{self.total}")
        parts.append(bar)
        parts.append(f"{it_s:.1f} it/s")
        parts.append(f"ETA {eta:.1f}s")
        for k, v in info.items():
            parts.append(f"{k}={v}")
        return " ".join(parts)

    def update(self, step: int, info: Optional[Dict[str, float]] = None) -> None:
        if not self.enable:
            return
        line = self._format_line(step, info or {})
        # Clear remnants of previous longer line to avoid leftover characters (e.g., "%%%" artifacts)
        pad = ""
        if len(self.last_print) > len(line):
            pad = " " * (len(self.last_print) - len(line))
        sys.stderr.write("\r" + line + pad)
        sys.stderr.flush()
        self.last_print = line

    def close(self) -> None:
        if not self.enable:
            return
        sys.stderr.write("\n")
        sys.stderr.flush()

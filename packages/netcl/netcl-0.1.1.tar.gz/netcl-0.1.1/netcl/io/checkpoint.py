from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor


def save_params(params: Iterable[Tensor], path: str | Path, names: Iterable[str] | None = None) -> None:
    arrs: Dict[str, np.ndarray] = {}
    if names is None:
        names = [f"p{i}" for i, _ in enumerate(params)]
    for n, p in zip(names, params):
        arrs[n] = p.to_host()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **arrs)


def load_params(queue: "cl.CommandQueue", params: Iterable[Tensor], path: str | Path, names: Iterable[str] | None = None) -> None:
    data = np.load(path)
    if names is None:
        names = [f"p{i}" for i, _ in enumerate(params)]
    for n, p in zip(names, params):
        if n not in data:
            raise KeyError(f"missing param {n} in checkpoint")
        arr = data[n]
        if arr.shape != p.shape:
            raise ValueError(f"shape mismatch for {n}: ckpt {arr.shape} vs param {p.shape}")
        cl.enqueue_copy(queue, p.buffer, arr.astype(np.float32)).wait()


def save_checkpoint(params: Iterable[Tensor], path: str | Path, optim_state: dict | None = None, config: dict | None = None, names: Iterable[str] | None = None) -> None:
    """
    Save params (NPZ) plus optional optimizer state/config (JSON alongside).
    """
    path = Path(path)
    save_params(params, path, names=names)
    meta = {"optim_state": optim_state or {}, "config": config or {}}
    import json

    with open(path.with_suffix(".json"), "w", encoding="utf-8") as f:
        json.dump(meta, f)


def load_checkpoint(queue: "cl.CommandQueue", params: Iterable[Tensor], path: str | Path, names: Iterable[str] | None = None):
    load_params(queue, params, path, names=names)
    meta = {}
    import json

    json_path = Path(path).with_suffix(".json")
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    return meta

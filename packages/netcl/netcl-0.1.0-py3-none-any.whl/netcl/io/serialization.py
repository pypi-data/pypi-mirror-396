"""
Model serialization without external AI frameworks.

Saves architecture as JSON (Sequential config) and weights as NPZ.
Supported layers (Sequential): Conv2d, Linear, ReLU, LeakyReLU, Sigmoid, Tanh, Dropout, MaxPool2d, Flatten.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import numpy as np

from netcl.nn.layers import (
    Linear,
    ReLU,
    LeakyReLU,
    Sigmoid,
    Tanh,
    Dropout,
    MaxPool2d,
    Flatten,
    Sequential,
    Conv2d,
    Module,
)
from netcl.nn.factory import build_sequential


def _layer_meta(layer: Module) -> Dict[str, Any]:
    if isinstance(layer, Linear):
        return {"type": "Linear", "args": {"in_features": layer.in_features, "out_features": layer.out_features, "bias": layer.bias is not None}}
    if isinstance(layer, ReLU):
        return {"type": "ReLU", "args": {}}
    if isinstance(layer, LeakyReLU):
        return {"type": "LeakyReLU", "args": {"negative_slope": layer.negative_slope}}
    if isinstance(layer, Sigmoid):
        return {"type": "Sigmoid", "args": {}}
    if isinstance(layer, Tanh):
        return {"type": "Tanh", "args": {}}
    if isinstance(layer, Dropout):
        return {"type": "Dropout", "args": {"p": layer.p, "seed": layer.seed}}
    if isinstance(layer, MaxPool2d):
        return {"type": "MaxPool2d", "args": {"kernel_size": layer.kernel_size, "stride": layer.stride}}
    if isinstance(layer, Flatten):
        return {"type": "Flatten", "args": {}}
    if isinstance(layer, Conv2d):
        return {
            "type": "Conv2d",
            "args": {
                "in_channels": layer.in_channels,
                "out_channels": layer.out_channels,
                "kernel_size": layer.kernel_size,
                "stride": layer.stride,
                "pad": layer.pad,
            },
        }
    raise ValueError(f"unsupported layer type {type(layer)} for serialization")


def _sequential_config(model: Sequential) -> List[Dict[str, Any]]:
    return [_layer_meta(l) for l in model.layers]


def save_model(model: Sequential, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    config = _sequential_config(model)
    meta = {"type": "Sequential", "config": config, "version": 1}
    weights: Dict[str, np.ndarray] = {}
    idx = 0
    for layer in model.layers:
        sd = layer.state_dict()
        for key, val in sd.items():
            if isinstance(val, np.ndarray):
                weights[f"{idx}:{key}"] = val
        idx += 1
    json_path = path + ".json"
    npz_path = path + ".npz"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)
    np.savez(npz_path, **weights)


def load_model(path: str, queue=None, pool=None) -> Sequential:
    if queue is None:
        from netcl.core.device import manager

        dev = manager.default()
        if dev is None:
            raise RuntimeError("No OpenCL device available for load_model")
        queue = dev.queue
    json_path = path + ".json"
    npz_path = path + ".npz"
    with open(json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("type") != "Sequential":
        raise ValueError("only Sequential models supported")
    config: List[Dict[str, Any]] = meta.get("config")
    if config is None and "layers" in meta:
        config = [{"type": m["type"], "args": {k: v for k, v in m.items() if k != "type"}} for m in meta["layers"]]
    model = build_sequential(queue, config)
    weights = np.load(npz_path, allow_pickle=False)
    idx = 0
    for layer in model.layers:
        sd = layer.state_dict()
        new_sd = {}
        for key in sd:
            wkey = f"{idx}:{key}"
            if wkey in weights:
                new_sd[key] = weights[wkey]
            else:
                new_sd[key] = sd[key]
        layer.load_state_dict(new_sd)
        idx += 1
    return model

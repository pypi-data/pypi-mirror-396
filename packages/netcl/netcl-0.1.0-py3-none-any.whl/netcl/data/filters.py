"""
Simple filter/transform API for NCHW batches (NumPy), CPU-side.
Filters are callables (xb, yb) -> (xb, yb).
"""

from __future__ import annotations

from typing import Callable, Iterable, List, Tuple
import numpy as np

Filter = Callable[[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]


def apply_filters(batch: Tuple[np.ndarray, np.ndarray], filters: Iterable[Filter]) -> Tuple[np.ndarray, np.ndarray]:
    xb, yb = batch
    for f in filters:
        xb, yb = f(xb, yb)
    return xb, yb


def normalize(mean: Tuple[float, float, float], std: Tuple[float, float, float]) -> Filter:
    mean_arr = np.array(mean, dtype=np.float32).reshape(1, -1, 1, 1)
    std_arr = np.array(std, dtype=np.float32).reshape(1, -1, 1, 1)

    def _fn(xb: np.ndarray, yb: np.ndarray):
        return (xb - mean_arr) / (std_arr + 1e-6), yb

    return _fn


def horizontal_flip(p: float = 0.5) -> Filter:
    def _fn(xb: np.ndarray, yb: np.ndarray):
        mask = np.random.rand(xb.shape[0]) < p
        xb_flipped = xb.copy()
        xb_flipped[mask] = xb_flipped[mask, :, :, ::-1]
        return xb_flipped, yb

    return _fn


def random_crop(padding: int = 4, crop_size: int = 32) -> Filter:
    def _fn(xb: np.ndarray, yb: np.ndarray):
        N, C, H, W = xb.shape
        if H < crop_size or W < crop_size:
            return xb, yb
        padded = np.pad(xb, ((0, 0), (0, 0), (padding, padding), (padding, padding)), mode="reflect")
        cropped = np.empty_like(xb)
        for i in range(N):
            h0 = np.random.randint(0, H + 2 * padding - crop_size + 1)
            w0 = np.random.randint(0, W + 2 * padding - crop_size + 1)
            cropped[i] = padded[i, :, h0 : h0 + crop_size, w0 : w0 + crop_size]
        return cropped, yb

    return _fn


def default_cifar10_filters() -> List[Filter]:
    """
    Returns a standard CIFAR-10 preprocessing pipeline: random crop+flip + normalize.
    """
    return [
        random_crop(padding=4, crop_size=32),
        horizontal_flip(p=0.5),
        normalize(mean=(0.4914, 0.4822, 0.4465), std=(0.2023, 0.1994, 0.2010)),
    ]

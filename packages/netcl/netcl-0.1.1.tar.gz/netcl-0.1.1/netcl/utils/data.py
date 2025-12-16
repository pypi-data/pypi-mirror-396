from __future__ import annotations

from typing import Tuple

import numpy as np


def split_dataset(
    x: np.ndarray,
    y: np.ndarray,
    val_ratio: float = 0.1,
    test_ratio: float = 0.0,
    shuffle: bool = True,
    seed: int | None = None,
) -> Tuple[tuple[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]]:
    """
    Split arrays into train/val/test.
    """
    assert 0 <= val_ratio < 1 and 0 <= test_ratio < 1 and val_ratio + test_ratio < 1
    n = x.shape[0]
    idx = np.arange(n)
    if shuffle:
        rng = np.random.default_rng(seed)
        rng.shuffle(idx)
    x = x[idx]
    y = y[idx]
    n_test = int(n * test_ratio)
    n_val = int(n * val_ratio)
    n_train = n - n_val - n_test
    x_train, y_train = x[:n_train], y[:n_train]
    x_val, y_val = x[n_train : n_train + n_val], y[n_train : n_train + n_val]
    x_test, y_test = x[n_train + n_val :], y[n_train + n_val :]
    return (x_train, y_train), (x_val, y_val), (x_test, y_test)

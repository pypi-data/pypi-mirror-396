from __future__ import annotations

import numpy as np


def random_erase(x: np.ndarray, p: float = 0.5, scale=(0.02, 0.2), ratio=(0.3, 3.3)):
    """
    Random Erase on NCHW batch (CPU). x is modified in-place copy returned.
    """
    out = x.copy()
    N, C, H, W = out.shape
    for i in range(N):
        if np.random.rand() > p:
            continue
        s = np.random.uniform(scale[0], scale[1]) * H * W
        r = np.random.uniform(ratio[0], ratio[1])
        h = int(np.sqrt(s * r))
        w = int(np.sqrt(s / r))
        if h >= H or w >= W:
            continue
        y = np.random.randint(0, H - h + 1)
        x0 = np.random.randint(0, W - w + 1)
        out[i, :, y : y + h, x0 : x0 + w] = 0
    return out


def cutout(x: np.ndarray, size: int = 8):
    out = x.copy()
    N, C, H, W = out.shape
    for i in range(N):
        cy = np.random.randint(size, H - size)
        cx = np.random.randint(size, W - size)
        out[i, :, cy - size : cy + size, cx - size : cx + size] = 0
    return out


def color_jitter(x: np.ndarray, brightness: float = 0.2, contrast: float = 0.2, saturation: float = 0.0):
    out = x.copy()
    # assume NCHW with values ~ normalized [-? , ?]
    b = np.random.uniform(-brightness, brightness)
    c = 1 + np.random.uniform(-contrast, contrast)
    out = out * c + b
    return out

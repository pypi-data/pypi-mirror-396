from __future__ import annotations

import numpy as np
from typing import Iterable, Iterator, Tuple, Optional, Callable, Any
import threading
from queue import Queue


class DataLoader:
    def __init__(
        self,
        dataset: Iterable,
        batch_size: int = 32,
        shuffle: bool = True,
        drop_last: bool = False,
        seed: Optional[int] = None,
        prefetch: int = 0,
        device_queue=None,
        augment: Optional[Callable[[Any], Any]] = None,
        overlap: bool = False,
        autocast: bool = False,
        transforms: Optional[Callable[[Any, Any], Any] | Iterable[Callable[[Any, Any], Any]]] = None,
    ):
        self.dataset = list(dataset)
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.drop_last = drop_last
        self.rng = np.random.default_rng(seed)
        self.prefetch = prefetch
        self.device_queue = device_queue
        self.augment = augment
        self.overlap = overlap
        self.autocast = autocast
        self.transforms = transforms

    def __iter__(self) -> Iterator:
        idx = np.arange(len(self.dataset))
        if self.shuffle:
            self.rng.shuffle(idx)
        batch = []
        for i in idx:
            batch.append(self.dataset[i])
            if len(batch) == self.batch_size:
                yield self._process_batch(batch)
                batch = []
        if batch and not self.drop_last:
            yield self._process_batch(batch)

    def _stack(self, batch):
        # assume each item is (x, y) arrays
        xs, ys = zip(*batch)
        return np.stack(xs, axis=0), np.stack(ys, axis=0)

    def _process_batch(self, batch):
        xb, yb = self._stack(batch)
        # apply optional CPU transforms first
        if self.transforms is not None:
            if callable(self.transforms):
                xb, yb = self.transforms(xb, yb)
            else:
                for t in self.transforms:
                    xb, yb = t(xb, yb)
        if self.augment is None:
            return xb, yb
        # Optional overlap: submit augment on separate queue if provided
        if self.overlap and self.device_queue is not None and hasattr(self.device_queue, "context"):
            import pyopencl as cl  # type: ignore

            aug_queue = cl.CommandQueue(self.device_queue.context, properties=self.device_queue.properties)
            # reuse a single augment queue per loader to avoid churn
            if not hasattr(self, "_aug_queue"):
                self._aug_queue = aug_queue
            return self._call_augment((xb, yb), device_queue=self._aug_queue)
        return self._call_augment((xb, yb), device_queue=self.device_queue)

    def _call_augment(self, batch, **kwargs):
        # prefer passing autocast flag if augment accepts it; otherwise fall back
        try:
            return self.augment(batch, autocast=self.autocast, **kwargs)
        except TypeError:
            return self.augment(batch, **kwargs)

    def __len__(self) -> int:
        n = len(self.dataset)
        if self.drop_last:
            return n // self.batch_size
        return (n + self.batch_size - 1) // self.batch_size

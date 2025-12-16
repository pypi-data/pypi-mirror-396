from __future__ import annotations

from netcl.nn.modules import Module, Sequential
from netcl.nn.layers import Conv2d, ReLU, MaxPool2d, Flatten, Linear


class SimpleCNN(Module):
    """
    Declarative-style simple CNN: conv->relu->pool->conv->relu->pool->flatten->fc.
    """

    def __init__(self, in_channels: int = 3, num_classes: int = 10, c1: int = 32, c2: int = 64, hidden: int = 128, queue=None):
        super().__init__()
        from netcl.core.device import manager
        if queue is None:
            queue = manager.default().queue
        self.conv1 = Conv2d(queue, in_channels, c1, kernel_size=3, stride=1, pad=1)
        self.relu1 = ReLU()
        self.pool1 = MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = Conv2d(queue, c1, c2, kernel_size=3, stride=1, pad=1)
        self.relu2 = ReLU()
        self.pool2 = MaxPool2d(kernel_size=2, stride=2)
        self.flatten = Flatten()
        self.fc1 = Linear(queue, c2 * 8 * 8, hidden)
        self.relu3 = ReLU()
        self.fc2 = Linear(queue, hidden, num_classes)
        self.layers = Sequential(
            self.conv1,
            self.relu1,
            self.pool1,
            self.conv2,
            self.relu2,
            self.pool2,
            self.flatten,
            self.fc1,
            self.relu3,
            self.fc2,
        )

    def __call__(self, x):
        return self.layers(x)

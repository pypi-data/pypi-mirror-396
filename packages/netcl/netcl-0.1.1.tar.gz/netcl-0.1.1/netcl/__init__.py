"""
netcl: PyOpenCL-based experimentation framework.
This package currently focuses on low-level kernel primitives and helpers.
"""

from . import core, ops, autograd, distributed, runtime, profiling
from .ops import (
    matmul,
    build_matmul_kernel,
    elementwise_binary,
    relu,
    bias_add,
    reduce_sum,
    softmax,
    conv2d,
)
from . import nn, optim, io

__all__ = [
    "core",
    "ops",
    "autograd",
    "distributed",
    "runtime",
    "profiling",
    "nn",
    "optim",
    "io",
    "matmul",
    "build_matmul_kernel",
    "elementwise_binary",
    "relu",
    "bias_add",
    "reduce_sum",
    "softmax",
    "conv2d",
]

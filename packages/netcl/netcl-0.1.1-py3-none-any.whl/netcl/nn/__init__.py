from .layers import Module, Linear, ReLU, Sequential, Conv2d, Sigmoid, Tanh, LeakyReLU, Dropout, MaxPool2d
from netcl.core.parameter import Parameter
from .init import xavier_uniform, kaiming_uniform
from .loss import mse_loss, cross_entropy
from .pooling import max_pool2d
from .factory import build_sequential, build_sequential_from_json, register_layer, get_registry, example_cnn_config, example_mlp_config
from .batchnorm import BatchNorm2dModule as BatchNorm2d
from .decorators import model

__all__ = [
    "Module",
    "Linear",
    "ReLU",
    "Sequential",
    "Conv2d",
    "Sigmoid",
    "Tanh",
    "LeakyReLU",
    "Dropout",
    "MaxPool2d",
    "Parameter",
    "model",
    "BatchNorm2d",
    "xavier_uniform",
    "kaiming_uniform",
    "mse_loss",
    "cross_entropy",
    "max_pool2d",
    "build_sequential",
    "build_sequential_from_json",
    "register_layer",
    "get_registry",
    "example_cnn_config",
    "example_mlp_config",
]


def __getattr__(name):
    if name == "ResNet18":
        from .resnet import ResNet18 as _ResNet18
        return _ResNet18
    if name == "functional":
        import netcl.nn.functional as _functional
        return _functional
    if name == "build_sequential_from_json":
        from .factory import build_sequential_from_json as _bsfj
        return _bsfj
    raise AttributeError(f"module 'netcl.nn' has no attribute {name}")

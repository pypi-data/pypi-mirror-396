from __future__ import annotations

from typing import Callable

from netcl.nn.layers import Module


def model(cls: type) -> type:
    """
    Decorator for declarative Models.

    Requirements:
    - Class defines __setup__(self, *args, **kwargs) and assigns submodules/params there.
    - Optional forward; if missing, a simple sequential forward over Module attributes is generated.
    - Sets self.training = True in __init__.
    """
    if not hasattr(cls, "__setup__"):
        raise ValueError("@netcl.model requires a __setup__ method")

    setup_fn: Callable = getattr(cls, "__setup__")
    orig_init = getattr(cls, "__init__", None)

    def __init__(self, *args, **kwargs):
        # Call potential parent __init__
        if orig_init is not None and orig_init is not object.__init__:
            orig_init(self, *args, **kwargs)
        self.training = True
        setup_fn(self, *args, **kwargs)

    cls.__init__ = __init__

    # Only generate a forward if the class did not override it (or left NotImplemented)
    forward_attr = getattr(cls, "forward", None)
    if forward_attr is None or forward_attr is Module.forward:
        def forward(self, x):
            out = x
            # Iterate in attribute insertion order over Modules
            for _, v in self.__dict__.items():
                if isinstance(v, Module):
                    try:
                        out = v(out)
                    except TypeError:
                        out = v(out)
            return out

        cls.forward = forward  # type: ignore

    return cls

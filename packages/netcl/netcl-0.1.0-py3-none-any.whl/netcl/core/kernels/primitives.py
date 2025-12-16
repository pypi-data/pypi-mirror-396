"""
Elementary OpenCL primitives, kernel generation helpers, and basic workgroup tuning.

The goal is to keep complex operations composable from a small set of primitives
such as loads, stores, simple arithmetic, and local reductions. Higher-level
operations (elementwise, reductions, matmul tiles) can be assembled by the
generator functions below.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import math
import textwrap

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover - optional dependency for pure generation tests
    cl = None


PRIMITIVE_PREAMBLE = textwrap.dedent(
    """
    // Primitive building blocks
    #define LOAD(ptr, idx) (ptr[idx])
    #define STORE(ptr, idx, value) (ptr[idx] = value)
    #define ADD(a, b) ((a) + (b))
    #define SUB(a, b) ((a) - (b))
    #define MUL(a, b) ((a) * (b))
    #define DIV(a, b) ((a) / (b))
    #define RELU(x) ((x) > 0 ? (x) : 0)
    """
)


@dataclass
class KernelSpec:
    """Structured representation of a generated kernel."""

    name: str
    params: Sequence[str]
    body: str
    preamble: str = ""

    def to_source(self) -> str:
        param_list = ", ".join(self.params)
        return textwrap.dedent(
            f"""
            {self.preamble}
            __kernel void {self.name}({param_list}) {{
            {textwrap.indent(self.body, '    ')}
            }}
            """
        ).strip()


class WorkGroupTuner:
    """
    Lightweight heuristics for choosing local and global sizes.

    This is intentionally simple: it favors power-of-two local sizes up to a
    cap derived from the device limits. The global size is rounded up to the
    next multiple of the local size.
    """

    def __init__(self, max_local: int = 256) -> None:
        self.max_local = max_local

    def choose_local_size(self, device: "cl.Device") -> int:
        limit = min(self.max_local, device.max_work_group_size)
        # pick the highest power-of-two not exceeding limit
        size = 1
        while size * 2 <= limit:
            size *= 2
        return max(1, size)

    def global_local_sizes(self, n_items: int, device: Optional["cl.Device"]) -> Tuple[int, Optional[int]]:
        if device is None:
            local = None
            global_size = n_items
        else:
            local = self.choose_local_size(device)
            global_size = int(math.ceil(n_items / local) * local)
        return global_size, local


def _normalize_dtype(dtype: str) -> str:
    mapping = {
        "float32": "float",
        "float": "float",
        "float16": "half",
        "half": "half",
        "float64": "double",
        "double": "double",
    }
    if dtype not in mapping:
        raise ValueError(f"unsupported dtype {dtype}")
    return mapping[dtype]


class PrimitiveBuilder:
    """
    Builds basic OpenCL kernels from primitive components.

    Supports pure source generation (when PyOpenCL is unavailable) and actual
    compilation when a context is provided.
    """

    def __init__(self, dtype: str = "float", tuner: Optional[WorkGroupTuner] = None) -> None:
        self.dtype = _normalize_dtype(dtype)
        self.tuner = tuner or WorkGroupTuner()

    def elementwise_spec(self, name: str, arity: int, expression: str) -> KernelSpec:
        params: List[str] = [f"__global const {self.dtype}* in{i}" for i in range(arity)]
        params.append(f"__global {self.dtype}* out")
        params.append("const int n")
        loads: List[str] = [f"{self.dtype} v{i} = LOAD(in{i}, gid);" for i in range(arity)]
        body_lines: List[str] = [
            "const int gid = get_global_id(0);",
            "if (gid >= n) return;",
            *loads,
            f"{self.dtype} out_val = {expression};",
            "STORE(out, gid, out_val);",
        ]
        body = "\n".join(body_lines)
        return KernelSpec(name=name, params=params, body=body, preamble=PRIMITIVE_PREAMBLE)

    def build(self, context: "cl.Context", spec: KernelSpec, options: Optional[str] = None) -> "cl.Kernel":
        if cl is None:
            raise ImportError("pyopencl is required to build kernels")
        program = cl.Program(context, spec.to_source()).build(options=options or "")
        return getattr(program, spec.name)


def build_elementwise_kernel(
    context: Optional["cl.Context"],
    name: str,
    arity: int,
    expression: str,
    dtype: str = "float",
    options: Optional[str] = None,
    tuner: Optional[WorkGroupTuner] = None,
) -> Tuple[KernelSpec, Optional["cl.Kernel"]]:
    """
    Convenience wrapper: generate an elementwise kernel and optionally build it.

    If context is None, only the KernelSpec is returned (for codegen/testing).
    """
    builder = PrimitiveBuilder(dtype=dtype, tuner=tuner)
    spec = builder.elementwise_spec(name=name, arity=arity, expression=expression)
    if context is None:
        return spec, None
    build_opts = options or ""
    if dtype in ("half", "float16"):
        build_opts = build_opts + " -cl-fast-relaxed-math -cl-mad-enable -cl-std=CL1.2"
        spec.preamble = "#pragma OPENCL EXTENSION cl_khr_fp16 : enable\n" + spec.preamble  # enable fp16
    kernel = builder.build(context, spec, options=build_opts)
    return spec, kernel

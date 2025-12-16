"""
Tiled matrix multiplication built from basic OpenCL primitives (no special instructions).
"""

from __future__ import annotations

from typing import Optional, Tuple

from netcl.core.kernels import KernelSpec
from netcl.core.tensor import Tensor
from netcl.core.memory import BufferPool

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


_DTYPE_INFO = {
    "float": ("float", 4),
    "float32": ("float", 4),
    "half": ("half", 2),
    "float16": ("half", 2),
    "double": ("double", 8),
    "float64": ("double", 8),
}


def _dtype_info(dtype: str) -> Tuple[str, int]:
    if dtype not in _DTYPE_INFO:
        raise ValueError(f"unsupported dtype {dtype}")
    return _DTYPE_INFO[dtype]


def choose_tile_size(device: Optional["cl.Device"], requested: int = 16, dtype_bytes: int = 4) -> int:
    """
    Choose a tile size that does not exceed the device's max work-group size.
    Prefers power-of-two sizes up to requested.
    """
    tile = requested
    if device is None:
        return tile
    limit = device.max_work_group_size
    dim_limit = min(device.max_work_item_sizes[0], device.max_work_item_sizes[1])
    local_mem_limit = getattr(device, "local_mem_size", 0)
    while (
        (tile * tile > limit)
        or (tile > dim_limit)
        or (local_mem_limit and (tile * tile * dtype_bytes * 2) > local_mem_limit)
    ) and tile > 1:
        tile //= 2
    tile = max(1, tile)
    if tile < 4:
        candidate = 4
        if (
            candidate * candidate <= limit
            and candidate <= dim_limit
            and (local_mem_limit == 0 or (candidate * candidate * dtype_bytes * 2) <= local_mem_limit)
        ):
            tile = candidate
    return tile


def matmul_kernel_spec(tile: int = 16, dtype: str = "float") -> KernelSpec:
    preamble = ""
    if dtype == "half":
        preamble = "#pragma OPENCL EXTENSION cl_khr_fp16 : enable\n"
    body = f"""
    const int row = get_global_id(0);
    const int col = get_global_id(1);
    const int local_row = get_local_id(0);
    const int local_col = get_local_id(1);
    __local {dtype} As[{tile}][{tile}];
    __local {dtype} Bs[{tile}][{tile}];
    {dtype} acc = 0;
    const int num_tiles = (K + {tile} - 1) / {tile};
    for (int t = 0; t < num_tiles; ++t) {{
        int k_base = t * {tile};
        int a_col = k_base + local_col;
        int b_row = k_base + local_row;
        {dtype} a_val = 0;
        {dtype} b_val = 0;
        if (row < M && a_col < K) {{
            a_val = A[row * K + a_col];
        }}
        if (b_row < K && col < N) {{
            b_val = B[b_row * N + col];
        }}
        As[local_row][local_col] = a_val;
        Bs[local_row][local_col] = b_val;
        barrier(CLK_LOCAL_MEM_FENCE);
        for (int k = 0; k < {tile}; ++k) {{
            acc += As[local_row][k] * Bs[k][local_col];
        }}
        barrier(CLK_LOCAL_MEM_FENCE);
    }}
    if (row < M && col < N) {{
        C[row * N + col] = acc;
    }}
    """
    params = [
        f"__global const {dtype}* A",
        f"__global const {dtype}* B",
        f"__global {dtype}* C",
        "const int M",
        "const int N",
        "const int K",
    ]
    return KernelSpec(name=f"matmul_t{tile}", params=params, body=body, preamble=preamble)


def build_matmul_kernel(
    context: Optional["cl.Context"], tile: int = 16, dtype: str = "float"
) -> Tuple[KernelSpec, Optional["cl.Kernel"]]:
    ocl_dtype, _ = _dtype_info(dtype)
    spec = matmul_kernel_spec(tile=tile, dtype=ocl_dtype)
    if context is None:
        return spec, None
    if cl is None:
        raise ImportError("pyopencl is required to build matmul kernels")
    build_opts = ""
    if ocl_dtype == "half":
        build_opts = "-cl-fast-relaxed-math -cl-std=CL1.2"
    program = cl.Program(context, spec.to_source()).build(options=build_opts)
    return spec, getattr(program, spec.name)


def matmul(a: Tensor, b: Tensor, tile: int = 16, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for matmul")
    if a.queue != b.queue:
        raise ValueError("input tensors must share the same command queue")
    if len(a.shape) != 2 or len(b.shape) != 2:
        raise ValueError("matmul expects 2D tensors")
    M, K = a.shape
    Kb, N = b.shape
    if K != Kb:
        raise ValueError("inner dimensions must match for matmul")
    dtype = a.dtype
    if dtype != b.dtype:
        raise ValueError("dtype mismatch between inputs")
    ocl_dtype, dtype_bytes = _dtype_info(dtype)

    queue = a.queue
    ctx = a.context
    tile_eff = choose_tile_size(
        ctx.devices[0] if ctx.devices else None, requested=tile, dtype_bytes=dtype_bytes
    )

    spec, kernel = build_matmul_kernel(context=ctx, tile=tile_eff, dtype=ocl_dtype)
    if kernel is None:
        raise RuntimeError("failed to build matmul kernel")

    mf = cl.mem_flags
    if out is None:
        if pool is not None:
            handle = pool.allocate(M * N * dtype_bytes)
            buf_out = handle.buffer
            out = Tensor(buffer=buf_out, shape=(M, N), dtype=dtype, context=ctx, queue=queue, pool_handle=handle)
        else:
            buf_out = cl.Buffer(ctx, mf.WRITE_ONLY, size=M * N * dtype_bytes)
            out = Tensor(buffer=buf_out, shape=(M, N), dtype=dtype, context=ctx, queue=queue)
    else:
        if out.shape != (M, N):
            raise ValueError("output tensor has wrong shape")
        if out.dtype != dtype:
            raise ValueError("output tensor dtype mismatch")

    # Global sizes rounded up to tile size.
    g0 = ((M + tile_eff - 1) // tile_eff) * tile_eff
    g1 = ((N + tile_eff - 1) // tile_eff) * tile_eff
    local = (tile_eff, tile_eff)
    m_i = np.int32(M) if np is not None else M
    n_i = np.int32(N) if np is not None else N
    k_i = np.int32(K) if np is not None else K
    kernel(queue, (g0, g1), local, a.buffer, b.buffer, out.buffer, m_i, n_i, k_i)
    return out

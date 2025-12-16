"""
Elementwise operation helper built on PrimitiveBuilder.
"""

from __future__ import annotations

from typing import Optional, Tuple

from netcl.core.kernels import build_elementwise_kernel, KernelSpec
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


_DTYPE_NBYTES = {"float": 4, "float32": 4, "double": 8, "float64": 8}
_DTYPE_CNAME = {"float": "float", "float32": "float", "half": "half", "float16": "half", "double": "double", "float64": "double"}


def _dtype_nbytes(dtype: str) -> int:
    if dtype not in _DTYPE_NBYTES:
        raise ValueError(f"unsupported dtype {dtype}")
    return _DTYPE_NBYTES[dtype]


_KERNEL_CACHE = {}


def _get_binary_kernel(ctx: "cl.Context", dtype: str, expression: str) -> "cl.Kernel":
    cache_key = (ctx.int_ptr, dtype, expression)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    _, kernel = build_elementwise_kernel(
        context=ctx, name="eltwise_bin", arity=2, expression=expression, dtype=dtype
    )
    if kernel is None:
        raise RuntimeError("failed to build elementwise kernel")
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _get_unary_kernel(ctx: "cl.Context", dtype: str, expression: str) -> "cl.Kernel":
    cache_key = (ctx.int_ptr, dtype, expression, "unary")
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    _, kernel = build_elementwise_kernel(
        context=ctx, name="eltwise_un", arity=1, expression=expression, dtype=dtype
    )
    if kernel is None:
        raise RuntimeError("failed to build elementwise kernel")
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def elementwise_binary(
    a: Tensor, b: Tensor, expression: str, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None
) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    if a.queue != b.queue:
        raise ValueError("input tensors must share the same command queue")
    if a.shape != b.shape:
        raise ValueError(f"elementwise expects matching shapes, got {a.shape} vs {b.shape}")
    if a.dtype != b.dtype:
        raise ValueError(f"dtype mismatch: {a.dtype} vs {b.dtype}")

    ctx = a.context
    kernel = _get_binary_kernel(ctx, a.dtype, expression)

    n = 1
    for d in a.shape:
        n *= d

    if out is None:
        out = Tensor.from_shape(a.queue, a.shape, dtype=a.dtype, pool=pool)
    else:
        if out.shape != a.shape or out.dtype != a.dtype:
            raise ValueError("output tensor shape/dtype mismatch")

    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(a.queue, gsize, lsize, a.buffer, b.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def relu(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    kernel = _get_unary_kernel(ctx, x.dtype, "RELU(v0)")
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    else:
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def bias_add(x: Tensor, bias: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    """
    Adds bias (shape [N]) to each row of x (shape [M,N]).
    """
    if cl is None:
        raise ImportError("pyopencl is required for bias_add")
    if len(x.shape) != 2 or len(bias.shape) != 1:
        raise ValueError("bias_add expects x: [M,N], bias: [N]")
    if x.shape[1] != bias.shape[0]:
        raise ValueError("bias dimension mismatch")
    if x.dtype != bias.dtype:
        raise ValueError("dtype mismatch")
    ctx = x.context
    dtype = x.dtype
    dtype_c = _DTYPE_CNAME.get(dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {dtype}")
    cache_key = (ctx.int_ptr, dtype, "bias_add")
    if cache_key in _KERNEL_CACHE:
        kernel = _KERNEL_CACHE[cache_key]
    else:
        body = """
        int gid = get_global_id(0);
        int col = gid % N;
        int row = gid / N;
        if (row < M) {
            out[gid] = x[gid] + bias[col];
        }
        """
        params = [
            f"__global const {dtype_c}* x",
            f"__global const {dtype_c}* bias",
            f"__global {dtype_c}* out",
            "const int M",
            "const int N",
        ]
        spec = KernelSpec(name="bias_add_kernel", params=params, body=body)
        program = cl.Program(ctx, spec.to_source()).build()
        kernel = getattr(program, spec.name)
        _KERNEL_CACHE[cache_key] = kernel

    M, N = x.shape
    total = M * N
    if out is None:
        out = Tensor.from_shape(x.queue, (M, N), dtype=dtype, pool=pool)
    gsize = (int(np.ceil(total / 256.0)) * 256,) if np is not None else (total,)
    lsize = (256,) if np is not None else None
    kernel(
        x.queue,
        gsize,
        lsize,
        x.buffer,
        bias.buffer,
        out.buffer,
        np.int32(M) if np is not None else M,
        np.int32(N) if np is not None else N,
    )  # type: ignore
    return out


def sigmoid(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    kernel = _get_unary_kernel(ctx, x.dtype, "1.0f / (1.0f + exp(-v0))")
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    else:
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def tanh(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    kernel = _get_unary_kernel(ctx, x.dtype, "tanh(v0)")
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    else:
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def leaky_relu(x: Tensor, negative_slope: float = 0.01, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = f"(v0 > 0 ? v0 : ({negative_slope}f * v0))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    else:
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def dropout(
    x: Tensor,
    p: float = 0.5,
    seed: Optional[int] = None,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    return_mask: bool = False,
    mask: Optional[Tensor] = None,
) -> Tensor | Tuple[Tensor, Tensor]:
    """
    Inference-safe dropout: if p==0 or None, returns input. Mask generated on host for simplicity.
    If return_mask=True, also returns the mask Tensor so callers (e.g., autograd) can reuse it in backward.
    """
    if p <= 0:
        if return_mask:
            ones = np.ones(x.shape, dtype=np.float32)
            mask_tensor = Tensor.from_host(x.queue, ones, dtype="float32")
            return x, mask_tensor
        return x
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for dropout")
    n = 1
    for d in x.shape:
        n *= d
    ctx = x.context
    mf = cl.mem_flags
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    if mask is None:
        rng = np.random.default_rng(seed)
        mask_host = (rng.random(n, dtype=np.float32) > p).astype(np.float32).reshape(x.shape)
        mask_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=mask_host)
        mask_tensor = Tensor(buffer=mask_buf, shape=x.shape, dtype="float32", context=ctx, queue=x.queue)
    else:
        mask_tensor = mask
        mask_buf = mask.buffer
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    cache_key = (ctx.int_ptr, x.dtype, "dropout")
    if cache_key in _KERNEL_CACHE:
        kernel = _KERNEL_CACHE[cache_key]
    else:
        expr = f"((float)mask[gid] * in0[gid]) / {(1.0 - p):.6f}"
        params = [
            f"__global const {dtype_c}* in0",
            "__global const float* mask",
            f"__global {dtype_c}* out",
            "const int n",
        ]
        body = """
        int gid = get_global_id(0);
        if (gid >= n) return;
        out[gid] = ((float)mask[gid]) * in0[gid];
        out[gid] = out[gid] / SCALE;
        """.replace("SCALE", f"{1.0 - p:.6f}")
        spec = KernelSpec(name="dropout_kernel", params=params, body=body)
        program = cl.Program(ctx, spec.to_source()).build()
        kernel = getattr(program, spec.name)
        _KERNEL_CACHE[cache_key] = kernel
    kernel(x.queue, gsize, lsize, x.buffer, mask_buf, out.buffer, np.int32(n))
    if return_mask:
        return out, mask_tensor
    return out


def gelu(x: Tensor, approximate: bool = True, out: Optional[Tensor] = None) -> Tensor:
    """
    GELU activation. approximate=True uses tanh approximation for speed.
    """
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    if approximate:
        expr = "0.5f * v0 * (1.0f + tanh(0.79788456f * (v0 + 0.044715f * v0 * v0 * v0)))"
    else:
        expr = "0.5f * v0 * (1.0f + erf(v0 / 1.41421356f))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def swish(x: Tensor, out: Optional[Tensor] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = "v0 / (1.0f + exp(-v0))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def elu(x: Tensor, alpha: float = 1.0, out: Optional[Tensor] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = f"(v0 > 0 ? v0 : ({alpha}f * (exp(v0) - 1.0f)))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def softplus(x: Tensor, out: Optional[Tensor] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = "log(1.0f + exp(v0))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def hard_sigmoid(x: Tensor, out: Optional[Tensor] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = "fmax(0.0f, fmin(1.0f, 0.2f * v0 + 0.5f))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def hard_swish(x: Tensor, out: Optional[Tensor] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = "(v0 * fmax(0.0f, fmin(1.0f, 0.2f * v0 + 0.5f)))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def clamp(x: Tensor, min_val: float, max_val: float, out: Optional[Tensor] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = f"fmin(fmax(v0, {min_val}f), {max_val}f)"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def hard_tanh(x: Tensor, min_val: float = -1.0, max_val: float = 1.0, out: Optional[Tensor] = None) -> Tensor:
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = f"(v0 < {min_val}f ? {min_val}f : (v0 > {max_val}f ? {max_val}f : v0))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def prelu(x: Tensor, alpha: Tensor, out: Optional[Tensor] = None) -> Tensor:
    """
    PReLU with channel-wise alpha (shape matches channel dimension for NCHW).
    """
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    N, C, H, W = x.shape
    if alpha.shape[0] != C:
        raise ValueError("alpha shape must match channels")
    ksrc = f"""
    __kernel void prelu(__global const {dtype_c}* x, __global const {dtype_c}* a, __global {dtype_c}* out,
                        const int C, const int H, const int W) {{
        int gid = get_global_id(0);
        int total = get_global_size(0);
        if (gid >= total) return;
        int w = gid % W;
        int h = (gid / W) % H;
        int c = (gid / (H*W)) % C;
        int n = gid / (C*H*W);
        int idx = ((n*C + c)*H + h)*W + w;
        float v = x[idx];
        float s = v > 0 ? v : a[c] * v;
        out[idx] = s;
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.prelu
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, alpha.buffer, out.buffer, np.int32(C), np.int32(H), np.int32(W))
    return out

"""
Conv2D forward/backward (NCHW) with stride and padding.
"""

from __future__ import annotations

import os
import time
from typing import Optional, Tuple

from netcl.core.tensor import Tensor
from netcl.core.memory import BufferPool
from netcl.ops.im2col import im2col, col2im
from netcl.ops.matmul import matmul as mm
from netcl.ops.transpose import transpose2d
from netcl.core.tensor import reshape as treshape

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

_DTYPE_CNAME = {"float": "float", "float32": "float", "half": "half", "float16": "half"}
_ENV_DEFAULT_ALGO = os.environ.get("NETCL_CONV_ALGO", "").lower()
_ENV_ENABLE_AUTO = os.environ.get("NETCL_CONV_AUTO", "1") not in ("0", "", "false", "False")
_ENV_AUTOTUNE = os.environ.get("NETCL_CONV_AUTOTUNE", "0") not in ("0", "", "false", "False")
_ENV_AUTOTUNE_WARMUP = int(os.environ.get("NETCL_CONV_AUTOTUNE_WARMUP", "2"))
_ENV_AUTOTUNE_RUNS = int(os.environ.get("NETCL_CONV_AUTOTUNE_RUNS", "3"))
_ENV_FORCE_AUTOTUNE = os.environ.get("NETCL_CONV_AUTOTUNE_FORCE", "0") not in ("0", "", "false", "False")
_TUNE_CACHE: dict = {}
_IN_TUNING = False
_HEUR_CACHE: dict = {}
_STRATEGY_CACHE: dict = {}
try:
    from netcl.core.capabilities import device_profile, kernel_strategy
except ImportError:  # pragma: no cover
    device_profile = None  # type: ignore
    kernel_strategy = None  # type: ignore


def conv2d_output_shape(
    x_shape: Tuple[int, int, int, int], w_shape: Tuple[int, int, int, int], stride: int = 1, pad: int = 0
) -> Tuple[int, int, int, int]:
    N, C, H, W = x_shape
    F, Cw, KH, KW = w_shape
    if C != Cw:
        raise ValueError("input and weight channel mismatch")
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W + 2 * pad - KW) // stride + 1
    return (N, F, OH, OW)


def _build_forward_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_fwd(__global const {dtype_c}* x, __global const {dtype_c}* w, __global const {dtype_c}* b, __global {dtype_c}* out,
                             const int N, const int C, const int H, const int W,
                             const int KH, const int KW, const int OH, const int OW, const int F,
                             const int stride, const int pad) {{
        int gid = get_global_id(0);
        int total = N * F * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int f = (gid / (OH * OW)) % F;
        int n = gid / (F * OH * OW);
        float acc = 0.0f;
        for (int c = 0; c < C; ++c) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += x[x_idx] * w[w_idx];
                }}
            }}
        }}
        if (b != 0) acc += b[f];
        out[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_fwd


def _build_forward_tiled_kernel(ctx: "cl.Context", dtype_c: str, tile_h: int = 8, tile_w: int = 8):
    src = f"""
    #define TILE_H {tile_h}
    #define TILE_W {tile_w}
    __kernel void conv2d_fwd_tiled(__global const {dtype_c}* x, __global const {dtype_c}* w, __global const {dtype_c}* b, __global {dtype_c}* out,
                                   const int N, const int C, const int H, const int W,
                                   const int KH, const int KW, const int OH, const int OW, const int F,
                                   const int stride, const int pad) {{
        int ow = get_global_id(0);
        int oh = get_global_id(1);
        int nf = get_global_id(2);
        if (ow >= OW || oh >= OH) return;
        int n = nf / F;
        int f = nf - n * F;
        if (n >= N) return;
        float acc = 0.0f;
        for (int c = 0; c < C; ++c) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += x[x_idx] * w[w_idx];
                }}
            }}
        }}
        if (b != 0) acc += b[f];
        int out_idx = ((n*F + f)*OH + oh)*OW + ow;
        out[out_idx] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_fwd_tiled


def _build_grad_input_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_grad_input(__global const {dtype_c}* grad_out, __global const {dtype_c}* w, __global {dtype_c}* grad_in,
                                    const int N, const int C, const int H, const int W,
                                    const int KH, const int KW, const int OH, const int OW, const int F,
                                    const int stride, const int pad) {{
        int gid = get_global_id(0);
        int total = N * C * H * W;
        if (gid >= total) return;
        int wcoord = gid % W;
        int hcoord = (gid / W) % H;
        int c = (gid / (H * W)) % C;
        int n = gid / (C * H * W);
        float acc = 0.0f;
        for (int f = 0; f < F; ++f) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int oh_num = hcoord + pad - kh;
                if (oh_num < 0) continue;
                if (oh_num % stride != 0) continue;
                int oh = oh_num / stride;
                if (oh < 0 || oh >= OH) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int ow_num = wcoord + pad - kw;
                    if (ow_num < 0) continue;
                    if (ow_num % stride != 0) continue;
                    int ow = ow_num / stride;
                    if (ow < 0 || ow >= OW) continue;
                    int go_idx = ((n*F + f)*OH + oh)*OW + ow;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += grad_out[go_idx] * w[w_idx];
                }}
            }}
        }}
        grad_in[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_input


def _build_grad_input_tiled_kernel(ctx: "cl.Context", dtype_c: str, tile_h: int = 8, tile_w: int = 8):
    src = f"""
    #define TILE_H {tile_h}
    #define TILE_W {tile_w}
    __kernel void conv2d_grad_input_tiled(__global const {dtype_c}* grad_out, __global const {dtype_c}* w, __global {dtype_c}* grad_in,
                                          const int N, const int C, const int H, const int W,
                                          const int KH, const int KW, const int OH, const int OW, const int F,
                                          const int stride, const int pad) {{
        int wcoord = get_global_id(0);
        int hcoord = get_global_id(1);
        int nc = get_global_id(2);
        if (wcoord >= W || hcoord >= H) return;
        int n = nc / C;
        int c = nc - n * C;
        if (n >= N) return;
        float acc = 0.0f;
        for (int f = 0; f < F; ++f) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int oh_num = hcoord + pad - kh;
                if (oh_num < 0) continue;
                if (oh_num % stride != 0) continue;
                int oh = oh_num / stride;
                if (oh < 0 || oh >= OH) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int ow_num = wcoord + pad - kw;
                    if (ow_num < 0) continue;
                    if (ow_num % stride != 0) continue;
                    int ow = ow_num / stride;
                    if (ow < 0 || ow >= OW) continue;
                    int go_idx = ((n*F + f)*OH + oh)*OW + ow;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += grad_out[go_idx] * w[w_idx];
                }}
            }}
        }}
        int out_idx = ((n*C + c)*H + hcoord)*W + wcoord;
        grad_in[out_idx] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_input_tiled


def _build_grad_weight_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_grad_weight(__global const {dtype_c}* x, __global const {dtype_c}* grad_out, __global {dtype_c}* grad_w,
                                     const int N, const int C, const int H, const int W,
                                     const int KH, const int KW, const int OH, const int OW, const int F,
                                     const int stride, const int pad) {{
        int gid = get_global_id(0);
        int total = F * C * KH * KW;
        if (gid >= total) return;
        int kw = gid % KW;
        int kh = (gid / KW) % KH;
        int c = (gid / (KH * KW)) % C;
        int f = gid / (C * KH * KW);
        float acc = 0.0f;
        for (int n = 0; n < N; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int ow = 0; ow < OW; ++ow) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int go_idx = ((n*F + f)*OH + oh)*OW + ow;
                    acc += x[x_idx] * grad_out[go_idx];
                }}
            }}
        }}
        grad_w[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_weight


def _build_grad_weight_tiled_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_grad_weight_tiled(__global const {dtype_c}* x, __global const {dtype_c}* grad_out, __global {dtype_c}* grad_w,
                                           const int N, const int C, const int H, const int W,
                                           const int KH, const int KW, const int OH, const int OW, const int F,
                                           const int stride, const int pad) {{
        int kw = get_global_id(0);
        int kh = get_global_id(1);
        int fc = get_global_id(2);
        if (kw >= KW || kh >= KH) return;
        int f = fc / C;
        int c = fc - f * C;
        if (f >= F || c >= C) return;
        float acc = 0.0f;
        for (int n = 0; n < N; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int ow = 0; ow < OW; ++ow) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int go_idx = ((n*F + f)*OH + oh)*OW + ow;
                    acc += x[x_idx] * grad_out[go_idx];
                }}
            }}
        }}
        int w_idx = ((f*C + c)*KH + kh)*KW + kw;
        grad_w[w_idx] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_weight_tiled


def _build_grad_bias_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_grad_bias(__global const {dtype_c}* grad_out, __global {dtype_c}* grad_b,
                                   const int N, const int F, const int OH, const int OW) {{
        int f = get_global_id(0);
        if (f >= F) return;
        float acc = 0.0f;
        for (int n = 0; n < N; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                for (int ow = 0; ow < OW; ++ow) {{
                    int idx = ((n*F + f)*OH + oh)*OW + ow;
                    acc += grad_out[idx];
                }}
            }}
        }}
        grad_b[f] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_bias


def _auto_select_algo(shape_info: Optional[Tuple[int, int, int, int, int, int, int, int, int]], stride: int, pad: int) -> str:
    """
    Very lightweight heuristic:
    - prefers tile for common 3x3 stride1 (pad 0/1) with moderate featuremaps
    - otherwise falls back to naive
    """
    if shape_info is None:
        return "naive"
    N, C, H, W, F, KH, KW, OH, OW = shape_info
    if KH == 3 and KW == 3 and stride == 1 and pad in (0, 1):
        area = OH * OW
        if F >= 16 and area >= 64:
            return "tile"
    return "naive"


def _autotune_algo(x: Tensor, w: Tensor, bias: Optional[Tensor], stride: int, pad: int, candidates: Tuple[str, ...]) -> str:
    key = (
        x.shape,
        w.shape,
        stride,
        pad,
        x.dtype,
        w.dtype,
    )
    if key in _TUNE_CACHE:
        return _TUNE_CACHE[key]
    global _IN_TUNING
    _IN_TUNING = True
    timings = []
    warmup = max(0, _ENV_AUTOTUNE_WARMUP)
    runs = max(1, _ENV_AUTOTUNE_RUNS)
    for algo in candidates:
        # warmup
        for _ in range(warmup):
            out = conv2d(x, w, bias=bias, stride=stride, pad=pad, algo=algo)  # type: ignore
            out.queue.finish()
        # timed runs
        t_min = 1e9
        for _ in range(runs):
            t0 = time.perf_counter()
            out = conv2d(x, w, bias=bias, stride=stride, pad=pad, algo=algo)  # type: ignore
            out.queue.finish()
            t1 = time.perf_counter()
            t_min = min(t_min, t1 - t0)
        timings.append((t_min, algo))
    _IN_TUNING = False
    best = min(timings, key=lambda p: p[0])[1]
    _TUNE_CACHE[key] = best
    return best


def _heuristic_algo(shape_info: Tuple[int, int, int, int, int, int, int, int, int], stride: int, pad: int, device_name: str) -> str:
    """
    Full heuristic keyed by shape/device. Prefers:
    - tile for typical 3x3 stride1 pad<=1 with moderate spatial size
    - im2col for larger channel/filter footprints
    - naive otherwise
    """
    key = (shape_info, stride, pad, device_name)
    if key in _HEUR_CACHE:
        return _HEUR_CACHE[key]
    N, C, H, W, F, KH, KW, OH, OW = shape_info
    area = OH * OW
    algo = "naive"
    if KH == 3 and KW == 3 and stride == 1 and pad in (0, 1) and F >= 16 and area >= 64:
        algo = "tile"
    elif (KH * KW >= 9 and C * KH * KW >= 64) or (F >= 32 and area >= 64):
        algo = "im2col"
    _HEUR_CACHE[key] = algo
    return algo


def _resolve_algo(
    algo: Optional[str],
    use_im2col: bool,
    shape_info: Optional[Tuple[int, int, int, int, int, int, int, int, int]],
    stride: int,
    pad: int,
    device_name: str,
    strategy: str,
) -> str:
    """
    Resolve algorithm name to an internal path flag.
    Supports "naive", "im2col", "tile" (forward). Unknown/experimental names fall back to "naive".
    """
    if algo:
        algo = algo.lower()
    if use_im2col and not algo:
        algo = "im2col"
    if not algo or algo == "":
        algo = _ENV_DEFAULT_ALGO or "auto"
    if algo == "auto":
        if _ENV_AUTOTUNE or _ENV_FORCE_AUTOTUNE:
            algo = "auto"  # leave for autotuner
        elif _ENV_ENABLE_AUTO and shape_info is not None:
            algo = _heuristic_algo(shape_info, stride, pad, device_name)
        else:
            algo = "naive"
    allowed = {"naive", "direct", "im2col"} if strategy == "portable" else {"naive", "direct", "im2col", "tile", "winograd", "fft"}
    if algo in allowed:
        return algo
    if algo == "auto":
        return "naive"
    # If user explicitly requested a non-portable algo, honor it (may be slower/unsafe on some devices)
    if algo in ("winograd", "fft", "tile"):
        return algo
    raise ValueError(f"unsupported conv2d algo: {algo}")


def conv2d(
    x: Tensor,
    w: Tensor,
    bias: Optional[Tensor] = None,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    stride: int = 1,
    pad: int = 0,
    use_im2col: bool = False,
    algo: Optional[str] = None,
    strategy: Optional[str] = None,
) -> Tensor:
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for conv2d")
    if x.dtype != w.dtype:
        raise ValueError(f"dtype mismatch: x {x.dtype} vs w {w.dtype}")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype for conv2d: {x.dtype}")
    # fp16 fallback to fp32 if device lacks fp16
    if x.dtype in ("half", "float16"):
        if "cl_khr_fp16" not in x.queue.device.extensions:
            # upcast to fp32 for compute
            x = Tensor.from_host(x.queue, x.to_host().astype(np.float32), dtype="float32")
            w = Tensor.from_host(w.queue, w.to_host().astype(np.float32), dtype="float32")
            if bias is not None:
                bias = Tensor.from_host(bias.queue, bias.to_host().astype(np.float32), dtype="float32")
            dtype_c = "float"
    N, C, H, W = x.shape
    F, Cw, KH, KW = w.shape
    if C != Cw:
        raise ValueError("channel mismatch")
    out_shape = conv2d_output_shape(x.shape, w.shape, stride=stride, pad=pad)
    OH, OW = out_shape[2], out_shape[3]
    ctx = x.context
    q = x.queue
    shape_info = (N, C, H, W, F, KH, KW, OH, OW)
    strategy = "optimized"
    if device_profile and kernel_strategy:
        dev = getattr(q, "device", None)
        if dev is not None:
            skey = getattr(dev, "hash", getattr(dev, "name", "unknown"))
            if skey in _STRATEGY_CACHE:
                strategy = _STRATEGY_CACHE[skey]
            else:
                prof = device_profile(dev)
                strategy = kernel_strategy(prof)
                _STRATEGY_CACHE[skey] = strategy
    if (_ENV_AUTOTUNE or _ENV_FORCE_AUTOTUNE) and not _IN_TUNING and (algo is None or algo == "" or algo == "auto"):
        algo_name = _autotune_algo(x, w, bias, stride, pad, candidates=("naive", "tile", "im2col"))
    else:
        device_name = getattr(q.device, "name", "unknown")
        algo_name = _resolve_algo(algo, use_im2col, shape_info, stride=stride, pad=pad, device_name=device_name, strategy=strategy)
    # log selection when env requests
    if _ENV_FORCE_AUTOTUNE:
        dn = getattr(q.device, "name", "unknown")
        print(f"[conv2d] strategy={strategy} algo={algo_name} device={dn}")
    if algo_name == "im2col":
        col, _ = im2col(x, KH, KW, stride=stride, pad=pad, pool=pool)
        col_flat = treshape(col, (N * OH * OW, C * KH * KW))
        w_flat = treshape(w, (F, C * KH * KW))
        w_flat_T = transpose2d(w_flat)
        out_col = mm(col_flat, w_flat_T)
        out_val_host = out_col.to_host().reshape(N, OH, OW, F).transpose(0, 3, 1, 2).copy()
        if out is None:
            out = Tensor.from_host(q, out_val_host.astype(np.float32))
        else:
            cl.enqueue_copy(q, out.buffer, out_val_host.astype(np.float32)).wait()
        if bias is not None:
            b_host = bias.to_host()
            out_host = out.to_host()
            out_host += b_host.reshape(1, F, 1, 1)
            cl.enqueue_copy(q, out.buffer, out_host).wait()
        return out
    elif algo_name == "tile":
        kernel = _build_forward_tiled_kernel(ctx, dtype_c)
        if out is None:
            out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
        gsize = (
            int(np.ceil(OW / 8.0)) * 8,
            int(np.ceil(OH / 8.0)) * 8,
            N * F,
        )
        lsize = (8, 8, 1)
        kernel(
            q,
            gsize,
            lsize,
            x.buffer,
            w.buffer,
            bias.buffer if bias is not None else None,
            out.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
        return out
    elif algo_name == "winograd":
        # Fallback until stable Winograd is in place
        return conv2d(x, w, bias=bias, out=out, pool=pool, stride=stride, pad=pad, algo="naive")
    elif algo_name == "fft":
        if np is None:
            raise ImportError("numpy required for fft path")
        if stride != 1:
            return conv2d(x, w, bias=bias, out=out, pool=pool, stride=stride, pad=pad, algo="naive")
        xh = x.to_host()
        wh = w.to_host()
        pad_effective = pad
        x_pad = np.pad(xh, ((0, 0), (0, 0), (pad_effective, pad_effective), (pad_effective, pad_effective)), mode="constant")
        H_pad, W_pad = x_pad.shape[2], x_pad.shape[3]
        fft_shape = (H_pad, W_pad)
        fft_x = np.fft.rfftn(x_pad, s=fft_shape, axes=(2, 3))
        # pad weights to fft_shape
        w_pad = np.zeros((F, C, H_pad, W_pad), dtype=np.float32)
        w_pad[:, :, :KH, :KW] = wh
        fft_w = np.fft.rfftn(w_pad, s=fft_shape, axes=(2, 3))
        out_freq = (fft_x[:, None, :, :, :] * np.conj(fft_w[None, :, :, :, :])).sum(axis=2)
        out_spatial = np.fft.irfftn(out_freq, s=fft_shape, axes=(2, 3)).real
        out_host = out_spatial[:, :, :OH, :OW].astype(np.float32)
        if bias is not None:
            out_host += bias.to_host().reshape(1, F, 1, 1)
        if out is None:
            out = Tensor.from_host(q, out_host)
        else:
            cl.enqueue_copy(q, out.buffer, out_host).wait()
        return out
    else:
        kernel = _build_forward_kernel(ctx, dtype_c)
        if out is None:
            out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
        total = int(np.prod(out_shape))
        gsize = (int(np.ceil(total / 256.0)) * 256,)
        kernel(
            q,
            gsize,
            (256,),
            x.buffer,
            w.buffer,
            bias.buffer if bias is not None else None,
            out.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
        return out


def conv2d_backward(
    x: Tensor,
    w: Tensor,
    grad_out: Tensor,
    bias: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    stride: int = 1,
    pad: int = 0,
    use_im2col: bool = False,
    algo: Optional[str] = None,
) -> tuple[Tensor, Tensor, Optional[Tensor]]:
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for conv2d backward")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError("unsupported dtype")
    N, C, H, W = x.shape
    F, _, KH, KW = w.shape
    _, _, OH, OW = grad_out.shape
    ctx = x.context
    q = x.queue
    shape_info = (N, C, H, W, F, KH, KW, OH, OW)
    device_name = getattr(q.device, "name", "unknown")
    strategy = "optimized"
    if device_profile and kernel_strategy:
        dev = getattr(q, "device", None)
        if dev is not None:
            skey = getattr(dev, "hash", getattr(dev, "name", "unknown"))
            if skey in _STRATEGY_CACHE:
                strategy = _STRATEGY_CACHE[skey]
            else:
                prof = device_profile(dev)
                strategy = kernel_strategy(prof)
                _STRATEGY_CACHE[skey] = strategy
    if _ENV_AUTOTUNE and not _IN_TUNING and (algo is None or algo == "" or algo == "auto"):
        key = (x.shape, w.shape, stride, pad, x.dtype, w.dtype)
        algo_name = _TUNE_CACHE.get(
            key, _resolve_algo(algo, use_im2col, shape_info, stride=stride, pad=pad, device_name=device_name, strategy=strategy)
        )
    else:
        algo_name = _resolve_algo(algo, use_im2col, shape_info, stride=stride, pad=pad, device_name=device_name, strategy=strategy)
    if algo_name == "im2col":
        col, _ = im2col(x, KH, KW, stride=stride, pad=pad, pool=pool)
        col_flat = treshape(col, (N * OH * OW, C * KH * KW))
        w_flat = treshape(w, (F, C * KH * KW))
        go_host = grad_out.to_host().transpose(0, 2, 3, 1).reshape(N * OH * OW, F)
        go_flat = Tensor.from_host(q, go_host.astype(np.float32))
        # grad_w = col^T @ grad_out => shape (C*KH*KW, F)
        col_T = transpose2d(col_flat)
        grad_w_flat = mm(col_T, go_flat)
        grad_w_host = grad_w_flat.to_host().reshape(C * KH * KW, F).T.reshape(w.shape)
        grad_w = Tensor.from_host(q, np.ascontiguousarray(grad_w_host.astype(np.float32)))
        # grad_in: grad_out @ w_flat -> col2im
        go_w = mm(go_flat, w_flat)  # (N*OH*OW, C*KH*KW)
        grad_col_host = go_w.to_host().reshape(N, OH, OW, C * KH * KW)
        grad_col = Tensor.from_host(q, grad_col_host.astype(np.float32))
        grad_in = col2im(grad_col, (N, C, H, W), KH, KW, stride=stride, pad=pad, pool=pool)
    elif algo_name == "tile":
        grad_in = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
        kernel_in = _build_grad_input_tiled_kernel(ctx, dtype_c)
        gsize_in = (
            int(np.ceil(W / 8.0)) * 8,
            int(np.ceil(H / 8.0)) * 8,
            N * C,
        )
        lsize_in = (8, 8, 1)
        kernel_in(
            q,
            gsize_in,
            lsize_in,
            grad_out.buffer,
            w.buffer,
            grad_in.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
        grad_w = Tensor.from_shape(q, w.shape, dtype=w.dtype, pool=pool)
        kernel_w = _build_grad_weight_tiled_kernel(ctx, dtype_c)
        gsize_w = (
            int(np.ceil(KW / 4.0)) * 4,
            int(np.ceil(KH / 4.0)) * 4,
            F * C,
        )
        lsize_w = (4, 4, 1)
        kernel_w(
            q,
            gsize_w,
            lsize_w,
            x.buffer,
            grad_out.buffer,
            grad_w.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
    else:
        # grad_input
        grad_in = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
        kernel_in = _build_grad_input_kernel(ctx, dtype_c)
        total_in = N * C * H * W
        gsize_in = (int(np.ceil(total_in / 256.0)) * 256,)
        kernel_in(
            q,
            gsize_in,
            (256,),
            grad_out.buffer,
            w.buffer,
            grad_in.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
        # grad_weight
        grad_w = Tensor.from_shape(q, w.shape, dtype=w.dtype, pool=pool)
        kernel_w = _build_grad_weight_kernel(ctx, dtype_c)
        total_w = F * C * KH * KW
        gsize_w = (int(np.ceil(total_w / 256.0)) * 256,)
        kernel_w(
            q,
            gsize_w,
            (256,),
            x.buffer,
            grad_out.buffer,
            grad_w.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
    grad_b_out = None
    if bias is not None:
        grad_b_out = Tensor.from_shape(q, bias.shape, dtype=bias.dtype, pool=pool)
        kernel_b = _build_grad_bias_kernel(ctx, dtype_c)
        gsize_b = (int(np.ceil(F / 256.0)) * 256,)
        kernel_b(q, gsize_b, (256,), grad_out.buffer, grad_b_out.buffer, np.int32(N), np.int32(F), np.int32(OH), np.int32(OW))
    return grad_in, grad_w, grad_b_out

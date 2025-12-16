from __future__ import annotations

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor
from netcl.core.parameter import Parameter
from netcl.nn.layers import Module
from netcl.core.device import manager

_DTYPE_CNAME = {"float": "float", "float32": "float", "half": "float", "float16": "float"}


def _build_bn_forward(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void bn_forward(__global const {dtype_c}* x, __global const {dtype_c}* gamma, __global const {dtype_c}* beta,
                             __global const {dtype_c}* mean, __global const {dtype_c}* var, __global {dtype_c}* out,
                             const int C, const int H, const int W, const float eps) {{
        int gid = get_global_id(0);
        int total = get_global_size(0);
        int idx = gid;
        if (idx >= total) return;
        int w = idx % W;
        int h = (idx / W) % H;
        int c = (idx / (H*W)) % C;
        int n = idx / (C*H*W);
        int offset = ((n*C + c)*H + h)*W + w;
        float m = mean[c];
        float v = var[c];
        float inv = rsqrt(v + eps);
        float xn = (x[offset] - m) * inv;
        out[offset] = xn * gamma[c] + beta[c];
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.bn_forward


def _build_bn_backward(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void bn_backward(__global const {dtype_c}* x, __global const {dtype_c}* grad_out,
                              __global const {dtype_c}* gamma, __global const {dtype_c}* mean, __global const {dtype_c}* var,
                              __global {dtype_c}* grad_x, __global {dtype_c}* grad_gamma, __global {dtype_c}* grad_beta,
                              const int N, const int C, const int H, const int W, const float eps) {{
        int c = get_global_id(0);
        if (c >= C) return;
        float m = mean[c];
        float v = var[c];
        float inv = rsqrt(v + eps);
        float dgamma = 0.0f;
        float dbeta = 0.0f;
        int spatial = H * W;
        int NHW = N * spatial;
        // accumulate grad_gamma, grad_beta
        for (int n = 0; n < N; ++n) {{
            for (int s = 0; s < spatial; ++s) {{
                int offset = ((n*C + c)*spatial) + s;
                float xn = (x[offset] - m) * inv;
                float go = grad_out[offset];
                dgamma += go * xn;
                dbeta += go;
            }}
        }}
        grad_gamma[c] = dgamma;
        grad_beta[c] = dbeta;
        // grad_x
        for (int n = 0; n < N; ++n) {{
            for (int s = 0; s < spatial; ++s) {{
                int offset = ((n*C + c)*spatial) + s;
                float go = grad_out[offset];
                float xmu = x[offset] - m;
                // simplified BN backward per channel
                float dvar = -0.5f * go * gamma[c] * xmu * powr(v + eps, -1.5f);
                float dmean = -go * gamma[c] * inv;
                float dx = go * gamma[c] * inv;
                dx += dvar * 2.0f * xmu / (float)NHW;
                dx += dmean / (float)NHW;
                grad_x[offset] = dx;
            }}
        }}
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.bn_backward


def _compute_stats_device(x: Tensor):
    """
    Compute mean and variance per channel on device: returns (mean Tensor, var Tensor).
    """
    ctx = x.context
    q = x.queue
    dtype_c = _DTYPE_CNAME[x.dtype]
    N, C, H, W = x.shape
    spatial = H * W
    total = N * spatial
    ksrc = f"""
    __kernel void bn_stats(__global const {dtype_c}* x, __global {dtype_c}* mean, __global {dtype_c}* var,
                           const int N, const int C, const int H, const int W) {{
        int c = get_global_id(0);
        if (c >= C) return;
        float m = 0.0f;
        float sq = 0.0f;
        int spatial = H * W;
        int count = N * spatial;
        for (int n = 0; n < N; ++n) {{
            for (int s = 0; s < spatial; ++s) {{
                int idx = ((n*C + c)*spatial) + s;
                float v = x[idx];
                m += v;
                sq += v * v;
            }}
        }}
        m = m / (float)count;
        float v = sq / (float)count - m * m;
        mean[c] = m;
        var[c] = v;
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.bn_stats
    mean = Tensor.from_shape(q, (C,), dtype=x.dtype)
    var = Tensor.from_shape(q, (C,), dtype=x.dtype)
    gsize = (int(np.ceil(C / 256.0)) * 256,)
    kernel(q, gsize, (256,), x.buffer, mean.buffer, var.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return mean, var


def batch_norm2d(x: Tensor, gamma: Tensor, beta: Tensor, running_mean: Tensor, running_var: Tensor, momentum: float = 0.1, eps: float = 1e-5, training: bool = True):
    """
    BatchNorm2d for NCHW. running_mean/var are 1D (C,).
    Stats computed on device; running stats updated on host.
    """
    if x.dtype not in ("float32", "float", "half", "float16"):
        raise ValueError("batch_norm2d supports float32/float16")
    N, C, H, W = x.shape
    ctx = x.context
    q = x.queue
    # fp16: upcast inputs/params to fp32 for stats + forward, cast output back
    cast_back = False
    if x.dtype in ("half", "float16"):
        cast_back = True
        x = Tensor.from_host(q, x.to_host().astype(np.float32))
        gamma = Tensor.from_host(q, gamma.to_host().astype(np.float32))
        beta = Tensor.from_host(q, beta.to_host().astype(np.float32))
    dtype_c = _DTYPE_CNAME[x.dtype if not cast_back else "float32"]
    if training:
        mean, var = _compute_stats_device(x)
        rm = running_mean.to_host()
        rv = running_var.to_host()
        rm = (1 - momentum) * rm + momentum * mean.to_host()
        rv = (1 - momentum) * rv + momentum * var.to_host()
        cl.enqueue_copy(q, running_mean.buffer, rm).wait()
        cl.enqueue_copy(q, running_var.buffer, rv).wait()
    else:
        mean = running_mean
        var = running_var
    out = Tensor.from_shape(q, x.shape, dtype=x.dtype)
    kernel = _build_bn_forward(ctx, dtype_c)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(q, gsize, (256,), x.buffer, gamma.buffer, beta.buffer, mean.buffer, var.buffer, out.buffer, np.int32(C), np.int32(H), np.int32(W), np.float32(eps))
    if cast_back:
        out_fp16 = Tensor.from_host(q, out.to_host().astype(np.float16), dtype="float16")
        return out_fp16, mean, var
    return out, mean, var


def batch_norm2d_backward(x: Tensor, gamma: Tensor, grad_out: Tensor, mean: Tensor, var: Tensor, eps: float = 1e-5):
    if x.dtype not in ("float32", "float", "half", "float16"):
        raise ValueError("batch_norm2d backward supports float32/float16")
    N, C, H, W = x.shape
    ctx = x.context
    q = x.queue
    cast_back = False
    if x.dtype in ("half", "float16"):
        cast_back = True
        x = Tensor.from_host(q, x.to_host().astype(np.float32))
        gamma = Tensor.from_host(q, gamma.to_host().astype(np.float32))
        grad_out = Tensor.from_host(q, grad_out.to_host().astype(np.float32))
    dtype_c = _DTYPE_CNAME[x.dtype if not cast_back else "float32"]
    grad_x = Tensor.from_shape(q, x.shape, dtype=x.dtype)
    grad_gamma = Tensor.from_shape(q, (C,), dtype=x.dtype)
    grad_beta = Tensor.from_shape(q, (C,), dtype=x.dtype)
    kernel = _build_bn_backward(ctx, dtype_c)
    gsize = (int(np.ceil(C / 256.0)) * 256,)
    kernel(q, gsize, (256,), x.buffer, grad_out.buffer, gamma.buffer, mean.buffer, var.buffer, grad_x.buffer, grad_gamma.buffer, grad_beta.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.float32(eps))
    if cast_back:
        grad_x = Tensor.from_host(q, grad_x.to_host().astype(np.float16), dtype="float16")
        grad_gamma = Tensor.from_host(q, grad_gamma.to_host().astype(np.float32))
        grad_beta = Tensor.from_host(q, grad_beta.to_host().astype(np.float32))
    return grad_x, grad_gamma, grad_beta


class BatchNorm2dModule(Module):
    """
    Stateful BatchNorm2d layer holding running_mean/running_var and gamma/beta parameters.
    """

    def __init__(self, queue=None, num_features: int = None, momentum: float = 0.1, eps: float = 1e-5, device: str | None = None):
        if queue is None:
            dev = manager.default()
            if dev is None:
                raise RuntimeError("No OpenCL device available")
            queue = dev.queue
        self.gamma = Parameter.from_host(queue, np.ones((num_features,), dtype=np.float32))
        self.beta = Parameter.from_host(queue, np.zeros((num_features,), dtype=np.float32))
        self.running_mean = Tensor.from_host(queue, np.zeros((num_features,), dtype=np.float32))
        self.running_var = Tensor.from_host(queue, np.ones((num_features,), dtype=np.float32))
        self.momentum = momentum
        self.eps = eps
        self.training = True

    def __call__(self, x, **kwargs):
        return self.forward(x)

    def forward(self, x):
        # Autograd-Pfad, wenn Node übergeben
        if hasattr(x, "value"):
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            g_node = ag.tensor(self.gamma, requires_grad=True)
            b_node = ag.tensor(self.beta, requires_grad=True)
            out = ag.batch_norm2d(
                x_node,
                g_node,
                b_node,
                self.running_mean,
                self.running_var,
                training=self.training,
            )
            return out
        return batch_norm2d(x, self.gamma, self.beta, self.running_mean, self.running_var, momentum=self.momentum, eps=self.eps, training=self.training)[0]

    def parameters(self):
        return [self.gamma, self.beta]

    def state_dict(self):
        return {
            "gamma": self.gamma.to_host(),
            "beta": self.beta.to_host(),
            "running_mean": self.running_mean.to_host(),
            "running_var": self.running_var.to_host(),
            "momentum": self.momentum,
            "eps": self.eps,
        }

    def load_state_dict(self, state: dict):
        import pyopencl as cl

        q = self.gamma.queue
        cl.enqueue_copy(q, self.gamma.buffer, state["gamma"]).wait()
        cl.enqueue_copy(q, self.beta.buffer, state["beta"]).wait()
        cl.enqueue_copy(q, self.running_mean.buffer, state["running_mean"]).wait()
        cl.enqueue_copy(q, self.running_var.buffer, state["running_var"]).wait()
        self.momentum = state.get("momentum", self.momentum)
        self.eps = state.get("eps", self.eps)

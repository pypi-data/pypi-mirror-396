"""
Autograd-enabled wrappers for core ops.
"""

from __future__ import annotations

import numpy as np
from typing import Optional

from netcl.autograd.engine import Node, apply_op
from netcl.core.tensor import Tensor, reshape as tensor_reshape
from netcl.amp import autocast, maybe_cast_tensor
from netcl.ops import (
    matmul,
    elementwise_binary,
    relu as relu_op,
    bias_add as bias_add_op,
    sigmoid as sigmoid_op,
    tanh as tanh_op,
    leaky_relu as leaky_relu_op,
    prelu as prelu_op,
    gelu as gelu_op,
    swish as swish_op,
    elu as elu_op,
    softplus as softplus_op,
    hard_sigmoid as hard_sigmoid_op,
    hard_swish as hard_swish_op,
    clamp as clamp_op,
    hard_tanh as hard_tanh_op,
    depthwise_conv2d as dw_conv2d_op,
    depthwise_conv2d_backward as dw_conv2d_bwd,
    softmax as softmax_op,
    max_pool2d as max_pool2d_op,
    max_pool2d_backward as max_pool2d_bwd,
    dropout as dropout_op,
    avg_pool2d as avg_pool2d_op,
    avg_pool2d_backward as avg_pool2d_bwd,
    transpose2d,
    broadcast_binary as bcast_bin,
    conv_transpose2d as conv_transpose2d_op,
)


def tensor(x: Tensor, requires_grad: bool = False) -> Node:
    return Node(value=maybe_cast_tensor(x), requires_grad=requires_grad)


def add(a: Node, b: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # broadcast-aware: grad for broadcasted arg needs reduction; for now rely on broadcast kernel producing full shape for both
        return [grad_out, grad_out]

    # If shapes match, use elementwise; else broadcast kernel
    if a.value.shape == b.value.shape:
        return apply_op(lambda x, y: elementwise_binary(x, y, expression="ADD(v0, v1)"), grad_fn, a, b, tape=tape)
    else:
        return apply_op(lambda x, y: bcast_bin(x, y, op="ADD"), grad_fn, a, b, tape=tape)


def relu(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # grad = grad_out * (x > 0)
        from netcl.ops.elementwise import elementwise_binary
        mask = elementwise_binary(x.value, x.value, expression="(v0 > 0 ? 1 : 0)")
        return [elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")]

    return apply_op(lambda t: relu_op(t), grad_fn, x, tape=tape)


def bias_add(x: Node, bias: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # dL/dx = grad_out ; dL/db = reduce over rows
        from netcl.ops.reduction import reduce_sum

        db = reduce_sum(grad_out, axis=0)
        return [grad_out, db]

    return apply_op(lambda a, b: bias_add_op(a, b), grad_fn, x, bias, tape=tape)


def matmul_op(a: Node, b: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # dA = grad_out @ B^T ; dB = A^T @ grad_out (all device-side)
        from netcl.ops.matmul import matmul as mm

        a_shape = a.value.shape
        b_shape = b.value.shape
        if len(a_shape) != 2 or len(b_shape) != 2:
            raise ValueError("matmul grad expects 2D tensors")
        b_T = transpose2d(b.value)
        a_T = transpose2d(a.value)
        dA = mm(grad_out, b_T)
        dB = mm(a_T, grad_out)
        return [dA, dB]

    return apply_op(lambda x, y: matmul(x, y), grad_fn, a, b, tape=tape)


def conv2d(x: Node, w: Node, bias: Optional[Node] = None, stride: int = 1, pad: int = 0, algo: Optional[str] = None, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        from netcl.ops.conv2d import conv2d_backward

        grad_x, grad_w, grad_b = conv2d_backward(
            x.value, w.value, grad_out, bias.value if bias else None, stride=stride, pad=pad, algo=algo
        )
        return [grad_x, grad_w, grad_b] if bias is not None else [grad_x, grad_w]

    from netcl.ops.conv2d import conv2d as conv2d_fwd

    fn = lambda a, b, c=None: conv2d_fwd(a, b, c, stride=stride, pad=pad, algo=algo)
    args = (x, w, bias) if bias is not None else (x, w)
    return apply_op(fn, grad_fn, *args, tape=tape)


def flatten(x: Node, shape: Tuple[int, ...], tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # reshape back to input shape
        return [tensor_reshape(grad_out, x.value.shape)]

    return apply_op(lambda t: tensor_reshape(t, shape), grad_fn, x, tape=tape)


def max_pool2d(x: Node, kernel_size: int = 2, stride: int = 2, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        grad_x = max_pool2d_bwd(x.value, grad_out, kernel_size=kernel_size, stride=stride)
        return [grad_x]

    return apply_op(lambda t: max_pool2d_op(t, kernel_size=kernel_size, stride=stride), grad_fn, x, tape=tape)


def avg_pool2d(x: Node, kernel_size: int = 2, stride: int = 2, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        grad_x = avg_pool2d_bwd(x.value, grad_out, kernel_size=kernel_size, stride=stride)
        return [grad_x]

    return apply_op(lambda t: avg_pool2d_op(t, kernel_size=kernel_size, stride=stride), grad_fn, x, tape=tape)


def dropout(x: Node, p: float = 0.5, seed: Optional[int] = None, tape=None) -> Node:
    """
    Dropout with saved mask for backward: grad = grad_out * mask / (1-p).
    """
    mask_holder: dict = {}

    def forward(t: Tensor) -> Tensor:
        out, mask = dropout_op(t, p=p, seed=seed, return_mask=True)
        mask_holder["mask"] = mask
        return out

    def grad_fn(grad_out: Tensor):
        mask = mask_holder.get("mask")
        if mask is None:
            raise RuntimeError("dropout mask missing for backward")
        scale = 1.0 / (1.0 - p) if p < 1 else 0.0
        grad = elementwise_binary(grad_out, mask, expression=f"MUL(v0, {scale})")
        return [grad]

    return apply_op(forward, grad_fn, x, tape=tape)


def sigmoid(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        y = sigmoid_op(x.value)
        y1 = elementwise_binary(y, y, expression="MUL(v0, (1.0f - v1))")  # y * (1 - y)
        grad = elementwise_binary(grad_out, y1, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: sigmoid_op(t), grad_fn, x, tape=tape)


def tanh(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        y = tanh_op(x.value)
        y_sq = elementwise_binary(y, y, expression="MUL(v0, v1)")
        one_minus = elementwise_binary(y_sq, y_sq, expression="SUB(1.0f, v0)")
        grad = elementwise_binary(grad_out, one_minus, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: tanh_op(t), grad_fn, x, tape=tape)

def gelu(x: Node, approximate: bool = True, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # Approximate grad via finite difference on host for now
        y = gelu_op(x.value, approximate=approximate)
        # derivative approx: y' ~ 0.5*(1 + erf(x/sqrt(2))) + x * pdf
        import numpy as np

        xh = x.value.to_host()
        if approximate:
            t = 0.79788456 * (xh + 0.044715 * np.power(xh, 3))
            sech2 = 1 / np.cosh(t) ** 2
            dy = 0.5 * (1 + np.tanh(t)) + 0.5 * xh * (1 - np.tanh(t) ** 2) * 0.79788456 * (1 + 0.134145 * xh * xh)
        else:
            from math import erf, sqrt, exp
            dy = 0.5 * (1 + np.array([erf(v / sqrt(2)) for v in xh.flatten()])).reshape(xh.shape) + xh * np.exp(-xh * xh / 2) / np.sqrt(2 * np.pi)
        dy_t = Tensor.from_host(x.value.queue, dy.astype(np.float32))
        grad = elementwise_binary(grad_out, dy_t, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: gelu_op(t, approximate=approximate), grad_fn, x, tape=tape)


def swish(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        sig = sigmoid_op(x.value)
        term = elementwise_binary(sig, x.value, expression="ADD(v0, MUL(v1, SUB(1.0f, v0)))")  # sig + x*sig*(1-sig)
        grad = elementwise_binary(grad_out, term, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: swish_op(t), grad_fn, x, tape=tape)


def elu(x: Node, alpha: float = 1.0, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        from netcl.ops.elementwise import elementwise_binary
        expx = elementwise_binary(x.value, x.value, expression="EXP(v0)")
        mask = elementwise_binary(x.value, x.value, expression="(v0 > 0 ? 1.0f : 0.0f)")
        neg_mask = elementwise_binary(x.value, x.value, expression="(v0 <= 0 ? 1.0f : 0.0f)")
        left = mask
        right = elementwise_binary(expx, expx, expression=f"MUL(v0, {alpha}f)")
        right = elementwise_binary(right, neg_mask, expression="MUL(v0, v1)")
        grad = elementwise_binary(left, right, expression="ADD(v0, v1)")
        grad = elementwise_binary(grad_out, grad, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: elu_op(t, alpha=alpha), grad_fn, x, tape=tape)


def softplus(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        sig = sigmoid_op(x.value)
        grad = elementwise_binary(grad_out, sig, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: softplus_op(t), grad_fn, x, tape=tape)


def hard_sigmoid(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        mask = elementwise_binary(x.value, x.value, expression="(v0 > -2.5f && v0 < 2.5f ? 0.2f : 0.0f)")
        grad = elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: hard_sigmoid_op(t), grad_fn, x, tape=tape)


def hard_swish(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # derivative of x * relu6(x+3)/6
        mask = elementwise_binary(x.value, x.value, expression="(v0 > -3 && v0 < 3 ? 1.0f : 0.0f)")
        relu6 = elementwise_binary(x.value, x.value, expression="fmax(0.0f, fmin(6.0f, v0 + 3.0f))")
        term = elementwise_binary(relu6, mask, expression="MUL(v0, v1)")
        term = elementwise_binary(term, term, expression="MUL(v0, 1.0f/6.0f)")
        add = elementwise_binary(mask, relu6, expression="MUL(v0, v1)")
        add = elementwise_binary(add, add, expression="MUL(v0, 1.0f/6.0f)")
        grad = elementwise_binary(term, add, expression="ADD(v0, v1)")
        grad = elementwise_binary(grad_out, grad, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: hard_swish_op(t), grad_fn, x, tape=tape)


def clamp(x: Node, min_val: float, max_val: float, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        mask = elementwise_binary(x.value, x.value, expression=f"(v0 >= {min_val}f && v0 <= {max_val}f ? 1.0f : 0.0f)")
        grad = elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: clamp_op(t, min_val, max_val), grad_fn, x, tape=tape)


def hard_tanh(x: Node, min_val: float = -1.0, max_val: float = 1.0, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        mask = elementwise_binary(x.value, x.value, expression=f"(v0 >= {min_val}f && v0 <= {max_val}f ? 1.0f : 0.0f)")
        grad = elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")
        return [grad]

    return apply_op(lambda t: hard_tanh_op(t, min_val=min_val, max_val=max_val), grad_fn, x, tape=tape)


def depthwise_conv2d(x: Node, w: Node, bias: Optional[Node] = None, stride: int = 1, pad: int = 0, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        gx, gw, gb = dw_conv2d_bwd(x.value, w.value, grad_out, bias.value if bias else None, stride=stride, pad=pad)
        return [gx, gw, gb] if bias is not None else [gx, gw]

    fn = lambda a, b, c=None: dw_conv2d_op(a, b, c, stride=stride, pad=pad)
    args = (x, w, bias) if bias is not None else (x, w)
    return apply_op(fn, grad_fn, *args, tape=tape)


def conv_transpose2d(x: Node, w: Node, bias: Optional[Node] = None, stride: int = 1, pad: int = 0, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        from netcl.ops.conv_transpose2d import conv_transpose2d_backward as ct_bwd

        gx, gw, gb = ct_bwd(x.value, w.value, grad_out, bias.value if bias else None, stride=stride, pad=pad)
        return [gx, gw, gb] if bias is not None else [gx, gw]

    fn = lambda a, b, c=None: conv_transpose2d_op(a, b, c, stride=stride, pad=pad)
    args = (x, w, bias) if bias is not None else (x, w)
    return apply_op(fn, grad_fn, *args, tape=tape)


def prelu(x: Node, alpha: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # grad_x = grad_out * (x>0 ? 1 : alpha)
        pos_mask = elementwise_binary(x.value, x.value, expression="(v0 > 0 ? 1.0f : 0.0f)")
        neg_mask = elementwise_binary(x.value, x.value, expression="(v0 <= 0 ? 1.0f : 0.0f)")
        alpha_broadcast = alpha.value  # shape [C]
        # multiply grad_out by appropriate slope
        grad_pos = elementwise_binary(grad_out, pos_mask, expression="MUL(v0, v1)")
        # For neg, need per-channel alpha; approximate by host multiply
        go_host = grad_out.to_host()
        xh = x.value.to_host()
        ah = alpha.value.to_host()
        N, C, H, W = x.value.shape
        gradx = go_host.copy()
        grad_alpha = np.zeros_like(ah, dtype=np.float32)
        for n in range(N):
            for c in range(C):
                mask = xh[n, c] <= 0
                gradx[n, c][mask] *= ah[c]
                grad_alpha[c] += np.sum(go_host[n, c][mask] * xh[n, c][mask])
        from netcl.core.tensor import Tensor as T

        grad_x_t = T.from_host(x.value.queue, gradx.astype(np.float32))
        grad_alpha_t = T.from_host(alpha.value.queue, grad_alpha.astype(np.float32))
        return [grad_x_t, grad_alpha_t]

    return apply_op(lambda t, a: prelu_op(t, a), grad_fn, x, alpha, tape=tape)


def batch_norm2d(x: Node, gamma: Node, beta: Node, running_mean: Tensor, running_var: Tensor, momentum: float = 0.1, eps: float = 1e-5, training: bool = True, tape=None) -> Node:
    """
    BatchNorm2d autograd wrapper. running_mean/var are Tensors (no grad). Returns normalized output; saves mean/var for backward.
    """
    cache: dict = {}

    def forward(x_t: Tensor, g_t: Tensor, b_t: Tensor) -> Tensor:
        out, mean, var = bn2d_fwd(x_t, g_t, b_t, running_mean, running_var, momentum=momentum, eps=eps, training=training)
        cache["mean"] = mean
        cache["var"] = var
        return out

    def grad_fn(grad_out: Tensor):
        mean = cache.get("mean")
        var = cache.get("var")
        if mean is None or var is None:
            raise RuntimeError("batch_norm2d backward missing mean/var")
        gx, ggamma, gbeta = bn2d_bwd(x.value, gamma.value, grad_out, mean, var, eps=eps)
        return [gx, ggamma, gbeta]

    return apply_op(forward, grad_fn, x, gamma, beta, tape=tape)


def layer_norm(x: Node, gamma: Node, beta: Node, eps: float = 1e-5, tape=None) -> Node:
    cache: dict = {}

    def forward(x_t: Tensor, g_t: Tensor, b_t: Tensor) -> Tensor:
        out, mean, var = ln_fwd(x_t, g_t, b_t, eps=eps)
        cache["mean"] = mean
        cache["var"] = var
        return out

    def grad_fn(grad_out: Tensor):
        mean = cache.get("mean")
        var = cache.get("var")
        gx, ggamma, gbeta = ln_bwd(x.value, gamma.value, grad_out, mean, var, eps=eps)
        return [gx, ggamma, gbeta]

    return apply_op(forward, grad_fn, x, gamma, beta, tape=tape)


def pad2d(x: Node, pad: int = 1, mode: str = "zero", tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # simple unpad: crop grad_out back to input shape
        gh = grad_out.shape[2]
        gw = grad_out.shape[3]
        # copy slice to host then back (simple but not ideal)
        go_host = grad_out.to_host()
        cropped = go_host[:, :, pad : gh - pad, pad : gw - pad]
        return [Tensor.from_host(grad_out.queue, cropped.astype(np.float32))]

    return apply_op(lambda t: pad2d_op(t, pad=pad, mode=mode), grad_fn, x, tape=tape)


def group_norm(x: Node, gamma: Node, beta: Node, groups: int, eps: float = 1e-5, tape=None) -> Node:
    cache: dict = {}

    def forward(x_t: Tensor, g_t: Tensor, b_t: Tensor) -> Tensor:
        out, mean, var = gn_fwd(x_t, g_t, b_t, groups=groups, eps=eps)
        cache["mean"] = mean
        cache["var"] = var
        return out

    def grad_fn(grad_out: Tensor):
        mean = cache.get("mean")
        var = cache.get("var")
        gx, ggamma, gbeta = gn_bwd(x.value, gamma.value, grad_out, mean, var, groups=groups, eps=eps)
        return [gx, ggamma, gbeta]

    return apply_op(forward, grad_fn, x, gamma, beta, tape=tape)


def global_avg_pool2d(x: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        # grad broadcast back: each input gets grad_out/(H*W)
        n, c, h, w = x.value.shape
        go_host = grad_out.to_host()
        go_expanded = np.repeat(go_host, h * w).reshape(n, c, h, w) / (h * w)
        from netcl.core.tensor import Tensor as T
        return [T.from_host(x.value.queue, go_expanded.astype(np.float32))]

    return apply_op(lambda t: gap2d_op(t), grad_fn, x, tape=tape)

def leaky_relu(x: Node, negative_slope: float = 0.01, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        expr = f"(v0 > 0 ? 1.0f : {negative_slope}f)"
        mask = elementwise_binary(x.value, x.value, expression=expr)
        return [elementwise_binary(grad_out, mask, expression="MUL(v0, v1)")]

    return apply_op(lambda t: leaky_relu_op(t, negative_slope=negative_slope), grad_fn, x, tape=tape)


def sub(a: Node, b: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        return [grad_out, elementwise_binary(grad_out, grad_out, expression="MUL(v0, -1)")]

    if a.value.shape == b.value.shape:
        return apply_op(lambda x, y: elementwise_binary(x, y, expression="SUB(v0, v1)"), grad_fn, a, b, tape=tape)
    else:
        return apply_op(lambda x, y: bcast_bin(x, y, op="SUB"), grad_fn, a, b, tape=tape)


def mse_loss(pred: Node, target: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        diff = elementwise_binary(pred.value, target.value, expression="SUB(v0, v1)")
        scale = 2.0
        grad_pred = elementwise_binary(diff, diff, expression=f"MUL(v0, {scale})")  # 2*diff
        grad_target = elementwise_binary(grad_pred, grad_pred, expression="MUL(v0, -1)")
        return [grad_pred, grad_target]

    def forward(x: Tensor, y: Tensor) -> Tensor:
        diff = elementwise_binary(x, y, expression="SUB(v0, v1)")
        sq = elementwise_binary(diff, diff, expression="MUL(v0, v1)")
        # reduce all
        from netcl.ops.reduction import reduce_sum

        return reduce_sum(sq, axis=None)

    return apply_op(lambda x, y: forward(x, y), grad_fn, pred, target, tape=tape)


def l1_loss(pred: Node, target: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        sign = elementwise_binary(pred.value, target.value, expression="(v0 > v1 ? 1.0f : (v0 < v1 ? -1.0f : 0.0f))")
        grad = elementwise_binary(grad_out, sign, expression="MUL(v0, v1)")
        return [grad, elementwise_binary(grad, grad, expression="MUL(v0, -1)")]

    def forward(x: Tensor, y: Tensor) -> Tensor:
        diff = elementwise_binary(x, y, expression="SUB(v0, v1)")
        absd = elementwise_binary(diff, diff, expression="ABS(v0)")
        from netcl.ops.reduction import reduce_sum

        return reduce_sum(absd, axis=None)

    return apply_op(lambda x, y: forward(x, y), grad_fn, pred, target, tape=tape)


def l2_loss(pred: Node, target: Node, tape=None) -> Node:
    def grad_fn(grad_out: Tensor):
        diff = elementwise_binary(pred.value, target.value, expression="SUB(v0, v1)")
        grad = elementwise_binary(diff, grad_out, expression="MUL(v0, v1)")
        return [grad, elementwise_binary(grad, grad, expression="MUL(v0, -1)")]

    def forward(x: Tensor, y: Tensor) -> Tensor:
        diff = elementwise_binary(x, y, expression="SUB(v0, v1)")
        sq = elementwise_binary(diff, diff, expression="MUL(v0, v1)")
        from netcl.ops.reduction import reduce_sum

        return reduce_sum(sq, axis=None)

    return apply_op(lambda x, y: forward(x, y), grad_fn, pred, target, tape=tape)


def hinge_loss(logits: Node, targets: Node, margin: float = 1.0, tape=None) -> Node:
    """
    Multi-class hinge: assumes targets are one-hot.
    """

    def forward(l: Tensor, t: Tensor) -> Tensor:
        # loss = sum(max(0, margin - (scores_y - scores_not_y)))
        l_host = l.to_host()
        t_host = t.to_host()
        true_scores = (l_host * t_host).sum(axis=1, keepdims=True)
        margins = np.maximum(0.0, margin - true_scores + l_host)
        margins[t_host.astype(bool)] = 0.0
        loss = margins.sum() / l_host.shape[0]
        return Tensor.from_host(l.queue, np.array([loss], dtype=np.float32))

    def grad_fn(grad_out: Tensor):
        l_host = logits.value.to_host()
        t_host = targets.value.to_host()
        batch = l_host.shape[0]
        true_scores = (l_host * t_host).sum(axis=1, keepdims=True)
        margins = margin - true_scores + l_host
        mask = (margins > 0).astype(np.float32)
        mask[t_host.astype(bool)] = 0.0
        row_sum = mask.sum(axis=1, keepdims=True)
        grad = mask
        grad[t_host.astype(bool)] = -row_sum[:, 0]
        grad = grad / batch
        g = Tensor.from_host(logits.value.queue, grad.astype(np.float32))
        if grad_out.shape == (1,):
            scale = float(grad_out.to_host()[0])
            if scale != 1.0:
                g = elementwise_binary(g, g, expression=f"MUL(v0, {scale})")
        return [g, None]

    return apply_op(lambda l, t: forward(l, t), grad_fn, logits, targets, tape=tape)


def cross_entropy(logits: Node, targets: Node, tape=None) -> Node:
    """
    Cross-entropy with softmax; targets expected as one-hot float tensor.
    Gradients are computed analytically: grad_logits = (softmax - targets) / N.
    """

    def forward(logit_t: Tensor, target_t: Tensor) -> Tensor:
        probs = softmax_op(logit_t)
        probs_host = probs.to_host()
        targets_host = target_t.to_host()
        # avoid log(0)
        eps = 1e-8
        loss = -np.sum(targets_host * np.log(probs_host + eps)) / targets_host.shape[0]
        return Tensor.from_host(logit_t.queue, np.array([loss], dtype=np.float32))

    def grad_fn(grad_out: Tensor):
        probs = softmax_op(logits.value)
        probs_host = probs.to_host()
        targets_host = targets.value.to_host()
        batch = targets_host.shape[0]
        grad_logits = (probs_host - targets_host) / batch
        grad_tensor = Tensor.from_host(logits.value.queue, grad_logits.astype(np.float32))
        # scale by grad_out (scalar or matching shape)
        if grad_out.shape == (1,):
            scale = float(grad_out.to_host()[0])
            if scale != 1.0:
                grad_tensor = elementwise_binary(grad_tensor, grad_tensor, expression=f"MUL(v0, {scale})")
        else:
            grad_tensor = elementwise_binary(grad_tensor, grad_out, expression="MUL(v0, v1)")
        return [grad_tensor, None]

    return apply_op(lambda l, t: forward(l, t), grad_fn, logits, targets, tape=tape)
from netcl.nn.batchnorm import batch_norm2d as bn2d_fwd, batch_norm2d_backward as bn2d_bwd
from netcl.nn.layernorm import layer_norm as ln_fwd, layer_norm_backward as ln_bwd
from netcl.nn.padding import pad2d as pad2d_op
from netcl.nn.groupnorm import group_norm as gn_fwd, group_norm_backward as gn_bwd
from netcl.nn.pooling import global_avg_pool2d as gap2d_op

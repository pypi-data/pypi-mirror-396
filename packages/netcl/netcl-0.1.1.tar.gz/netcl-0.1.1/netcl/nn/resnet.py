from __future__ import annotations

import numpy as np

from netcl import autograd as ag
from netcl.core.tensor import Tensor
from netcl.nn import init as init_ops
from netcl.nn.modules import Module
from netcl.core.device import manager


def _bn_params(queue, channels: int):
    gamma = Tensor.from_host(queue, np.ones((channels,), dtype=np.float32))
    beta = Tensor.from_host(queue, np.zeros((channels,), dtype=np.float32))
    running_mean = Tensor.from_host(queue, np.zeros((channels,), dtype=np.float32))
    running_var = Tensor.from_host(queue, np.ones((channels,), dtype=np.float32))
    return gamma, beta, running_mean, running_var


class ResNet18(Module):
    """
    Minimal ResNet-18 style model (CIFAR-friendly: 3x3 stem, stride2 in later stages).
    Uses autograd ops directly so that weights participate in backward via Node wrappers.
    """

    def __init__(self, queue=None, num_classes: int = 10, base_channels: int = 64, use_batchnorm: bool = True):
        super().__init__()
        if queue is None:
            queue = manager.default().queue
        self.queue = queue
        self.num_classes = num_classes
        self.use_bn = use_batchnorm

        # Stem
        self.conv1_w = Tensor.from_shape(queue, (base_channels, 3, 3, 3), dtype="float32")
        self.conv1_b = Tensor.from_shape(queue, (base_channels,), dtype="float32")
        init_ops.kaiming_uniform(self.conv1_w)
        init_ops.kaiming_uniform(self.conv1_b)
        self.bn1 = _bn_params(queue, base_channels) if self.use_bn else None

        # Residual blocks configuration
        channels = [base_channels, base_channels * 2, base_channels * 4, base_channels * 8]
        blocks_per_stage = [2, 2, 2, 2]
        self.blocks = []
        in_c = base_channels
        for stage_idx, (c_out, reps) in enumerate(zip(channels, blocks_per_stage)):
            stride = 1 if stage_idx == 0 else 2
            for block_idx in range(reps):
                blk_stride = stride if block_idx == 0 else 1
                block = self._make_block(in_c, c_out, stride=blk_stride)
                self.blocks.append(block)
                in_c = c_out

        # Classification head
        self.fc_w = Tensor.from_shape(queue, (channels[-1], num_classes), dtype="float32")
        self.fc_b = Tensor.from_shape(queue, (num_classes,), dtype="float32")
        init_ops.xavier_uniform(self.fc_w)
        init_ops.xavier_uniform(self.fc_b)

    def _make_block(self, in_c: int, out_c: int, stride: int):
        w1 = Tensor.from_shape(self.queue, (out_c, in_c, 3, 3), dtype="float32")
        b1 = Tensor.from_shape(self.queue, (out_c,), dtype="float32")
        w2 = Tensor.from_shape(self.queue, (out_c, out_c, 3, 3), dtype="float32")
        b2 = Tensor.from_shape(self.queue, (out_c,), dtype="float32")
        init_ops.kaiming_uniform(w1)
        init_ops.kaiming_uniform(b1)
        init_ops.kaiming_uniform(w2)
        init_ops.kaiming_uniform(b2)
        bn1 = _bn_params(self.queue, out_c) if self.use_bn else None
        bn2 = _bn_params(self.queue, out_c) if self.use_bn else None

        proj = None
        if stride != 1 or in_c != out_c:
            pw = Tensor.from_shape(self.queue, (out_c, in_c, 1, 1), dtype="float32")
            pb = Tensor.from_shape(self.queue, (out_c,), dtype="float32")
            init_ops.kaiming_uniform(pw)
            init_ops.kaiming_uniform(pb)
            proj_bn = _bn_params(self.queue, out_c) if self.use_bn else None
            proj = (pw, pb, proj_bn)

        return {
            "w1": w1,
            "b1": b1,
            "bn1": bn1,
            "w2": w2,
            "b2": b2,
            "bn2": bn2,
            "stride": stride,
            "proj": proj,
        }

    def _conv_bn_relu(self, x, w, b, bn_params, stride: int, pad: int, tape):
        w_node = ag.tensor(w, requires_grad=True)
        b_node = ag.tensor(b, requires_grad=True)
        out = ag.conv2d(x, w_node, bias=b_node, stride=stride, pad=pad, tape=tape)
        if self.use_bn and bn_params is not None:
            gamma, beta, rm, rv = bn_params
            out = ag.batch_norm2d(out, ag.tensor(gamma, requires_grad=True), ag.tensor(beta, requires_grad=True), rm, rv, training=True, tape=tape)
        out = ag.relu(out, tape=tape)
        return out

    def _project(self, x, proj, stride: int, tape):
        if proj is None:
            return x
        pw, pb, proj_bn = proj
        out = ag.conv2d(x, ag.tensor(pw, requires_grad=True), bias=ag.tensor(pb, requires_grad=True), stride=stride, pad=0, tape=tape)
        if self.use_bn and proj_bn is not None:
            gamma, beta, rm, rv = proj_bn
            out = ag.batch_norm2d(out, ag.tensor(gamma, requires_grad=True), ag.tensor(beta, requires_grad=True), rm, rv, training=True, tape=tape)
        return out

    def _block(self, x, block, tape):
        out = self._conv_bn_relu(x, block["w1"], block["b1"], block["bn1"], stride=block["stride"], pad=1, tape=tape)
        w2 = ag.tensor(block["w2"], requires_grad=True)
        b2 = ag.tensor(block["b2"], requires_grad=True)
        out = ag.conv2d(out, w2, bias=b2, pad=1, tape=tape)
        if self.use_bn and block["bn2"] is not None:
            gamma2, beta2, rm2, rv2 = block["bn2"]
            out = ag.batch_norm2d(out, ag.tensor(gamma2, requires_grad=True), ag.tensor(beta2, requires_grad=True), rm2, rv2, training=True, tape=tape)
        skip = self._project(x, block["proj"], block["stride"], tape)
        out = ag.add(out, skip, tape=tape)
        out = ag.relu(out, tape=tape)
        return out

    def __call__(self, x, tape=None):
        out = self._conv_bn_relu(x, self.conv1_w, self.conv1_b, self.bn1, stride=1, pad=1, tape=tape)
        for block in self.blocks:
            out = self._block(out, block, tape)
        out = ag.global_avg_pool2d(out, tape=tape)
        # flatten N x C x 1 x 1 -> N x C
        n = out.value.shape[0]
        c = out.value.shape[1]
        out = ag.flatten(out, (n, c), tape=tape)
        logits = ag.matmul_op(out, ag.tensor(self.fc_w, requires_grad=True), tape=tape)
        logits = ag.bias_add(logits, ag.tensor(self.fc_b, requires_grad=True), tape=tape)
        return logits

    def parameters(self):
        params = [self.conv1_w, self.conv1_b, self.fc_w, self.fc_b]
        if self.use_bn and self.bn1 is not None:
            gamma, beta, _, _ = self.bn1
            params.extend([gamma, beta])
        for block in self.blocks:
            params.extend([block["w1"], block["b1"], block["w2"], block["b2"]])
            if self.use_bn:
                if block["bn1"] is not None:
                    params.extend(block["bn1"][:2])
                if block["bn2"] is not None:
                    params.extend(block["bn2"][:2])
            if block["proj"] is not None:
                proj_w, proj_b, proj_bn = block["proj"]
                params.extend([proj_w, proj_b])
                if self.use_bn and proj_bn is not None:
                    params.extend(proj_bn[:2])
        return params

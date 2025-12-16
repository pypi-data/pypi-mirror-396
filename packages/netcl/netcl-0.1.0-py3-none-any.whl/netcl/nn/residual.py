from __future__ import annotations

from netcl import autograd as ag


def basic_block(x: ag.Node, w1: ag.Node, b1: ag.Node, w2: ag.Node, b2: ag.Node, stride: int = 1, pad: int = 1, proj: ag.Node | None = None, tape=None):
    """
    Simple residual block: conv-bn?-relu -> conv-bn? + skip -> relu.
    BatchNorm not yet present; pad/stride passed to conv.
    If proj is given (tuple of (w_p, b_p)), it is applied to the skip path for channel/stride match.
    """
    out = ag.conv2d(x, w1, bias=b1, stride=stride, pad=pad, tape=tape)
    out = ag.relu(out, tape=tape)
    out = ag.conv2d(out, w2, bias=b2, pad=pad, tape=tape)
    if proj is not None:
        wp, bp = proj
        skip = ag.conv2d(x, wp, bias=bp, stride=stride, pad=0, tape=tape)
    else:
        skip = x
    out = ag.add(out, skip, tape=tape)
    out = ag.relu(out, tape=tape)
    return out

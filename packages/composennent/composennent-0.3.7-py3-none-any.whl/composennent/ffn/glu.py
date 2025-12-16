"""GLU Feed-Forward Network layer.

The original Gated Linear Unit from "Language Modeling with Gated
Convolutional Networks" (Dauphin et al., 2017).

Reference: https://arxiv.org/abs/1612.08083
"""

import torch
import torch.nn as nn
from typing import Optional

from composennent.basic.block import Block


class GLU(Block):
    """GLU Feed-Forward Network layer.

    Implements: GLU(x) = (xW1 + b1) ⊙ sigmoid(xW2 + b2)

    Args:
        in_features: Input dimension.
        hidden_features: Hidden dimension. Defaults to 4 * in_features.
        out_features: Output dimension. Defaults to in_features.
        bias: Whether to use bias. Defaults to True.

    Example:
        >>> ffn = GLU(in_features=512, hidden_features=2048)
        >>> x = torch.randn(2, 100, 512)
        >>> output = ffn(x)  # Shape: (2, 100, 512)
    """

    def __init__(
        self,
        in_features: int,
        hidden_features: Optional[int] = None,
        out_features: Optional[int] = None,
        bias: bool = True,
    ) -> None:
        super().__init__()
        hidden_features = hidden_features or in_features * 4
        out_features = out_features or in_features

        self.w1 = nn.Linear(in_features, hidden_features, bias=bias)
        self.w2 = nn.Linear(in_features, hidden_features, bias=bias)
        self.w3 = nn.Linear(hidden_features, out_features, bias=bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w3(torch.sigmoid(self.w1(x)) * self.w2(x))

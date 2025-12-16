"""ReGLU Feed-Forward Network layer.

Reference: https://arxiv.org/abs/2002.05202
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

from composennent.basic.block import Block


class ReGLU(Block):
    """ReGLU Feed-Forward Network layer.

    Implements: ReGLU(x) = (xW1 + b1) ⊙ ReLU(xW2 + b2)

    Simpler variant using ReLU activation for the gate.

    Args:
        in_features: Input dimension.
        hidden_features: Hidden dimension. Defaults to 4 * in_features.
        out_features: Output dimension. Defaults to in_features.
        bias: Whether to use bias. Defaults to False.

    Example:
        >>> ffn = ReGLU(in_features=512, hidden_features=2048)
        >>> x = torch.randn(2, 100, 512)
        >>> output = ffn(x)  # Shape: (2, 100, 512)
    """

    def __init__(
        self,
        in_features: int,
        hidden_features: Optional[int] = None,
        out_features: Optional[int] = None,
        bias: bool = False,
    ) -> None:
        super().__init__()
        hidden_features = hidden_features or in_features * 4
        out_features = out_features or in_features

        self.w1 = nn.Linear(in_features, hidden_features, bias=bias)
        self.w2 = nn.Linear(in_features, hidden_features, bias=bias)
        self.w3 = nn.Linear(hidden_features, out_features, bias=bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w3(F.relu(self.w1(x)) * self.w2(x))
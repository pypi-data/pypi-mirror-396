"""Standard MLP Feed-Forward Network.

The standard FFN from the original Transformer paper.
"""

import torch
import torch.nn as nn
from typing import Optional

from composennent.basic.block import Block


class MLP(Block):
    """Standard MLP Feed-Forward Network.

    Implements: MLP(x) = GELU(xW1 + b1)W2 + b2

    Args:
        in_features: Input dimension.
        hidden_features: Hidden dimension. Defaults to 4 * in_features.
        out_features: Output dimension. Defaults to in_features.
        bias: Whether to use bias. Defaults to True.
        dropout: Dropout probability. Defaults to 0.0.

    Example:
        >>> ffn = MLP(in_features=512, hidden_features=2048)
        >>> x = torch.randn(2, 100, 512)
        >>> output = ffn(x)  # Shape: (2, 100, 512)
    """

    def __init__(
        self,
        in_features: int,
        hidden_features: Optional[int] = None,
        out_features: Optional[int] = None,
        bias: bool = True,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        hidden_features = hidden_features or in_features * 4
        out_features = out_features or in_features

        self.fc1 = nn.Linear(in_features, hidden_features, bias=bias)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_features, out_features, bias=bias)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

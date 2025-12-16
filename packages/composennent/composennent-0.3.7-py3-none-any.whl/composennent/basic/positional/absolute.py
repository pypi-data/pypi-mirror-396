"""Sinusoidal absolute positional encoding."""

import math
import torch
import torch.nn as nn
from typing import Optional

from composennent.basic.block import Block


class AbsolutePositionalEncoding(Block):
    """Sinusoidal absolute positional encoding.

    Adds fixed sinusoidal position information to embeddings.
    From "Attention Is All You Need" (Vaswani et al., 2017).

    Args:
        d_model: Dimension of the model (embedding size).
        max_len: Maximum sequence length. Defaults to 5000.
        dropout: Dropout probability. Defaults to 0.1.

    Example:
        >>> pe = AbsolutePositionalEncoding(d_model=512)
        >>> x = torch.randn(2, 100, 512)
        >>> output = pe(x)
    """

    def __init__(
        self,
        d_model: int,
        max_len: int = 5000,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.max_len = max_len
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        seq_len = x.size(1)
        x = x + self.pe[:, :seq_len, :]
        return self.dropout(x)

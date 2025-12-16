"""Learnable relative positional encoding."""

import torch
import torch.nn as nn

from composennent.basic.block import Block


class RelativePositionalEncoding(Block):
    """Learnable relative positional encoding.

    Adds learnable position embeddings that are looked up and added.
    Simple and effective for fixed-length sequences.

    Args:
        d_model: Dimension of the model.
        max_len: Maximum sequence length. Defaults to 5000.
        dropout: Dropout probability. Defaults to 0.1.

    Example:
        >>> pe = RelativePositionalEncoding(d_model=512, max_len=1024)
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
        self.position_embeddings = nn.Embedding(max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)
        x = x + self.position_embeddings(positions)
        return self.dropout(x)

"""Token embedding for vocabulary lookup."""

import torch
import torch.nn as nn
import math

from composennent.basic.block import Block


class TokenEmbedding(Block):
    """Token embedding with vocabulary lookup.

    Standard embedding layer for text tokenization. Optionally
    scales embeddings by sqrt(d_model) as in original Transformer.

    Args:
        vocab_size: Size of vocabulary.
        embed_dim: Embedding dimension.
        padding_idx: Token ID for padding (masked in embedding). Defaults to 0.
        scale: Whether to scale by sqrt(embed_dim). Defaults to True.

    Example:
        >>> emb = TokenEmbedding(vocab_size=32000, embed_dim=512)
        >>> tokens = torch.randint(0, 32000, (2, 100))
        >>> x = emb(tokens)  # (2, 100, 512)
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        padding_idx: int = 0,
        scale: bool = True,
    ) -> None:
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.scale = scale
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=padding_idx)
        self.scale_factor = math.sqrt(embed_dim) if scale else 1.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Convert token IDs to embeddings.
        
        Args:
            x: Token IDs of shape (batch, seq_len).
            
        Returns:
            Embeddings of shape (batch, seq_len, embed_dim).
        """
        return self.embedding(x) * self.scale_factor

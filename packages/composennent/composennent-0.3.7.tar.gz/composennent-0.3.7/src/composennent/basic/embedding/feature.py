"""Feature embedding for continuous/tabular features."""

import torch
import torch.nn as nn

from composennent.basic.block import Block


class FeatureEmbedding(Block):
    """Feature embedding for continuous/tabular features.

    Projects continuous features to embedding space.
    Useful for tabular data or multi-modal fusion.

    Args:
        in_features: Number of input features.
        embed_dim: Embedding dimension.
        bias: Whether to use bias. Defaults to True.

    Example:
        >>> emb = FeatureEmbedding(in_features=32, embed_dim=512)
        >>> features = torch.randn(2, 32)
        >>> x = emb(features)  # (2, 512)
    """

    def __init__(
        self,
        in_features: int,
        embed_dim: int,
        bias: bool = True,
    ) -> None:
        super().__init__()
        self.in_features = in_features
        self.embed_dim = embed_dim
        self.projection = nn.Linear(in_features, embed_dim, bias=bias)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Project continuous features to embedding space.
        
        Args:
            x: Feature tensor of shape (batch, in_features) or 
               (batch, seq_len, in_features).
            
        Returns:
            Embeddings of shape (batch, embed_dim) or 
            (batch, seq_len, embed_dim).
        """
        x = self.projection(x)
        x = self.norm(x)
        return x

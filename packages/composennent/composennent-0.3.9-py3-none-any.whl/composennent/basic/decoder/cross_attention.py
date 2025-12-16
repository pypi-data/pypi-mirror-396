"""Cross-Attention Decoder block (T5-style, encoder-decoder)."""

import torch
import torch.nn as nn
from typing import Optional, Tuple

from composennent.basic.block import Block
from composennent.basic.sequential import SequentialBlock
from composennent.attention import MultiHeadAttention


class CrossAttentionDecoder(Block):
    """Cross-Attention Decoder block for encoder-decoder models (T5-style).

    Includes both self-attention and cross-attention to encoder outputs.
    Suitable for:
    - T5, BART, Whisper
    - Machine translation
    - Summarization

    Args:
        latent_dim: Dimension of the model.
        num_heads: Number of attention heads.
        dropout: Dropout probability. Defaults to 0.1.
        mlp_ratio: MLP expansion ratio. Defaults to 4.
        return_attention: Whether to return attention weights.

    Example:
        >>> dec = CrossAttentionDecoder(latent_dim=512, num_heads=8)
        >>> output = dec(x, memory=encoder_output, tgt_mask=causal_mask)
    """

    def __init__(
        self,
        latent_dim: int,
        num_heads: int,
        dropout: float = 0.1,
        mlp_ratio: int = 4,
        return_attention: bool = False,
    ) -> None:
        super().__init__()
        self.latent_dim = latent_dim
        self.return_attention = return_attention

        self.self_attn = MultiHeadAttention(
            embed_dim=latent_dim,
            num_heads=num_heads,
            dropout=dropout,
        )
        self.norm1 = nn.LayerNorm(latent_dim)

        self.cross_attn = MultiHeadAttention(
            embed_dim=latent_dim,
            num_heads=num_heads,
            dropout=dropout,
        )
        self.norm2 = nn.LayerNorm(latent_dim)

        mlp_hidden_dim = latent_dim * mlp_ratio
        self.mlp = SequentialBlock(
            nn.Linear(latent_dim, mlp_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden_dim, latent_dim),
        )
        self.norm3 = nn.LayerNorm(latent_dim)
        self.dropout_layer = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        memory: torch.Tensor,
        tgt_mask: Optional[torch.Tensor] = None,
        tgt_key_padding_mask: Optional[torch.Tensor] = None,
        memory_key_padding_mask: Optional[torch.Tensor] = None,
        return_attention: Optional[bool] = None,
    ) -> Tuple[torch.Tensor, Optional[Tuple]]:
        return_attn = return_attention if return_attention is not None else self.return_attention

        # Self-attention
        normed = self.norm1(x)
        self_attn_out, self_attn_weights = self.self_attn(
            normed,
            attn_mask=tgt_mask,
            key_padding_mask=tgt_key_padding_mask,
            need_weights=return_attn,
        )
        x = x + self.dropout_layer(self_attn_out)

        # Cross-attention to encoder output
        normed = self.norm2(x)
        cross_attn_out, cross_attn_weights = self.cross_attn(
            normed,
            key=memory,
            value=memory,
            key_padding_mask=memory_key_padding_mask,
            need_weights=return_attn,
        )
        x = x + self.dropout_layer(cross_attn_out)

        # FFN
        normed = self.norm3(x)
        mlp_out = self.mlp(normed)
        x = x + self.dropout_layer(mlp_out)

        if return_attn:
            return x, (self_attn_weights, cross_attn_weights)
        return x, None

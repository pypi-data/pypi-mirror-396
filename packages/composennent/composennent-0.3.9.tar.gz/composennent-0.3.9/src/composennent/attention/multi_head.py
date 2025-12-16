"""Multi-Head Attention implementation."""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class MultiHeadAttention(nn.Module):
    """Multi-Head Attention block.

    Implements scaled dot-product attention with multiple heads as described
    in "Attention Is All You Need". Supports causal masking, padding masks,
    and optional dropout.

    Args:
        embed_dim: Total dimension of the model.
        num_heads: Number of attention heads.
        dropout: Dropout probability on attention weights. Defaults to 0.0.
        bias: Whether to use bias in projections. Defaults to True.
        add_bias_kv: Whether to add bias to key/value. Defaults to False.

    Example:
        >>> attn = MultiHeadAttention(embed_dim=512, num_heads=8)
        >>> x = torch.randn(2, 100, 512)  # (batch, seq, embed)
        >>> output, weights = attn(x)
        >>> # output: (2, 100, 512), weights: (2, 8, 100, 100)
    """

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        dropout: float = 0.0,
        bias: bool = True,
        add_bias_kv: bool = False,
    ) -> None:
        super().__init__()

        if embed_dim % num_heads != 0:
            raise ValueError(
                f"embed_dim ({embed_dim}) must be divisible by num_heads ({num_heads})"
            )

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.dropout = dropout

        # Projections for Q, K, V
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)

        # Optional bias for K and V
        if add_bias_kv:
            self.bias_k = nn.Parameter(torch.zeros(1, 1, embed_dim))
            self.bias_v = nn.Parameter(torch.zeros(1, 1, embed_dim))
        else:
            self.bias_k = None
            self.bias_v = None

        self._reset_parameters()

    def _reset_parameters(self) -> None:
        """Initialize parameters with Xavier uniform."""
        nn.init.xavier_uniform_(self.q_proj.weight)
        nn.init.xavier_uniform_(self.k_proj.weight)
        nn.init.xavier_uniform_(self.v_proj.weight)
        nn.init.xavier_uniform_(self.out_proj.weight)

        if self.q_proj.bias is not None:
            nn.init.zeros_(self.q_proj.bias)
            nn.init.zeros_(self.k_proj.bias)
            nn.init.zeros_(self.v_proj.bias)
            nn.init.zeros_(self.out_proj.bias)

    def forward(
        self,
        query: torch.Tensor,
        key: Optional[torch.Tensor] = None,
        value: Optional[torch.Tensor] = None,
        attn_mask: Optional[torch.Tensor] = None,
        key_padding_mask: Optional[torch.Tensor] = None,
        need_weights: bool = True,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Forward pass for multi-head attention.

        Supports self-attention (q=k=v) and cross-attention (separate k, v).

        Args:
            query: Query tensor of shape (batch, seq_q, embed_dim).
            key: Key tensor of shape (batch, seq_k, embed_dim).
                If None, uses query (self-attention).
            value: Value tensor of shape (batch, seq_k, embed_dim).
                If None, uses key.
            attn_mask: Attention mask of shape (seq_q, seq_k) or
                (batch, seq_q, seq_k). True = masked.
            key_padding_mask: Padding mask of shape (batch, seq_k).
                True = padded position to mask.
            need_weights: Whether to return attention weights.

        Returns:
            Tuple of:
                - Output tensor of shape (batch, seq_q, embed_dim)
                - Attention weights of shape (batch, num_heads, seq_q, seq_k)
                  if need_weights=True, else None
        """
        # Self-attention: key and value default to query
        if key is None:
            key = query
        if value is None:
            value = key

        batch_size, seq_q, _ = query.shape
        seq_k = key.size(1)

        # Project Q, K, V
        q = self.q_proj(query)
        k = self.k_proj(key)
        v = self.v_proj(value)

        # Add bias to K and V if present
        if self.bias_k is not None:
            k = torch.cat([k, self.bias_k.expand(batch_size, -1, -1)], dim=1)
            v = torch.cat([v, self.bias_v.expand(batch_size, -1, -1)], dim=1)
            seq_k += 1
            if key_padding_mask is not None:
                key_padding_mask = F.pad(key_padding_mask, (0, 1), value=False)

        # Reshape to (batch, num_heads, seq, head_dim)
        q = q.view(batch_size, seq_q, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_k, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_k, self.num_heads, self.head_dim).transpose(1, 2)

        # Scaled dot-product attention
        # (batch, heads, seq_q, head_dim) @ (batch, heads, head_dim, seq_k)
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) * self.scale

        # Apply attention mask (True = masked, set to -inf)
        if attn_mask is not None:
            if attn_mask.dim() == 2:
                attn_mask = attn_mask.unsqueeze(0).unsqueeze(0)
            elif attn_mask.dim() == 3:
                attn_mask = attn_mask.unsqueeze(1)
            attn_scores = attn_scores.masked_fill(attn_mask, float("-inf"))

        # Apply key padding mask
        if key_padding_mask is not None:
            # (batch, 1, 1, seq_k)
            key_padding_mask = key_padding_mask.unsqueeze(1).unsqueeze(2)
            attn_scores = attn_scores.masked_fill(key_padding_mask, float("-inf"))

        # Softmax and dropout
        attn_weights = F.softmax(attn_scores, dim=-1)
        attn_weights = F.dropout(attn_weights, p=self.dropout, training=self.training)

        # Apply attention to values
        # (batch, heads, seq_q, head_dim)
        attn_output = torch.matmul(attn_weights, v)

        # Reshape back to (batch, seq_q, embed_dim)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, seq_q, self.embed_dim)

        # Final projection
        output = self.out_proj(attn_output)

        if need_weights:
            return output, attn_weights
        return output, None

    def __repr__(self) -> str:
        return (
            f"MultiHeadAttention(embed_dim={self.embed_dim}, "
            f"num_heads={self.num_heads}, dropout={self.dropout})"
        )

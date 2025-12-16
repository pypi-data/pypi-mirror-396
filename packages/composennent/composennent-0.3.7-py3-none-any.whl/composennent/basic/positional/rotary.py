"""Rotary Position Embedding (RoPE)."""

import torch
import torch.nn as nn
from typing import Optional, Tuple

from composennent.basic.block import Block


class RotaryPositionalEncoding(Block):
    """Rotary Position Embedding (RoPE).

    Applies rotation to query and key vectors based on position.
    Used in LLaMA, Mistral, GPT-NeoX.

    Unlike additive encodings, RoPE is applied during attention
    to Q and K vectors, not to input embeddings.

    Args:
        dim: Dimension of the embeddings (head_dim typically).
        max_len: Maximum sequence length. Defaults to 5000.
        base: Base for frequency computation. Defaults to 10000.

    Example:
        >>> rope = RotaryPositionalEncoding(dim=64, max_len=2048)
        >>> q = torch.randn(2, 8, 100, 64)  # (batch, heads, seq, head_dim)
        >>> k = torch.randn(2, 8, 100, 64)
        >>> q_rot, k_rot = rope(q, k)
    """

    def __init__(
        self,
        dim: int,
        max_len: int = 5000,
        base: float = 10000.0,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.max_len = max_len
        self.base = base

        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self._update_cos_sin_cache(max_len)

    def _update_cos_sin_cache(self, seq_len: int) -> None:
        t = torch.arange(seq_len, device=self.inv_freq.device).float()
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        self.register_buffer("cos_cached", emb.cos().unsqueeze(0).unsqueeze(0))
        self.register_buffer("sin_cached", emb.sin().unsqueeze(0).unsqueeze(0))

    def _rotate_half(self, x: torch.Tensor) -> torch.Tensor:
        x1 = x[..., : self.dim // 2]
        x2 = x[..., self.dim // 2 :]
        return torch.cat([-x2, x1], dim=-1)

    def forward(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        seq_len: Optional[int] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        if seq_len is None:
            seq_len = q.size(2)

        if seq_len > self.cos_cached.size(2):
            self._update_cos_sin_cache(seq_len)

        cos = self.cos_cached[:, :, :seq_len, :]
        sin = self.sin_cached[:, :, :seq_len, :]

        q_rot = (q * cos) + (self._rotate_half(q) * sin)
        k_rot = (k * cos) + (self._rotate_half(k) * sin)

        return q_rot, k_rot

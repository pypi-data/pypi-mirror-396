"""Attention mask utilities for transformers."""

import torch
from typing import Optional


def causal_mask(seq_len: int, device: Optional[torch.device] = None) -> torch.Tensor:
    """Generate upper-triangular causal mask for autoregressive attention.

    Args:
        seq_len: Length of the sequence.
        device: Device to create the mask on. Defaults to CPU.

    Returns:
        Boolean mask of shape (seq_len, seq_len) where True indicates
        positions to be masked (future tokens that should not be attended to).

    Example:
        >>> mask = causal_mask(4)
        >>> # Token at position i can only attend to positions <= i
    """
    mask = torch.triu(
        torch.ones(seq_len, seq_len, device=device, dtype=torch.bool),
        diagonal=1,
    )
    return mask


def padding_mask(
    lengths: torch.Tensor,
    max_len: Optional[int] = None,
) -> torch.Tensor:
    """Generate padding mask from sequence lengths.

    Args:
        lengths: Tensor of shape (batch_size,) containing actual lengths.
        max_len: Maximum sequence length. If None, uses max(lengths).

    Returns:
        Boolean mask of shape (batch_size, max_len) where True indicates
        padded positions that should be masked.

    Example:
        >>> lengths = torch.tensor([3, 5, 2])
        >>> mask = padding_mask(lengths, max_len=5)
        >>> # mask[0] = [False, False, False, True, True]
        >>> # mask[1] = [False, False, False, False, False]
        >>> # mask[2] = [False, False, True, True, True]
    """
    if max_len is None:
        max_len = int(lengths.max().item())

    batch_size = lengths.size(0)
    # Create range tensor: [0, 1, 2, ..., max_len-1]
    positions = torch.arange(max_len, device=lengths.device).unsqueeze(0)
    # Expand lengths for comparison: (batch_size, 1)
    lengths = lengths.unsqueeze(1)
    # True where position >= length (i.e., padded)
    mask = positions >= lengths
    return mask


def sliding_window_mask(
    seq_len: int,
    window_size: int,
    device: Optional[torch.device] = None,
) -> torch.Tensor:
    """Generate sliding window attention mask for local attention.

    Each token can only attend to tokens within a window of size `window_size`
    centered on itself. This reduces attention from O(n^2) to O(n*w).

    Args:
        seq_len: Length of the sequence.
        window_size: Size of the attention window (total, not one-sided).
        device: Device to create the mask on.

    Returns:
        Boolean mask of shape (seq_len, seq_len) where True indicates
        positions outside the window that should be masked.

    Example:
        >>> mask = sliding_window_mask(6, window_size=3)
        >>> # Each token attends to 1 token before and 1 after (window=3)
    """
    # Create position indices
    row_idx = torch.arange(seq_len, device=device).unsqueeze(1)
    col_idx = torch.arange(seq_len, device=device).unsqueeze(0)

    # Distance between positions
    distance = (row_idx - col_idx).abs()

    # Mask positions outside the window (half window on each side)
    half_window = window_size // 2
    mask = distance > half_window

    return mask


def combine_masks(
    *masks: torch.Tensor,
    causal: bool = False,
    seq_len: Optional[int] = None,
) -> torch.Tensor:
    """Combine multiple masks with logical OR.

    Useful for combining causal mask with padding mask, or adding
    sliding window constraints to causal attention.

    Args:
        *masks: Variable number of masks to combine.
        causal: If True, also apply causal mask.
        seq_len: Required if causal=True and no masks provided.

    Returns:
        Combined boolean mask where True indicates masked positions.

    Example:
        >>> pad_mask = padding_mask(lengths, max_len=10)  # (batch, seq)
        >>> combined = combine_masks(pad_mask, causal=True, seq_len=10)
        >>> # Shape: (batch, seq, seq) - causal + padding
    """
    if len(masks) == 0 and not causal:
        raise ValueError("At least one mask required, or set causal=True")

    device = masks[0].device if masks else None
    combined = None

    for mask in masks:
        # Expand 2D (batch, seq) to 3D (batch, 1, seq) for broadcasting
        if mask.dim() == 2:
            mask = mask.unsqueeze(1)

        if combined is None:
            combined = mask
        else:
            combined = combined | mask

    if causal:
        if seq_len is None:
            if combined is not None:
                seq_len = combined.size(-1)
            else:
                raise ValueError("seq_len required when causal=True and no masks")

        causal_m = causal_mask(seq_len, device=device)

        if combined is None:
            combined = causal_m
        else:
            combined = combined | causal_m

    return combined
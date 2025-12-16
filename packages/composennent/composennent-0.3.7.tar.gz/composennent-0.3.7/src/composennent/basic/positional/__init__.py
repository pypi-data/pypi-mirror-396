"""Positional encoding blocks for transformer models.

Usage:
    # Via factory function
    pe = positional_encoding("absolute", d_model=512)
    pe = positional_encoding("rope", dim=64)
    
    # Direct import
    from composennent.basic.positional import AbsolutePositionalEncoding
"""

from typing import Dict, Any, Type
from .absolute import AbsolutePositionalEncoding
from .relative import RelativePositionalEncoding
from .rotary import RotaryPositionalEncoding

# Registry of positional encoding types
POSITIONAL_ENCODINGS: Dict[str, Type] = {
    "absolute": AbsolutePositionalEncoding,
    "sinusoidal": AbsolutePositionalEncoding,  # alias
    "relative": RelativePositionalEncoding,
    "learnable": RelativePositionalEncoding,   # alias
    "rotary": RotaryPositionalEncoding,
    "rope": RotaryPositionalEncoding,          # alias
}


def positional_encoding(encoding_type: str, **kwargs) -> Any:
    """Create a positional encoding by type name.
    
    Args:
        encoding_type: One of "absolute", "relative", "rope"
        **kwargs: Arguments passed to the encoding class
        
    Returns:
        Positional encoding instance
        
    Example:
        >>> pe = positional_encoding("absolute", d_model=512)
        >>> pe = positional_encoding("rope", dim=64)
    """
    if encoding_type not in POSITIONAL_ENCODINGS:
        available = ", ".join(f'"{k}"' for k in POSITIONAL_ENCODINGS.keys())
        raise ValueError(f"Unknown encoding type: '{encoding_type}'. Choose from: {available}")
    return POSITIONAL_ENCODINGS[encoding_type](**kwargs)


# Alias for backward compatibility
PositionalEncoding = AbsolutePositionalEncoding

__all__ = [
    "positional_encoding",
    "AbsolutePositionalEncoding",
    "RelativePositionalEncoding",
    "RotaryPositionalEncoding",
    "PositionalEncoding",
    "POSITIONAL_ENCODINGS",
]

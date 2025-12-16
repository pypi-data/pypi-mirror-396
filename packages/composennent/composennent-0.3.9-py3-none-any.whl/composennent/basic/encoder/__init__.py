"""Encoder blocks for transformer models.

Usage:
    # Via factory function
    enc = encoder("transformer", latent_dim=512, num_heads=8)
    
    # Direct import
    from composennent.basic.encoder import TransformerEncoder
"""

from typing import Dict, Any, Type
from .transformer import TransformerEncoder

# Registry of encoder types
ENCODERS: Dict[str, Type] = {
    "transformer": TransformerEncoder,
}


def encoder(encoder_type: str, **kwargs) -> Any:
    """Create an encoder by type name.
    
    Args:
        encoder_type: One of "transformer"
        **kwargs: Arguments passed to the encoder class
        
    Returns:
        Encoder instance
        
    Example:
        >>> enc = encoder("transformer", latent_dim=512, num_heads=8)
    """
    if encoder_type not in ENCODERS:
        available = ", ".join(f'"{k}"' for k in ENCODERS.keys())
        raise ValueError(f"Unknown encoder type: '{encoder_type}'. Choose from: {available}")
    return ENCODERS[encoder_type](**kwargs)


# Aliases for backward compatibility
Encoder = TransformerEncoder

__all__ = ["encoder", "TransformerEncoder", "Encoder", "ENCODERS"]

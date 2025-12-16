"""Decoder blocks for transformer models.

Usage:
    # Via factory function
    dec = decoder("causal", latent_dim=512, num_heads=8)
    dec = decoder("cross_attention", latent_dim=512, num_heads=8)
    
    # Direct import
    from composennent.basic.decoder import CausalDecoder, CrossAttentionDecoder
"""

from typing import Dict, Any, Type
from .causal import CausalDecoder
from .cross_attention import CrossAttentionDecoder

# Registry of decoder types
DECODERS: Dict[str, Type] = {
    "causal": CausalDecoder,
    "gpt": CausalDecoder,  # alias
    "cross_attention": CrossAttentionDecoder,
    "t5": CrossAttentionDecoder,  # alias
    "encoder_decoder": CrossAttentionDecoder,  # alias
}


def decoder(decoder_type: str, **kwargs) -> Any:
    """Create a decoder by type name.
    
    Args:
        decoder_type: One of "causal", "gpt", "cross_attention", "t5"
        **kwargs: Arguments passed to the decoder class
        
    Returns:
        Decoder instance
        
    Example:
        >>> dec = decoder("causal", latent_dim=512, num_heads=8)
        >>> dec = decoder("cross_attention", latent_dim=512, num_heads=8)
    """
    if decoder_type not in DECODERS:
        available = ", ".join(f'"{k}"' for k in DECODERS.keys())
        raise ValueError(f"Unknown decoder type: '{decoder_type}'. Choose from: {available}")
    return DECODERS[decoder_type](**kwargs)


# Alias for backward compatibility (CausalDecoder is simpler and more common)
Decoder = CausalDecoder

__all__ = ["decoder", "CausalDecoder", "CrossAttentionDecoder", "Decoder", "DECODERS"]

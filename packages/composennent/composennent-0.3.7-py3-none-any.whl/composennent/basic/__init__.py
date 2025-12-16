"""Basic building blocks for neural networks.

Usage with factory functions:
    enc = encoder("transformer", latent_dim=512, num_heads=8)
    dec = decoder("causal", latent_dim=512, num_heads=8)
    emb = embedding("token", vocab_size=32000, embed_dim=512)
    pe = positional_encoding("rope", dim=64)

For masks, import from attention:
    from composennent.attention import causal_mask, padding_mask
"""

# Core blocks (simple, at root level)
from .block import Block
from .sequential import SequentialBlock

# Encoder factory and classes
from .encoder import encoder, TransformerEncoder, Encoder, ENCODERS

# Decoder factory and classes
from .decoder import decoder, CausalDecoder, CrossAttentionDecoder, Decoder, DECODERS

# Embedding factory and classes
from .embedding import embedding, TokenEmbedding, PatchEmbedding, FeatureEmbedding, EMBEDDINGS

# Positional encoding factory and classes
from .positional import (
    positional_encoding,
    AbsolutePositionalEncoding,
    RelativePositionalEncoding,
    RotaryPositionalEncoding,
    PositionalEncoding,
    POSITIONAL_ENCODINGS,
)

__all__ = [
    # Core blocks
    "Block",
    "SequentialBlock",
    # Factory functions
    "encoder",
    "decoder",
    "embedding",
    "positional_encoding",
    # Encoder classes
    "TransformerEncoder",
    "Encoder",
    "ENCODERS",
    # Decoder classes
    "CausalDecoder",
    "CrossAttentionDecoder",
    "Decoder",
    "DECODERS",
    # Embedding classes
    "TokenEmbedding",
    "PatchEmbedding",
    "FeatureEmbedding",
    "EMBEDDINGS",
    # Positional encoding classes
    "AbsolutePositionalEncoding",
    "RelativePositionalEncoding",
    "RotaryPositionalEncoding",
    "PositionalEncoding",
    "POSITIONAL_ENCODINGS",
]

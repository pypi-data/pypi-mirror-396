"""Embedding blocks for transformer models.

Usage:
    # Via factory function
    emb = embedding("token", vocab_size=32000, embed_dim=512)
    emb = embedding("patch", image_size=224, embed_dim=768)
    
    # Direct import
    from composennent.basic.embedding import TokenEmbedding, PatchEmbedding
"""

from typing import Dict, Any, Type
from .token import TokenEmbedding
from .patch import PatchEmbedding
from .feature import FeatureEmbedding

# Registry of embedding types
EMBEDDINGS: Dict[str, Type] = {
    "token": TokenEmbedding,
    "text": TokenEmbedding,       # alias
    "patch": PatchEmbedding,
    "vision": PatchEmbedding,    # alias
    "image": PatchEmbedding,     # alias
    "feature": FeatureEmbedding,
    "tabular": FeatureEmbedding, # alias
}


def embedding(embedding_type: str, **kwargs) -> Any:
    """Create an embedding by type name.
    
    Args:
        embedding_type: One of "token", "patch", "feature"
        **kwargs: Arguments passed to the embedding class
        
    Returns:
        Embedding instance
        
    Example:
        >>> emb = embedding("token", vocab_size=32000, embed_dim=512)
        >>> emb = embedding("patch", image_size=224, embed_dim=768)
    """
    if embedding_type not in EMBEDDINGS:
        available = ", ".join(f'"{k}"' for k in EMBEDDINGS.keys())
        raise ValueError(f"Unknown embedding type: '{embedding_type}'. Choose from: {available}")
    return EMBEDDINGS[embedding_type](**kwargs)


__all__ = [
    "embedding",
    "TokenEmbedding",
    "PatchEmbedding",
    "FeatureEmbedding",
    "EMBEDDINGS",
]

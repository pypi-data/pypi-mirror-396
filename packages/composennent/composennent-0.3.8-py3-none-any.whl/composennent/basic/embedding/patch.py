"""Patch embedding for vision transformers (ViT)."""

import torch
import torch.nn as nn

from composennent.basic.block import Block


class PatchEmbedding(Block):
    """Patch embedding for Vision Transformers (ViT).

    Splits image into patches and projects each patch to embedding dim.
    Used in ViT, CLIP, DINO.

    Args:
        image_size: Input image size (assumed square).
        patch_size: Size of each patch (assumed square). Defaults to 16.
        in_channels: Number of input channels. Defaults to 3 (RGB).
        embed_dim: Embedding dimension.

    Example:
        >>> emb = PatchEmbedding(image_size=224, patch_size=16, embed_dim=768)
        >>> img = torch.randn(2, 3, 224, 224)
        >>> x = emb(img)  # (2, 196, 768) for 14x14 patches
    """

    def __init__(
        self,
        image_size: int,
        patch_size: int = 16,
        in_channels: int = 3,
        embed_dim: int = 768,
    ) -> None:
        super().__init__()
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_patches = (image_size // patch_size) ** 2
        self.embed_dim = embed_dim

        # Conv2d is equivalent to patch extraction + linear projection
        self.projection = nn.Conv2d(
            in_channels,
            embed_dim,
            kernel_size=patch_size,
            stride=patch_size,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Convert image to patch embeddings.
        
        Args:
            x: Image tensor of shape (batch, channels, height, width).
            
        Returns:
            Patch embeddings of shape (batch, num_patches, embed_dim).
        """
        # (B, C, H, W) -> (B, embed_dim, H/P, W/P)
        x = self.projection(x)
        # (B, embed_dim, H/P, W/P) -> (B, embed_dim, num_patches) -> (B, num_patches, embed_dim)
        x = x.flatten(2).transpose(1, 2)
        return x

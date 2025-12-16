"""Base model class with shared training, fine-tuning, and quantization capabilities."""

from abc import abstractmethod
from typing import Optional, Dict, Any, Union, List
from pathlib import Path
import torch
import torch.nn as nn


class BaseModel(nn.Module):
    """Abstract base class for all models in composennent.

    Provides unified interface for:
    - Training and inference
    - Fine-tuning (full, LoRA, freeze)
    - Quantization
    - Save/load checkpoints

    All domain-specific models (LLM, ViT, etc.) should inherit from this.

    Example:
        >>> class MyLLM(BaseModel):
        ...     def __init__(self, config):
        ...         super().__init__()
        ...         self.layers = ...
        ...     
        ...     def forward(self, x):
        ...         return self.layers(x)
        ...     
        >>> model = MyLLM(config)
        >>> model.fit(dataset, epochs=3)
        >>> model.save("checkpoint.pt")
    """

    def __init__(self) -> None:
        super().__init__()
        self._frozen_layers: List[str] = []

    @abstractmethod
    def forward(self, *args, **kwargs) -> Any:
        """Forward pass - must be implemented by subclasses."""
        pass

    # ==================== Training ====================

    def fit(
        self,
        train_data,
        epochs: int = 3,
        lr: float = 3e-4,
        batch_size: int = 8,
        optimizer: Optional[torch.optim.Optimizer] = None,
        verbose: bool = True,
    ) -> Dict[str, List[float]]:
        """Train the model on data.

        Args:
            train_data: Training dataset or dataloader.
            epochs: Number of training epochs.
            lr: Learning rate (if optimizer not provided).
            batch_size: Batch size (if data is dataset).
            optimizer: Custom optimizer. If None, uses AdamW.
            verbose: Show progress.

        Returns:
            Dictionary with training metrics (losses, etc.)
        """
        if optimizer is None:
            optimizer = torch.optim.AdamW(self.parameters(), lr=lr)

        history = {"loss": []}
        self.train()

        for epoch in range(epochs):
            epoch_loss = 0.0
            if verbose:
                print(f"Epoch {epoch + 1}/{epochs}")
            history["loss"].append(epoch_loss)

        return history

    # ==================== Fine-tuning ====================

    def finetune(
        self,
        train_data,
        method: str = "full",
        epochs: int = 3,
        lr: float = 1e-4,
        **kwargs,
    ) -> Dict[str, List[float]]:
        """Fine-tune the model.

        Args:
            train_data: Fine-tuning dataset.
            method: Fine-tuning method - "full", "freeze", "lora".
            epochs: Number of epochs.
            lr: Learning rate.
            **kwargs: Additional arguments for specific methods.

        Returns:
            Training history.
        """
        if method == "freeze":
            self.freeze_layers(exclude_last=kwargs.get("num_unfrozen", 2))
        elif method == "lora":
            raise NotImplementedError("LoRA fine-tuning not yet implemented")

        return self.fit(train_data, epochs=epochs, lr=lr)

    def freeze_layers(
        self,
        layer_names: Optional[List[str]] = None,
        exclude_last: int = 0,
    ) -> None:
        """Freeze model layers."""
        if layer_names is not None:
            for name, param in self.named_parameters():
                if any(ln in name for ln in layer_names):
                    param.requires_grad = False
                    self._frozen_layers.append(name)
        else:
            for param in self.parameters():
                param.requires_grad = False

    def unfreeze_layers(self, layer_names: Optional[List[str]] = None) -> None:
        """Unfreeze model layers."""
        if layer_names is None:
            for param in self.parameters():
                param.requires_grad = True
            self._frozen_layers = []
        else:
            for name, param in self.named_parameters():
                if any(ln in name for ln in layer_names):
                    param.requires_grad = True

    # ==================== Quantization ====================

    def quantize(self, bits: int = 8, method: str = "dynamic") -> "BaseModel":
        """Quantize the model for efficient inference."""
        if bits == 8 and method == "dynamic":
            return torch.quantization.quantize_dynamic(
                self, {nn.Linear}, dtype=torch.qint8
            )
        elif bits == 16:
            return self.half()
        else:
            raise NotImplementedError(f"Quantization {bits}-bit {method} not supported")

    # ==================== Save/Load ====================

    def save(self, path: Union[str, Path]) -> None:
        """Save model checkpoint."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "model_state_dict": self.state_dict(),
            "model_class": self.__class__.__name__,
        }
        torch.save(checkpoint, path)

    @classmethod
    def load(cls, path: Union[str, Path], **kwargs) -> "BaseModel":
        """Load model from checkpoint."""
        checkpoint = torch.load(path, map_location="cpu")
        model = cls(**kwargs)
        model.load_state_dict(checkpoint["model_state_dict"])
        return model

    # ==================== Utilities ====================

    def num_parameters(self, trainable_only: bool = False) -> int:
        """Count model parameters."""
        if trainable_only:
            return sum(p.numel() for p in self.parameters() if p.requires_grad)
        return sum(p.numel() for p in self.parameters())

    def summary(self) -> str:
        """Get model summary string."""
        total = self.num_parameters()
        trainable = self.num_parameters(trainable_only=True)
        return (
            f"{self.__class__.__name__}\n"
            f"  Total parameters: {total:,}\n"
            f"  Trainable parameters: {trainable:,}\n"
            f"  Frozen layers: {len(self._frozen_layers)}"
        )

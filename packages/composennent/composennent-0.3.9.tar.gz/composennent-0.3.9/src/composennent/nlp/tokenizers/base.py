"""Base tokenizer interface following HuggingFace standards."""

from abc import ABC, abstractmethod
from typing import Union, List, Optional, Dict


class BaseTokenizer(ABC):
    """Abstract base class for all tokenizers.

    Follows HuggingFace tokenizer interface conventions for compatibility.
    Provides a unified interface for different tokenization methods
    (BPE, WordPiece, Unigram, etc.).
    """

    @abstractmethod
    def train(self, data: Union[str, List[str]], **kwargs) -> None:
        """Train the tokenizer on data.

        Args:
            data: Training data. Can be:
                - File path (str) to text file
                - List of strings
            **kwargs: Additional training arguments.
        """
        ...

    @abstractmethod
    def encode(
        self,
        text: str,
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
        truncation: bool = False,
        padding: bool = False,
    ) -> List[int]:
        """Encode text to token IDs.

        Args:
            text: Input text to encode.
            add_special_tokens: Whether to add special tokens (BOS, EOS, etc.).
            max_length: Maximum sequence length.
            truncation: Whether to truncate if longer than max_length.
            padding: Whether to pad to max_length.

        Returns:
            List of token IDs.
        """
        ...

    @abstractmethod
    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs back to text.

        Args:
            ids: List of token IDs to decode.
            skip_special_tokens: Whether to skip special tokens in output.

        Returns:
            Decoded text string.
        """
        ...

    def __call__(
        self,
        text: Union[str, List[str]],
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
        truncation: bool = False,
        padding: Union[bool, str] = False,
        return_tensors: Optional[str] = None,
        return_attention_mask: bool = True,
    ) -> Dict:
        """Tokenize text (HuggingFace-style callable interface).

        Args:
            text: Input text or list of texts.
            add_special_tokens: Whether to add special tokens.
            max_length: Maximum sequence length.
            truncation: Whether to truncate.
            padding: Padding strategy ("max_length", True, or False).
            return_tensors: "pt" for PyTorch tensors, None for lists.
            return_attention_mask: Whether to return attention mask.

        Returns:
            Dictionary with input_ids and optionally attention_mask.
        """
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text

        all_input_ids = []
        for t in texts:
            ids = self.encode(t, add_special_tokens=add_special_tokens)
            
            # Truncation
            if truncation and max_length and len(ids) > max_length:
                ids = ids[:max_length]
            
            all_input_ids.append(ids)

        # Padding
        if padding:
            if padding == "max_length" and max_length:
                pad_len = max_length
            else:
                pad_len = max(len(ids) for ids in all_input_ids)
            
            attention_mask = []
            for i, ids in enumerate(all_input_ids):
                mask = [1] * len(ids) + [0] * (pad_len - len(ids))
                ids_padded = ids + [self.pad_token_id] * (pad_len - len(ids))
                all_input_ids[i] = ids_padded
                attention_mask.append(mask)
        else:
            attention_mask = [[1] * len(ids) for ids in all_input_ids]

        result = {"input_ids": all_input_ids}
        if return_attention_mask:
            result["attention_mask"] = attention_mask

        # Convert to tensors if requested
        if return_tensors == "pt":
            import torch
            result["input_ids"] = torch.tensor(result["input_ids"])
            if return_attention_mask:
                result["attention_mask"] = torch.tensor(result["attention_mask"])

        # Unwrap single item
        if isinstance(text, str) and return_tensors is None:
            result["input_ids"] = result["input_ids"][0]
            if return_attention_mask:
                result["attention_mask"] = result["attention_mask"][0]

        return result

    @property
    @abstractmethod
    def vocab_size(self) -> int:
        """Return the vocabulary size."""
        ...

    # ==================== HuggingFace Standard Token IDs ====================

    @property
    def pad_token_id(self) -> int:
        """Return the padding token ID."""
        return 0

    @property
    def bos_token_id(self) -> int:
        """Return the beginning-of-sequence token ID."""
        return 1

    @property
    def eos_token_id(self) -> int:
        """Return the end-of-sequence token ID."""
        return 2

    @property
    def unk_token_id(self) -> int:
        """Return the unknown token ID."""
        return 1

    # Legacy aliases (for backward compatibility)
    @property
    def pad_id(self) -> int:
        """Alias for pad_token_id."""
        return self.pad_token_id

    @property
    def bos_id(self) -> int:
        """Alias for bos_token_id."""
        return self.bos_token_id

    @property
    def eos_id(self) -> int:
        """Alias for eos_token_id."""
        return self.eos_token_id

    @abstractmethod
    def save(self, path: str) -> None:
        """Save tokenizer model to file.

        Args:
            path: Path to save the tokenizer model.
        """
        ...

    @classmethod
    @abstractmethod
    def from_pretrained(cls, path: str):
        """Load pretrained tokenizer from file.

        Args:
            path: Path to the saved tokenizer model.

        Returns:
            Loaded tokenizer instance.
        """
        ...

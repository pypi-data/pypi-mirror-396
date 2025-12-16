"""SentencePiece tokenizer wrapper following HuggingFace standards."""

import os
import tempfile
from typing import Union, List, Optional
from .base import BaseTokenizer

try:
    import sentencepiece as spm
except ImportError:
    raise ImportError(
        "sentencepiece is required for SentencePieceTokenizer. "
        "Install it with: pip install sentencepiece"
    )


class SentencePieceTokenizer(BaseTokenizer):
    """Wrapper around SentencePiece for BPE and Unigram tokenization.

    Follows HuggingFace tokenizer interface for compatibility.

    Args:
        model_type: Type of model ('bpe', 'unigram', 'word', 'char'). Defaults to 'bpe'.
        vocab_size: Target vocabulary size. Defaults to 32000.
        model_prefix: Prefix for saved model files. Defaults to 'tokenizer'.
        **kwargs: Additional arguments passed to SentencePiece trainer.

    Example:
        >>> tokenizer = SentencePieceTokenizer(model_type='bpe', vocab_size=32000)
        >>> tokenizer.train(texts)
        >>> 
        >>> # HuggingFace-style usage
        >>> output = tokenizer("Hello world!", return_tensors="pt")
        >>> print(output["input_ids"])
        >>> 
        >>> # Simple usage
        >>> ids = tokenizer.encode("Hello world!")
        >>> text = tokenizer.decode(ids)
    """

    def __init__(
        self,
        model_type: str = 'bpe',
        vocab_size: int = 32000,
        model_prefix: str = 'tokenizer',
        **kwargs
    ) -> None:
        if model_type not in ['bpe', 'unigram', 'word', 'char']:
            raise ValueError(
                f"model_type must be one of ['bpe', 'unigram', 'word', 'char'], "
                f"got '{model_type}'"
            )

        self.model_type = model_type
        self._vocab_size = vocab_size
        self.model_prefix = model_prefix
        self.kwargs = kwargs
        self.sp = None

    def train(
        self,
        data: Union[str, List[str]],
        output_dir: Optional[str] = None,
        **kwargs
    ) -> None:
        """Train the SentencePiece tokenizer.

        Args:
            data: Training data. Can be:
                - Path to a text file
                - List of strings (will be written to temp file)
            output_dir: Directory to save the model. If None, uses current directory.
        """
        if isinstance(data, list):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
                for line in data:
                    f.write(line + '\n')
                input_file = f.name
            temp_file = True
        elif isinstance(data, str) and os.path.isfile(data):
            input_file = data
            temp_file = False
        else:
            raise ValueError(
                "data must be either a file path or a list of strings"
            )

        if output_dir is None:
            output_dir = '.'
        os.makedirs(output_dir, exist_ok=True)

        model_path = os.path.join(output_dir, self.model_prefix)

        train_args = {
            'input': input_file,
            'model_prefix': model_path,
            'model_type': self.model_type,
            'vocab_size': self._vocab_size,
            'pad_id': 0,
            'unk_id': 1,
            'bos_id': 2,
            'eos_id': 3,
        }
        train_args.update(self.kwargs)
        train_args.update(kwargs)

        spm.SentencePieceTrainer.train(**train_args)

        if temp_file:
            os.remove(input_file)

        self.sp = spm.SentencePieceProcessor()
        self.sp.load(f'{model_path}.model')

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
            add_special_tokens: Whether to add BOS/EOS tokens.
            max_length: Maximum sequence length.
            truncation: Whether to truncate.
            padding: Whether to pad.

        Returns:
            List of token IDs.
        """
        if self.sp is None:
            raise RuntimeError(
                "Tokenizer not trained or loaded. "
                "Call train() or use from_pretrained() first."
            )

        if add_special_tokens:
            ids = [self.sp.bos_id()] + self.sp.encode(text) + [self.sp.eos_id()]
        else:
            ids = self.sp.encode(text)

        # Truncation
        if truncation and max_length and len(ids) > max_length:
            ids = ids[:max_length]

        # Padding
        if padding and max_length and len(ids) < max_length:
            ids = ids + [self.pad_token_id] * (max_length - len(ids))

        return ids

    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs back to text.

        Args:
            ids: List of token IDs to decode.
            skip_special_tokens: Whether to skip special tokens.

        Returns:
            Decoded text string.
        """
        if self.sp is None:
            raise RuntimeError(
                "Tokenizer not trained or loaded. "
                "Call train() or use from_pretrained() first."
            )

        if skip_special_tokens:
            special_ids = {self.sp.pad_id(), self.sp.bos_id(), self.sp.eos_id()}
            ids = [i for i in ids if i not in special_ids]

        return self.sp.decode(ids)

    @property
    def vocab_size(self) -> int:
        """Return the vocabulary size."""
        if self.sp is not None:
            return self.sp.get_piece_size()
        return self._vocab_size

    # ==================== HuggingFace Standard Token IDs ====================

    @property
    def pad_token_id(self) -> int:
        """Return the padding token ID."""
        if self.sp is not None:
            return self.sp.pad_id()
        return 0

    @property
    def bos_token_id(self) -> int:
        """Return the beginning-of-sequence token ID."""
        if self.sp is not None:
            return self.sp.bos_id()
        return 2

    @property
    def eos_token_id(self) -> int:
        """Return the end-of-sequence token ID."""
        if self.sp is not None:
            return self.sp.eos_id()
        return 3

    @property
    def unk_token_id(self) -> int:
        """Return the unknown token ID."""
        if self.sp is not None:
            return self.sp.unk_id()
        return 1

    # Legacy aliases
    @property
    def pad_id(self) -> int:
        return self.pad_token_id

    @property
    def bos_id(self) -> int:
        return self.bos_token_id

    @property
    def eos_id(self) -> int:
        return self.eos_token_id

    def save(self, path: str) -> None:
        """Save tokenizer model to file.

        Args:
            path: Path to save the tokenizer model.
        """
        if self.sp is None:
            raise RuntimeError("No trained model to save.")

        import shutil
        model_file = f'{self.model_prefix}.model'
        if os.path.exists(model_file):
            shutil.copy(model_file, path)
        else:
            raise FileNotFoundError(f"Model file {model_file} not found.")

    @classmethod
    def from_pretrained(cls, path: str) -> 'SentencePieceTokenizer':
        """Load pretrained tokenizer from file.

        Args:
            path: Path to the saved SentencePiece model (.model file).

        Returns:
            Loaded SentencePieceTokenizer instance.
        """
        tokenizer = cls()
        tokenizer.sp = spm.SentencePieceProcessor()
        tokenizer.sp.load(path)
        tokenizer._vocab_size = tokenizer.sp.get_piece_size()
        return tokenizer

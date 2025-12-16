# composennent

[![PyPI version](https://badge.fury.io/py/composennent.svg)](https://badge.fury.io/py/composennent)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Composable neural network components for building models in PyTorch.**

Composennent provides modular, reusable building blocks for constructing transformer-based models. Train GPT, BERT, and other architectures with minimal code.

## Features

- 🧩 **Modular Components**: Encoder, Decoder, Attention blocks that compose together
- 🚀 **Built-in Training**: Pre-training and fine-tuning with a single method call
- 📝 **Multiple Architectures**: GPT, BERT, Seq2Seq support out of the box
- 🔧 **Tokenizer Support**: WordPiece and SentencePiece tokenizers included
- ⚡ **Mixed Precision**: Automatic mixed precision (AMP) support
- 🎯 **Instruction Tuning**: Fine-tune models on instruction datasets (Alpaca format)

## Installation

```bash
pip install composennent
```

For tokenizer support:
```bash
pip install composennent[tokenizers]
```

For development:
```bash
pip install composennent[dev]
```

## Quick Start

### Pre-train a GPT Model

```python
import torch
from composennent.nlp.transformers import GPT
from composennent.nlp.tokenizers import SentencePieceTokenizer

# Create model
model = GPT(
    vocab_size=32000,
    latent_dim=512,
    num_heads=8,
    num_layers=6,
    max_seq_len=512,
)

# Load tokenizer
tokenizer = SentencePieceTokenizer.from_pretrained("tokenizer.model")

# Pre-train
texts = ["Your training data here...", ...]
model.pretrain(
    texts=texts,
    tokenizer=tokenizer,
    epochs=3,
    batch_size=16,
    device="cuda",
)

# Save
model.save("my_model.pt")
```

### Fine-tune on Instructions

```python
# Load pre-trained model
model = GPT.load("my_model.pt", device="cuda")

# Instruction data (Alpaca format)
instruction_data = [
    {
        "instruction": "What is the capital of France?",
        "input": "",
        "output": "The capital of France is Paris."
    },
    # ... more examples
]

# Fine-tune
model.fine_tune(
    data=instruction_data,
    tokenizer=tokenizer,
    epochs=2,
    lr=5e-5,
    mask_prompt=True,  # Only compute loss on outputs
)
```

### Generate Text

```python
prompt = tokenizer.encode("What is")
generated = model.generate(
    input_ids=prompt,
    max_length=100,
    temperature=0.8,
)
print(tokenizer.decode(generated[0].tolist()))
```

## Modules

| Module | Description |
|--------|-------------|
| `composennent.basic` | Core building blocks (Encoder, Decoder, Block) |
| `composennent.attention` | Attention mechanisms and masks |
| `composennent.nlp.transformers` | GPT, BERT, and other transformer models |
| `composennent.nlp.tokenizers` | WordPiece and SentencePiece tokenizers |
| `composennent.training` | Training utilities and trainer classes |
| `composennent.expert` | Mixture of Experts components |
| `composennent.vision` | Vision transformer components |
| `composennent.utils` | Utility functions |

## Training API

For more control over training, use the trainer classes directly:

```python
from composennent.training import CausalLMTrainer, train

# Option 1: Use the train() convenience function
train(model, texts, tokenizer, model_type="causal_lm", epochs=5)

# Option 2: Use trainer class directly
trainer = CausalLMTrainer(model, tokenizer, device="cuda")
trainer.train(texts, epochs=5, batch_size=16)
trainer.save_checkpoint("checkpoint.pt")
```

Available trainers:
- `CausalLMTrainer` - GPT-style next-token prediction
- `MaskedLMTrainer` - BERT-style masked language modeling
- `Seq2SeqTrainer` - Encoder-decoder models
- `MultiTaskTrainer` - Multi-task learning (MLM + NSP)
- `CustomTrainer` - Custom loss functions

## Requirements

- Python >= 3.8
- PyTorch >= 2.0.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install dev dependencies (`pip install -e ".[dev]"`)
4. Run tests (`pytest`)
5. Run formatters (`black . && ruff check .`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Repository](https://github.com/DataOpsFusion/composennent)
- [PyPI](https://pypi.org/project/composennent/)
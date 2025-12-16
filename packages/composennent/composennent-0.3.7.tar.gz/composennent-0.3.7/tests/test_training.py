"""Tests for composennent.training module."""

import pytest
import torch

from composennent.training import (
    BaseTrainer,
    CausalLMTrainer,
    MaskedLMTrainer,
    Batch,
    create_dataloader,
)


class TestBatch:
    """Tests for the Batch dataclass."""
    
    def test_batch_creation(self, device):
        """Test Batch can be created with required fields."""
        batch = Batch(
            input_ids=torch.tensor([[1, 2, 3]]),
            attention_mask=torch.tensor([[1, 1, 1]]),
            labels=torch.tensor([[1, 2, 3]]),
        )
        assert batch.input_ids.shape == (1, 3)
        assert batch.attention_mask.shape == (1, 3)
        assert batch.labels.shape == (1, 3)
    
    def test_batch_optional_fields(self):
        """Test Batch with optional fields."""
        batch = Batch(
            input_ids=torch.tensor([[1, 2, 3]]),
            attention_mask=torch.tensor([[1, 1, 1]]),
            labels=torch.tensor([[1, 2, 3]]),
            pixel_values=torch.randn(1, 3, 224, 224),  # For vision models
        )
        assert batch.pixel_values is not None


class TestCreateDataloader:
    """Tests for the create_dataloader function."""
    
    def test_create_dataloader_basic(self, sample_texts, mock_tokenizer):
        """Test dataloader creation with basic inputs."""
        dataloader = create_dataloader(
            texts=sample_texts,
            tokenizer=mock_tokenizer,
            batch_size=2,
            max_length=32,
        )
        assert dataloader is not None
        
        # Get first batch
        batch = next(iter(dataloader))
        assert hasattr(batch, 'input_ids')
        assert hasattr(batch, 'attention_mask')
        assert hasattr(batch, 'labels')
    
    def test_create_dataloader_batch_size(self, sample_texts, mock_tokenizer):
        """Test that dataloader respects batch size."""
        batch_size = 2
        dataloader = create_dataloader(
            texts=sample_texts,
            tokenizer=mock_tokenizer,
            batch_size=batch_size,
            max_length=32,
        )
        
        batch = next(iter(dataloader))
        assert batch.input_ids.shape[0] == batch_size


class SimpleModel(torch.nn.Module):
    """Simple model for testing trainers."""
    
    def __init__(self, vocab_size, hidden_dim):
        super().__init__()
        self.embedding = torch.nn.Embedding(vocab_size, hidden_dim)
        self.linear = torch.nn.Linear(hidden_dim, vocab_size)
        self.vocab_size = vocab_size
    
    def forward(self, input_ids, attention_mask=None, **kwargs):
        x = self.embedding(input_ids)
        logits = self.linear(x)
        return {"logits": logits}


class TestCausalLMTrainer:
    """Tests for CausalLMTrainer class."""
    
    def test_trainer_instantiation(self, mock_tokenizer, device):
        """Test CausalLMTrainer can be instantiated."""
        model = SimpleModel(vocab_size=1000, hidden_dim=64)
        trainer = CausalLMTrainer(
            model=model,
            tokenizer=mock_tokenizer,
            device=device,
            use_amp=False,  # Disable AMP for CPU testing
        )
        assert trainer is not None
        assert trainer.model is model
    
    def test_trainer_prepare_batch(self, mock_tokenizer, device):
        """Test batch preparation."""
        model = SimpleModel(vocab_size=1000, hidden_dim=64)
        trainer = CausalLMTrainer(
            model=model,
            tokenizer=mock_tokenizer,
            device=device,
            use_amp=False,
        )
        
        batch_data = Batch(
            input_ids=torch.tensor([[1, 2, 3]]),
            attention_mask=torch.tensor([[1, 1, 1]]),
            labels=torch.tensor([[1, 2, 3]]),
        )
        
        prepared = trainer.prepare_batch(batch_data)
        assert prepared.input_ids.device.type == device
    
    def test_trainer_compute_loss(self, mock_tokenizer, device):
        """Test loss computation."""
        model = SimpleModel(vocab_size=1000, hidden_dim=64).to(device)
        trainer = CausalLMTrainer(
            model=model,
            tokenizer=mock_tokenizer,
            device=device,
            use_amp=False,
        )
        
        batch = Batch(
            input_ids=torch.tensor([[1, 2, 3, 4]]).to(device),
            attention_mask=torch.tensor([[1, 1, 1, 1]]).to(device),
            labels=torch.tensor([[1, 2, 3, 4]]).to(device),
        )
        
        # Get model output
        model_output = model(batch.input_ids, batch.attention_mask)
        
        # Compute loss
        loss = trainer.compute_loss(model_output, batch)
        
        assert loss is not None
        assert loss.dim() == 0  # Scalar loss
        assert not torch.isnan(loss)


class TestMaskedLMTrainer:
    """Tests for MaskedLMTrainer class."""
    
    def test_masked_trainer_instantiation(self, mock_tokenizer, device):
        """Test MaskedLMTrainer can be instantiated."""
        model = SimpleModel(vocab_size=1000, hidden_dim=64)
        
        # Modify model to output mlm_logits
        class MLMModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.embedding = torch.nn.Embedding(1000, 64)
                self.linear = torch.nn.Linear(64, 1000)
            
            def forward(self, input_ids, **kwargs):
                x = self.embedding(input_ids)
                return {"mlm_logits": self.linear(x)}
        
        mlm_model = MLMModel()
        trainer = MaskedLMTrainer(
            model=mlm_model,
            tokenizer=mock_tokenizer,
            device=device,
            use_amp=False,
        )
        assert trainer is not None

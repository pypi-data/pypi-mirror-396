"""Tests for composennent.basic module."""

import pytest
import torch
import torch.nn as nn

from composennent.basic import Decoder, Encoder, Block, SequentialBlock, CrossAttentionDecoder


class TestBlock:
    """Tests for the Block base class."""
    
    def test_block_is_module(self):
        """Block should inherit from nn.Module."""
        assert issubclass(Block, torch.nn.Module)
    
    def test_block_is_abstract(self):
        """Block should be abstract and not instantiable directly."""
        with pytest.raises(TypeError):
            Block()
    
    def test_custom_block_implementation(self, device):
        """Test creating a custom Block subclass."""
        class LinearBlock(Block):
            def __init__(self, in_features, out_features):
                super().__init__()
                self.linear = nn.Linear(in_features, out_features)
            
            def forward(self, x):
                return self.linear(x)
        
        block = LinearBlock(64, 128).to(device)
        x = torch.randn(2, 64).to(device)
        output = block(x)
        
        assert output.shape == (2, 128)
        assert not torch.isnan(output).any()


class TestSequentialBlock:
    """Tests for the SequentialBlock class."""
    
    def test_sequential_instantiation(self):
        """Test SequentialBlock can be instantiated."""
        seq = SequentialBlock(
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
        )
        assert seq is not None
        assert len(seq.layers) == 3
    
    def test_sequential_forward(self, device):
        """Test SequentialBlock forward pass."""
        seq = SequentialBlock(
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 32),
        ).to(device)
        
        x = torch.randn(2, 64).to(device)
        output = seq(x)
        
        assert output.shape == (2, 32)
        assert not torch.isnan(output).any()
    
    def test_sequential_with_block_layers(self, small_model_config, device):
        """Test SequentialBlock passes extra args to Block layers."""
        # Create a custom Block that uses extra arguments
        class AttentionBlock(Block):
            def __init__(self, dim):
                super().__init__()
                self.attn = nn.MultiheadAttention(dim, num_heads=4, batch_first=True)
                self.norm = nn.LayerNorm(dim)
            
            def forward(self, x, key_padding_mask=None):
                normed = self.norm(x)
                out, _ = self.attn(normed, normed, normed, key_padding_mask=key_padding_mask)
                return x + out
        
        dim = small_model_config["latent_dim"]
        seq = SequentialBlock(
            nn.LayerNorm(dim),  # Regular layer
            AttentionBlock(dim),  # Block layer - receives extra args
        ).to(device)
        
        batch_size, seq_len = 2, 16
        x = torch.randn(batch_size, seq_len, dim).to(device)
        mask = torch.zeros(batch_size, seq_len, dtype=torch.bool).to(device)
        mask[:, -4:] = True
        
        # Should pass mask to AttentionBlock but not to LayerNorm
        output = seq(x, key_padding_mask=mask)
        
        assert output.shape == x.shape
    
    def test_sequential_empty(self, device):
        """Test SequentialBlock with no layers."""
        seq = SequentialBlock().to(device)
        x = torch.randn(2, 64).to(device)
        output = seq(x)
        
        # Should return input unchanged
        assert torch.allclose(output, x)
    
    def test_sequential_single_layer(self, device):
        """Test SequentialBlock with single layer."""
        seq = SequentialBlock(nn.Linear(64, 32)).to(device)
        x = torch.randn(2, 64).to(device)
        output = seq(x)
        
        assert output.shape == (2, 32)


class TestEncoder:
    """Tests for the Encoder class."""
    
    def test_encoder_instantiation(self, small_model_config):
        """Test that Encoder can be instantiated."""
        encoder = Encoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        )
        assert encoder is not None
        assert encoder.latent_dim == small_model_config["latent_dim"]
    
    def test_encoder_instantiation_with_all_params(self):
        """Test Encoder with all parameters specified."""
        encoder = Encoder(
            latent_dim=128,
            num_heads=4,
            dropout=0.2,
            mlp_ratio=2,
            return_attention=True,
        )
        assert encoder.latent_dim == 128
        assert encoder.return_attention is True
    
    def test_encoder_forward(self, small_model_config, device):
        """Test Encoder forward pass."""
        encoder = Encoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        ).to(device)
        
        batch_size = 2
        seq_len = 16
        x = torch.randn(batch_size, seq_len, small_model_config["latent_dim"]).to(device)
        
        output = encoder(x)
        
        assert output.shape == x.shape
        assert not torch.isnan(output).any()
    
    def test_encoder_with_mask(self, small_model_config, device):
        """Test Encoder forward pass with attention mask."""
        encoder = Encoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        ).to(device)
        
        batch_size = 2
        seq_len = 16
        x = torch.randn(batch_size, seq_len, small_model_config["latent_dim"]).to(device)
        key_padding_mask = torch.zeros(batch_size, seq_len, dtype=torch.bool).to(device)
        key_padding_mask[:, -4:] = True  # Mask last 4 positions
        
        output = encoder(x, key_padding_mask=key_padding_mask)
        
        assert output.shape == x.shape
    
    def test_encoder_return_attention(self, small_model_config, device):
        """Test Encoder returns attention weights."""
        encoder = Encoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
            return_attention=True,
        ).to(device)
        
        batch_size = 2
        seq_len = 16
        x = torch.randn(batch_size, seq_len, small_model_config["latent_dim"]).to(device)
        
        output, attn_weights = encoder(x)
        
        assert output.shape == x.shape
        assert attn_weights is not None
        # New MultiHeadAttention returns (batch, num_heads, seq, seq)
        assert attn_weights.shape == (batch_size, small_model_config["num_heads"], seq_len, seq_len)
    
    def test_encoder_return_attention_override(self, small_model_config, device):
        """Test Encoder attention return can be overridden at call time."""
        encoder = Encoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
            return_attention=False,  # Default is False
        ).to(device)
        
        batch_size = 2
        seq_len = 16
        x = torch.randn(batch_size, seq_len, small_model_config["latent_dim"]).to(device)
        
        # Override to True at call time
        output, attn_weights = encoder(x, return_attention=True)
        
        assert attn_weights is not None
    
    def test_encoder_different_mlp_ratios(self, device):
        """Test Encoder with different MLP expansion ratios."""
        for mlp_ratio in [1, 2, 4, 8]:
            encoder = Encoder(
                latent_dim=64,
                num_heads=4,
                mlp_ratio=mlp_ratio,
            ).to(device)
            
            x = torch.randn(2, 8, 64).to(device)
            output = encoder(x)
            
            assert output.shape == x.shape
    
    def test_encoder_stacked(self, small_model_config, device):
        """Test stacking multiple Encoder layers."""
        num_layers = 3
        encoders = nn.ModuleList([
            Encoder(
                latent_dim=small_model_config["latent_dim"],
                num_heads=small_model_config["num_heads"],
            )
            for _ in range(num_layers)
        ]).to(device)
        
        x = torch.randn(2, 16, small_model_config["latent_dim"]).to(device)
        
        for encoder in encoders:
            x = encoder(x)
        
        assert x.shape == (2, 16, small_model_config["latent_dim"])
        assert not torch.isnan(x).any()


class TestDecoder:
    """Tests for the Decoder class."""
    
    def test_decoder_instantiation(self, small_model_config):
        """Test that Decoder can be instantiated."""
        decoder = Decoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        )
        assert decoder is not None
        assert decoder.latent_dim == small_model_config["latent_dim"]
    
    def test_decoder_instantiation_with_all_params(self):
        """Test Decoder with all parameters specified."""
        decoder = Decoder(
            latent_dim=128,
            num_heads=4,
            dropout=0.2,
            mlp_ratio=2,
            return_attention=True,
        )
        assert decoder.latent_dim == 128
        assert decoder.return_attention is True
    
    def test_decoder_forward_self_attention_only(self, small_model_config, device):
        """Test Decoder forward pass with only self-attention (GPT-style)."""
        decoder = Decoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        ).to(device)
        
        batch_size = 2
        seq_len = 16
        x = torch.randn(batch_size, seq_len, small_model_config["latent_dim"]).to(device)
        
        output = decoder(x)
        
        assert output.shape == x.shape
        assert not torch.isnan(output).any()
    
    def test_decoder_forward_with_memory(self, small_model_config, device):
        """Test CrossAttentionDecoder forward pass with cross-attention to encoder output."""
        dec = CrossAttentionDecoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        ).to(device)
        
        batch_size = 2
        tgt_len = 16
        src_len = 20
        x = torch.randn(batch_size, tgt_len, small_model_config["latent_dim"]).to(device)
        memory = torch.randn(batch_size, src_len, small_model_config["latent_dim"]).to(device)
        
        output, _ = dec(x, memory=memory)
        
        assert output.shape == x.shape
        assert not torch.isnan(output).any()
    
    def test_decoder_return_attention(self, small_model_config, device):
        """Test CausalDecoder returns attention weights when requested."""
        decoder = Decoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
            return_attention=True,
        ).to(device)
        
        batch_size = 2
        seq_len = 16
        x = torch.randn(batch_size, seq_len, small_model_config["latent_dim"]).to(device)
        
        output, attn_weights = decoder(x)
        
        assert output.shape == x.shape
        assert attn_weights is not None
    
    def test_decoder_return_attention_with_memory(self, small_model_config, device):
        """Test CrossAttentionDecoder returns both attention weights when memory provided."""
        dec = CrossAttentionDecoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
            return_attention=True,
        ).to(device)
        
        batch_size = 2
        tgt_len = 16
        src_len = 20
        x = torch.randn(batch_size, tgt_len, small_model_config["latent_dim"]).to(device)
        memory = torch.randn(batch_size, src_len, small_model_config["latent_dim"]).to(device)
        
        output, (self_attn, cross_attn) = dec(x, memory=memory)
        
        assert output.shape == x.shape
        assert self_attn is not None
        assert cross_attn is not None
        # New MultiHeadAttention returns (batch, num_heads, seq, seq)
        num_heads = small_model_config["num_heads"]
        assert self_attn.shape == (batch_size, num_heads, tgt_len, tgt_len)
        assert cross_attn.shape == (batch_size, num_heads, tgt_len, src_len)
    
    def test_decoder_with_causal_mask(self, small_model_config, device):
        """Test Decoder with causal attention mask."""
        decoder = Decoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        ).to(device)
        
        batch_size = 2
        seq_len = 16
        x = torch.randn(batch_size, seq_len, small_model_config["latent_dim"]).to(device)
        
        # Create causal mask
        causal_mask = torch.triu(
            torch.ones(seq_len, seq_len, dtype=torch.bool).to(device),
            diagonal=1
        )
        
        output = decoder(x, tgt_mask=causal_mask)
        
        assert output.shape == x.shape
        assert not torch.isnan(output).any()
    
    def test_decoder_with_padding_mask(self, small_model_config, device):
        """Test Decoder with target padding mask."""
        decoder = Decoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        ).to(device)
        
        batch_size = 2
        seq_len = 16
        x = torch.randn(batch_size, seq_len, small_model_config["latent_dim"]).to(device)
        
        # Create padding mask
        padding_mask = torch.zeros(batch_size, seq_len, dtype=torch.bool).to(device)
        padding_mask[:, -4:] = True  # Last 4 positions are padding
        
        output = decoder(x, tgt_key_padding_mask=padding_mask)
        
        assert output.shape == x.shape
    
    def test_decoder_stacked(self, small_model_config, device):
        """Test stacking multiple Decoder layers."""
        num_layers = 3
        decoders = nn.ModuleList([
            Decoder(
                latent_dim=small_model_config["latent_dim"],
                num_heads=small_model_config["num_heads"],
            )
            for _ in range(num_layers)
        ]).to(device)
        
        x = torch.randn(2, 16, small_model_config["latent_dim"]).to(device)
        
        for decoder in decoders:
            x = decoder(x)
        assert x.shape == (2, 16, small_model_config["latent_dim"])
        assert not torch.isnan(x).any()
    
    def test_decoder_encoder_decoder_architecture(self, small_model_config, device):
        """Test CrossAttentionDecoder in encoder-decoder architecture."""
        enc = Encoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        ).to(device)
        dec = CrossAttentionDecoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
        ).to(device)
        
        batch_size = 2
        src_len = 20
        tgt_len = 16
        
        # Encoder input
        src = torch.randn(batch_size, src_len, small_model_config["latent_dim"]).to(device)
        # Decoder input
        tgt = torch.randn(batch_size, tgt_len, small_model_config["latent_dim"]).to(device)
        
        # Encoder forward
        encoder_output = enc(src)
        
        # Decoder forward with cross-attention
        decoder_output, _ = dec(tgt, memory=encoder_output)
        
        assert decoder_output.shape == tgt.shape
        assert not torch.isnan(decoder_output).any()


class TestTrainEvalModes:
    """Tests for train/eval mode behavior."""
    
    def test_encoder_eval_mode_dropout(self, small_model_config, device):
        """Test Encoder dropout is disabled in eval mode."""
        encoder = Encoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
            dropout=0.5,  # High dropout
        ).to(device)
        
        x = torch.randn(2, 16, small_model_config["latent_dim"]).to(device)
        
        encoder.eval()
        with torch.no_grad():
            out1 = encoder(x)
            out2 = encoder(x)
        
        # In eval mode, outputs should be identical
        assert torch.allclose(out1, out2)
    
    def test_decoder_eval_mode_dropout(self, small_model_config, device):
        """Test Decoder dropout is disabled in eval mode."""
        decoder = Decoder(
            latent_dim=small_model_config["latent_dim"],
            num_heads=small_model_config["num_heads"],
            dropout=0.5,
        ).to(device)
        
        x = torch.randn(2, 16, small_model_config["latent_dim"]).to(device)
        
        decoder.eval()
        with torch.no_grad():
            out1 = decoder(x)
            out2 = decoder(x)
        
        # In eval mode, outputs should be identical
        assert torch.allclose(out1, out2)


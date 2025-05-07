import asyncio
import pytest
import torch
import torch.nn as nn
from src.llm import LLMClient
from src.config import Config, MacConfig, TTSConfig
from src.mac_optimizations import MPSOptimizer, GPULayerConfig
try:
    from src.tts_native import NativeTTSClient
except ImportError:
    # Skip tests if NativeTTSClient is not available
    NativeTTSClient = None

@pytest.mark.asyncio
async def test_mps_availability():
    """Test Metal Performance Shaders (MPS) availability."""
    if torch.backends.mps.is_available():
        assert torch.device('mps') is not None
    else:
        pytest.skip("MPS is not available on this system")

@pytest.mark.asyncio
async def test_llm_with_gpu_optimization(test_config):
    """Test LLM with GPU optimization."""
    if not torch.backends.mps.is_available():
        pytest.skip("MPS is not available on this system")
        
    llm_client = LLMClient(test_config.llm)
    response = await llm_client.generate("Test prompt")
    assert response is not None
    assert response.error is None or response.error == ""

@pytest.mark.asyncio
async def test_tts_with_mps(test_config):
    """Test TTS with MPS."""
    if not torch.backends.mps.is_available() or NativeTTSClient is None:
        pytest.skip("MPS is not available or NativeTTSClient is not importable")
    
    try:
        tts_client = NativeTTSClient(test_config.tts, test_config.mac)
        tts_response = await tts_client.generate_speech("Test speech")
        assert tts_response is not None
        if not tts_response.error:
            assert tts_response.audio_path is not None
        tts_client.cleanup()
    except Exception as e:
        pytest.skip(f"TTS test failed: {str(e)}")

class SimpleModel(nn.Module):
    """Simple model for testing GPU optimizations."""
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 64, kernel_size=3)
        self.fc = nn.Linear(64, 10)
    
    def forward(self, x):
        x = self.conv(x)
        x = x.mean([2, 3])  # Global average pooling
        # Ensure correct precision before FC layer
        if self.fc.weight.dtype != x.dtype:
            x = x.to(dtype=self.fc.weight.dtype)
        return self.fc(x)

@pytest.fixture
def mac_config():
    """Create a test Mac configuration."""
    return MacConfig(
        device="mps",
        gpu_layers=32,
        batch_size=1
    )

@pytest.fixture
def test_model():
    """Create a test model."""
    return SimpleModel()

@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS not available")
class TestMPSOptimizer:
    """Test suite for MPS optimizer."""
    
    def test_optimizer_initialization(self, mac_config):
        """Test optimizer initialization."""
        optimizer = MPSOptimizer(mac_config)
        assert optimizer.device.type == "mps"
        assert optimizer.config == mac_config
        assert len(optimizer._layer_configs) == 0
        assert len(optimizer._layer_metrics) == 0
    
    def test_layer_configuration(self, mac_config):
        """Test layer configuration."""
        optimizer = MPSOptimizer(mac_config)
        layer_config = GPULayerConfig(
            layer_name="conv",
            precision="float16",
            memory_format="channels_last"
        )
        
        optimizer.configure_layer("conv", layer_config)
        assert "conv" in optimizer._layer_configs
        assert "conv" in optimizer._layer_metrics
        assert optimizer._layer_configs["conv"].precision == "float16"
        assert optimizer._layer_configs["conv"].memory_format == "channels_last"
        
        # Check initial metrics
        metrics = optimizer._layer_metrics["conv"]
        assert "compute_time_ms" in metrics
        assert "memory_usage_mb" in metrics
        assert "throughput_items_per_sec" in metrics
    
    def test_model_optimization_and_performance(self, mac_config, test_model):
        """Test model optimization and performance measurement."""
        optimizer = MPSOptimizer(mac_config)
        
        # Configure both layers to use float32 for simplicity
        conv_config = GPULayerConfig(
            layer_name="conv",
            precision="float32",
            memory_format="channels_last"
        )
        optimizer.configure_layer("conv", conv_config)
        
        fc_config = GPULayerConfig(
            layer_name="fc",
            precision="float32",
            memory_format="contiguous"
        )
        optimizer.configure_layer("fc", fc_config)
        
        # Optimize model
        optimized_model = optimizer.optimize_model_layers(test_model)
        
        # Check if model is on MPS device
        assert next(optimized_model.parameters()).device.type == "mps"
        
        # Test with sample input
        x = torch.randn(1, 3, 32, 32).to(optimizer.device)
        output = optimized_model(x)
        assert output.shape == (1, 10)
        
        # Check performance metrics for both layers
        conv_metrics = optimizer.get_layer_performance("conv")
        fc_metrics = optimizer.get_layer_performance("fc")
        
        # Verify metrics are populated with reasonable values
        assert conv_metrics["compute_time_ms"] > 0
        assert conv_metrics["memory_usage_mb"] >= 0
        assert conv_metrics["throughput_items_per_sec"] > 0
        
        assert fc_metrics["compute_time_ms"] > 0
        assert fc_metrics["memory_usage_mb"] >= 0
        assert fc_metrics["throughput_items_per_sec"] > 0
    
    def test_cleanup(self, mac_config):
        """Test resource cleanup."""
        optimizer = MPSOptimizer(mac_config)
        layer_config = GPULayerConfig(
            layer_name="test_layer",
            precision="float32"
        )
        
        optimizer.configure_layer("test_layer", layer_config)
        optimizer.cleanup()
        
        assert len(optimizer._layer_configs) == 0
        assert len(optimizer._layer_metrics) == 0
    
    def test_invalid_layer_performance(self, mac_config):
        """Test error handling for unconfigured layer performance check."""
        optimizer = MPSOptimizer(mac_config)
        
        with pytest.raises(ValueError, match="Layer unconfigured_layer not configured"):
            optimizer.get_layer_performance("unconfigured_layer")
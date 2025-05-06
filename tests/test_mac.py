import pytest
import torch
from src.config import MacConfig

def test_mps_availability():
    """Test MPS (Metal Performance Shaders) availability."""
    assert torch.backends.mps.is_available()
    assert torch.backends.mps.is_built()

def test_mac_device_creation():
    """Test Mac device creation."""
    device = torch.device("mps")
    assert str(device) == "mps"
    assert device.type == "mps"

def test_mac_config_gpu_layers():
    """Test Mac configuration GPU layers."""
    config = MacConfig(device="mps", gpu_layers=16, batch_size=1)
    assert config.gpu_layers == 16
    assert isinstance(config.gpu_layers, int)
    
    # Test invalid GPU layers
    with pytest.raises(ValueError):
        MacConfig(device="mps", gpu_layers=-1, batch_size=1)

def test_mac_config_batch_size():
    """Test Mac configuration batch size."""
    config = MacConfig(device="mps", gpu_layers=32, batch_size=2)
    assert config.batch_size == 2
    assert isinstance(config.batch_size, int)
    
    # Test invalid batch size
    with pytest.raises(ValueError):
        MacConfig(device="mps", gpu_layers=32, batch_size=0)

def test_mac_tensor_operations():
    """Test basic tensor operations on MPS device."""
    if not torch.backends.mps.is_available():
        pytest.skip("MPS not available")
    
    device = torch.device("mps")
    x = torch.tensor([1, 2, 3], device=device)
    y = torch.tensor([4, 5, 6], device=device)
    
    # Test basic operations
    z = x + y
    assert z.device.type == "mps"
    assert torch.equal(z.cpu(), torch.tensor([5, 7, 9])) 
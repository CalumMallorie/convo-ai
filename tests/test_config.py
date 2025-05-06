import pytest
from src.config import Config, LLMConfig, TTSConfig, MacConfig
import os
from pydantic import ValidationError

def test_default_config_initialization():
    """Test default configuration initialization."""
    config = Config()
    assert isinstance(config.mac, MacConfig)
    assert isinstance(config.llm, LLMConfig)
    assert isinstance(config.tts, TTSConfig)

def test_mac_config_validation():
    """Test Mac configuration validation."""
    # Test valid device values
    valid_config = MacConfig(device="mps", gpu_layers=32, batch_size=1)
    assert valid_config.device == "mps"
    
    # Test invalid device value
    with pytest.raises(ValidationError):
        MacConfig(device="invalid", gpu_layers=32, batch_size=1)

def test_llm_config_validation():
    """Test LLM configuration validation."""
    config = LLMConfig(
        base_url="http://test:1234",
        model="test-model",
        temperature=0.5,
        top_p=0.9,
        max_tokens=1000
    )
    assert config.base_url == "http://test:1234"
    assert config.model == "test-model"
    assert config.temperature == 0.5
    assert config.top_p == 0.9
    assert config.max_tokens == 1000

def test_tts_config_validation():
    """Test TTS configuration validation."""
    config = TTSConfig(
        base_url="http://test:5000",
        voice="test-voice",
        model="test-model"
    )
    assert config.base_url == "http://test:5000"
    assert config.voice == "test-voice"
    assert config.model == "test-model"

def test_config_from_env(monkeypatch):
    """Test configuration loading from environment variables."""
    # Set environment variables
    env_vars = {
        "TTS_DEVICE": "mlx",
        "GPU_LAYERS": "16",
        "TTS_MODEL_PATH": "/path/to/model",
        "OLLAMA_BASE_URL": "http://test:11434",
        "LLM_MODEL": "test-model",
        "TTS_BASE_URL": "http://test:5000",
        "TTS_VOICE": "test-voice"
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    config = Config.load()
    assert config.mac.device == "mlx"
    assert config.mac.gpu_layers == 16
    assert config.mac.model_path == "/path/to/model"
    assert config.llm.base_url == "http://test:11434"
    assert config.llm.model == "test-model"
    assert config.tts.base_url == "http://test:5000"
    assert config.tts.voice == "test-voice"

def test_config_defaults():
    """Test configuration defaults."""
    config = Config()
    assert config.mac.device == "mps"  # Default device
    assert config.mac.gpu_layers == 32  # Default GPU layers
    assert config.mac.batch_size == 1  # Default batch size
    assert config.llm.temperature == 0.7  # Default temperature
    assert config.llm.top_p == 0.9  # Default top_p
    assert config.llm.max_tokens == 2048  # Default max tokens

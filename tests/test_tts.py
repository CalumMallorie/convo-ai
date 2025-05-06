import pytest
import torch
import os
from pathlib import Path
from src.tts import TTSClient, TTSResponse
from src.config import TTSConfig

@pytest.fixture
def test_tts_config():
    """Create a test TTS configuration."""
    return TTSConfig()

@pytest.fixture
def test_tts_client(test_tts_config):
    """Create a test TTS client."""
    client = TTSClient(test_tts_config)
    yield client
    client.cleanup()

@pytest.mark.asyncio
async def test_tts_client_initialization(test_tts_config):
    """Test TTS client initialization."""
    client = TTSClient(test_tts_config)
    assert client.config == test_tts_config
    assert client.device in ["mps", "cpu"]
    assert client.sample_rate == 24000
    assert client.model is None

@pytest.mark.asyncio
async def test_tts_output_directory_creation(test_tts_client):
    """Test output directory creation."""
    test_path = "output/test/audio.wav"
    test_tts_client._ensure_output_dir(test_path)
    assert Path("output/test").exists()

@pytest.mark.asyncio
async def test_tts_generate_audio(test_tts_client):
    """Test audio generation."""
    response = await test_tts_client.generate("Hello, world!")
    assert response.error is None
    assert response.audio_path is not None
    assert response.audio_url is not None
    assert Path(response.audio_path).exists()
    assert Path(response.audio_path).suffix == ".wav"

@pytest.mark.asyncio
async def test_tts_custom_output_path(test_tts_client):
    """Test custom output path."""
    custom_path = "output/custom/test.wav"
    response = await test_tts_client.generate("Test", output_path=custom_path)
    assert response.error is None
    assert response.audio_path == custom_path
    assert response.audio_url == "/audio/test.wav"
    assert Path(custom_path).exists()

@pytest.mark.asyncio
async def test_tts_error_handling(test_tts_client):
    """Test error handling."""
    # Test empty text
    response = await test_tts_client.generate("")
    assert response.error is not None
    assert "Text cannot be empty" in response.error
    assert response.audio_path is None
    assert response.audio_url is None

@pytest.mark.asyncio
async def test_tts_resource_cleanup(test_tts_client):
    """Test resource cleanup."""
    await test_tts_client._load_model()
    assert test_tts_client.model is not None
    test_tts_client.cleanup()
    assert test_tts_client.model is None

@pytest.mark.asyncio
async def test_tts_mps_device(test_tts_client):
    """Test MPS device usage."""
    if torch.backends.mps.is_available():
        assert test_tts_client.device == "mps"
        response = await test_tts_client.generate("Test MPS")
        assert response.error is None
        assert response.audio_path is not None
        assert response.audio_url is not None
        assert Path(response.audio_path).exists()

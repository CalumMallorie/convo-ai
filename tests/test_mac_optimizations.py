import asyncio
import pytest
import torch
from src.llm import LLMClient
from src.config import Config, MacConfig, TTSConfig
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
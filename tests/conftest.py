import pytest
import os
from src.config import Config, LLMConfig, TTSConfig, MacConfig
from unittest.mock import patch, AsyncMock
import httpx
from src.llm import LLMResponse

@pytest.fixture
def test_config() -> Config:
    """Create a test configuration."""
    return Config(
        mac=MacConfig(
            device="mps",
            gpu_layers=32,
            batch_size=1
        ),
        llm=LLMConfig(
            base_url="http://localhost:11434",
            model="phi",
            temperature=0.7,
            top_p=0.9,
            max_tokens=2048
        ),
        tts=TTSConfig(
            base_url="http://localhost:5000",
            voice="alloy",
            model="csm-1b"
        )
    )

@pytest.fixture
def test_llm_config(test_config: Config) -> LLMConfig:
    """Get LLM configuration for testing."""
    return test_config.llm

@pytest.fixture
def test_tts_config(test_config: Config) -> TTSConfig:
    """Get TTS configuration for testing."""
    return test_config.tts

@pytest.fixture
def test_mac_config(test_config: Config) -> MacConfig:
    """Get Mac configuration for testing."""
    return test_config.mac

@pytest.fixture(autouse=True)
def mock_llm_in_ci():
    """Mock the LLM client in CI environments to prevent connection failures."""
    # Only mock in CI environment
    if os.environ.get('CI') == 'true':
        # Create a mock response with streaming data
        async def mock_aiter_lines():
            yield '{"response": "This is a mock response"}'
            yield '{"response": " from the CI environment."}'
        
        # Create the mock response
        mock_response = httpx.Response(200)
        mock_response.aiter_lines = mock_aiter_lines
        
        # Create the async mock for the post method
        async_mock = AsyncMock(return_value=mock_response)
        
        # Apply the patch for httpx.AsyncClient.post
        with patch.object(httpx.AsyncClient, 'post', async_mock):
            yield
    else:
        # No mocking outside CI
        yield

import pytest
import os
from src.llm import LLMClient, LLMResponse
from src.config import LLMConfig

@pytest.mark.asyncio
async def test_llm_in_ci_environment(test_llm_config):
    """Test that LLM client works in CI environment with mocking."""
    # Verify we're in CI mode
    is_ci = os.environ.get('CI') == 'true'
    
    # Create LLM client and run a test
    client = LLMClient(test_llm_config)
    response = await client.generate("Test prompt in CI")
    
    # Assertions
    assert isinstance(response, LLMResponse)
    if is_ci:
        # In CI, we should get a mock response
        assert response.text is not None
        assert response.error is None
        assert len(response.text) > 0
    else:
        # In non-CI, we might get a real response or an error if service is unavailable
        pass

@pytest.mark.asyncio
async def test_llm_streaming_in_ci(test_llm_config):
    """Test that LLM streaming works in CI environment with mocking."""
    # Verify we're in CI mode
    is_ci = os.environ.get('CI') == 'true'
    
    # Create LLM client and run a streaming test
    client = LLMClient(test_llm_config)
    responses = []
    async for chunk in client.generate_stream("Test streaming in CI"):
        responses.append(chunk)
    
    if is_ci:
        # In CI, we should get mock responses
        assert len(responses) > 0
        assert not any(chunk.startswith("Error:") for chunk in responses)
    else:
        # In non-CI, we might get real responses or errors if service is unavailable
        pass 
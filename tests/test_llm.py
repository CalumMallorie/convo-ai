import pytest
import os
from src.llm import LLMClient, LLMResponse
import httpx
import asyncio
from typing import AsyncGenerator
from unittest.mock import patch
from src.config import LLMConfig

@pytest.mark.asyncio
async def test_llm_client_initialization(test_llm_config):
    """Test LLM client initialization."""
    client = LLMClient(test_llm_config)
    assert client.config == test_llm_config
    assert client.base_url == test_llm_config.base_url
    assert client.model == test_llm_config.model
    assert client.timeout == 30.0  # Default timeout

@pytest.mark.asyncio
async def test_llm_generate_response(test_llm_config):
    """Test LLM response generation."""
    client = LLMClient(test_llm_config)
    
    # Mock response with streaming data
    async def mock_aiter_lines():
        yield '{"response": "Paris"}'
        yield '{"response": " is"}'
        yield '{"response": " the capital of France."}'
    
    # Mock the response
    mock_response = httpx.Response(200, text="")
    mock_response.aiter_lines = mock_aiter_lines
    
    # Patch the post method
    with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
        response = await client.generate("What is the capital of France?")
    
        assert isinstance(response, LLMResponse)
        assert response.text is not None
        assert len(response.text) > 0
        assert "Paris" in response.text
        assert response.error is None

@pytest.mark.asyncio
async def test_llm_error_handling(test_llm_config):
    """Test LLM error handling."""
    # Skip connection error testing in CI environment where we mock connections
    if os.environ.get('CI') == 'true':
        return
        
    # Test with invalid base URL
    invalid_config = test_llm_config.model_copy(update={"base_url": "http://invalid-url:1234"})
    client = LLMClient(invalid_config)
    response = await client.generate("Test")
    
    assert isinstance(response, LLMResponse)
    assert response.text == ""
    assert response.error is not None
    assert "Connection error:" in response.error

@pytest.mark.asyncio
async def test_llm_connection_timeout(test_llm_config):
    """Test LLM connection timeout handling."""
    # Skip in CI environment where we mock connections
    if os.environ.get('CI') == 'true':
        return
        
    client = LLMClient(test_llm_config)
    client.timeout = 0.001  # 1ms timeout
    
    response = await client.generate("Test")
    assert isinstance(response, LLMResponse)
    assert response.text == ""
    assert response.error is not None
    assert "Request timed out:" in response.error

@pytest.mark.asyncio
async def test_llm_model_change(test_llm_config):
    """Test model change functionality."""
    client = LLMClient(test_llm_config)
    original_model = client.model
    
    # Change model
    new_model = "new-model"
    client.set_model(new_model)
    assert client.model == new_model
    assert client.model != original_model

@pytest.mark.asyncio
async def test_llm_response_validation():
    """Test LLM response validation."""
    # Test valid response
    response = LLMResponse(text="Test response")
    assert response.text == "Test response"
    assert response.error is None
    
    # Test error response
    error_response = LLMResponse(text="", error="Test error")
    assert error_response.text == ""
    assert error_response.error == "Test error"

@pytest.mark.asyncio
async def test_llm_empty_prompt(test_llm_config):
    """Test LLM handling of empty prompt."""
    client = LLMClient(test_llm_config)
    response = await client.generate("")
    
    assert isinstance(response, LLMResponse)
    assert response.text == ""  # Empty text for empty prompt
    assert response.error == "Prompt cannot be empty"  # Should get an error

@pytest.mark.asyncio
async def test_llm_long_prompt(test_llm_config):
    """Test LLM handling of long prompt."""
    client = LLMClient(test_llm_config)
    long_prompt = "test " * 1000  # Very long prompt
    response = await client.generate(long_prompt)
    
    assert isinstance(response, LLMResponse)
    assert response.text is not None
    assert response.error is None

@pytest.mark.asyncio
async def test_llm_streaming_response(test_llm_config):
    """Test streaming response from LLM."""
    client = LLMClient(test_llm_config)
    prompt = "What is the capital of France?"
    
    # Collect streaming response
    responses = []
    async for chunk in client.generate_stream(prompt):
        responses.append(chunk)
    
    # Verify response
    assert len(responses) > 0
    assert not any(chunk.startswith("Error:") for chunk in responses)

@pytest.mark.asyncio
async def test_llm_streaming_error_handling(test_llm_config):
    """Test error handling in streaming responses."""
    # Skip in CI environment where we mock connections
    if os.environ.get('CI') == 'true':
        return
    
    client = LLMClient(test_llm_config)
    
    # Test empty prompt
    responses = []
    async for chunk in client.generate_stream(""):
        responses.append(chunk)
    assert len(responses) == 1
    assert responses[0] == "Error: Prompt cannot be empty"
    
    # Test invalid URL
    client.base_url = "http://invalid-url"
    responses = []
    async for chunk in client.generate_stream("test"):
        responses.append(chunk)
    assert len(responses) == 1
    assert "Error: Could not connect to LLM service" in responses[0]

@pytest.mark.asyncio
async def test_llm_streaming_timeout(test_llm_config):
    """Test timeout handling in streaming responses."""
    # Skip in CI environment where we mock connections
    if os.environ.get('CI') == 'true':
        return
    
    client = LLMClient(test_llm_config)
    client.timeout = 0.001  # Set very short timeout
    
    responses = []
    async for chunk in client.generate_stream("test"):
        responses.append(chunk)
    
    assert len(responses) == 1
    assert "Error: Request timed out" in responses[0]

@pytest.mark.asyncio
async def test_llm_streaming_invalid_json(test_llm_config):
    """Test handling of invalid JSON in streaming responses."""
    client = LLMClient(test_llm_config)
    
    # Mock response with invalid JSON
    async def mock_aiter_lines():
        yield "invalid json"
        yield '{"response": "valid response"}'
    
    # Mock the response
    mock_response = httpx.Response(200, text="")
    mock_response.aiter_lines = mock_aiter_lines
    
    # Patch the post method
    with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
        responses = []
        async for chunk in client.generate_stream("test"):
            responses.append(chunk)
        
        assert len(responses) == 1
        assert responses[0] == "valid response"

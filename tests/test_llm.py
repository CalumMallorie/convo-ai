import pytest
import os
from src.llm import LLMClient, LLMResponse
import httpx
import asyncio
from typing import AsyncGenerator, Any, Callable
from unittest.mock import patch, MagicMock
from src.config import LLMConfig

@pytest.fixture
def mock_benchmark():
    """Mock the benchmark decorator to pass through the function."""
    def mock_decorator(category: str) -> Callable:
        def wrapper(func: Callable) -> Callable:
            async def wrapped(*args: Any, **kwargs: Any) -> Any:
                return await func(*args, **kwargs)
            return wrapped
        return wrapper
    
    with patch('src.llm.benchmark', side_effect=mock_decorator) as mock:
        yield mock

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

@pytest.mark.asyncio
async def test_llm_response_metrics():
    """Test LLM response metrics."""
    # Test response with metrics
    metrics = {
        "start_metrics": {"cpu_percent": 10.0, "memory_mb": 100.0},
        "end_metrics": {"cpu_percent": 12.0, "memory_mb": 110.0},
        "memory_increase_mb": 10.0,
        "prompt_length": 10,
        "response_length": 20,
        "model": "test-model"
    }
    response = LLMResponse(text="Test response", metrics=metrics)
    assert response.text == "Test response"
    assert response.metrics == metrics
    assert response.error is None
    
    # Test response without metrics
    response_no_metrics = LLMResponse(text="Test response")
    assert response_no_metrics.text == "Test response"
    assert response_no_metrics.metrics == {}
    assert response_no_metrics.error is None

@pytest.mark.asyncio
async def test_llm_generate_with_metrics(test_llm_config, mock_benchmark):
    """Test LLM response generation with metrics collection."""
    client = LLMClient(test_llm_config)
    
    # Mock system metrics
    mock_start_metrics = {
        "cpu_percent": 10.0,
        "memory_percent": 50.0,
        "memory_mb": 1000.0,
        "num_threads": 4
    }
    mock_end_metrics = {
        "cpu_percent": 12.0,
        "memory_percent": 51.0,
        "memory_mb": 1010.0,
        "num_threads": 4
    }
    
    # Mock response with streaming data
    async def mock_aiter_lines():
        yield '{"response": "Paris"}'
        yield '{"response": " is"}'
        yield '{"response": " the capital of France."}'
    
    # Mock the response
    mock_response = httpx.Response(200, text="")
    mock_response.aiter_lines = mock_aiter_lines
    
    # Mock system metrics
    with patch('src.llm.get_system_metrics') as mock_metrics:
        mock_metrics.side_effect = [mock_start_metrics, mock_end_metrics]
        
        # Mock the cache to always miss
        with patch('src.cache.ResponseCache.get', return_value=None):
            # Patch the post method
            with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
                response = await client.generate("What is the capital of France?")
                
                assert isinstance(response, LLMResponse)
                assert response.text == "Paris is the capital of France."
                assert response.error is None
                
                # Verify metrics
                assert response.metrics is not None
                assert response.metrics["start_metrics"] == mock_start_metrics
                assert response.metrics["end_metrics"] == mock_end_metrics
                assert response.metrics["memory_increase_mb"] == 10.0
                assert response.metrics["prompt_length"] == len("What is the capital of France?")
                assert response.metrics["response_length"] == len("Paris is the capital of France.")
                assert response.metrics["model"] == client.model

@pytest.mark.asyncio
async def test_llm_generate_metrics_on_error(test_llm_config, mock_benchmark):
    """Test metrics collection when LLM generation fails."""
    client = LLMClient(test_llm_config)
    
    # Mock system metrics
    mock_metrics = {
        "cpu_percent": 10.0,
        "memory_percent": 50.0,
        "memory_mb": 1000.0,
        "num_threads": 4
    }
    
    # Mock error response
    mock_response = httpx.Response(500, text="Internal Server Error")
    
    # Mock system metrics
    with patch('src.llm.get_system_metrics', return_value=mock_metrics):
        # Mock the cache to always miss
        with patch('src.cache.ResponseCache.get', return_value=None):
            with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
                response = await client.generate("Test prompt")
                
                assert isinstance(response, LLMResponse)
                assert response.error is not None
                assert "HTTP error 500" in response.error
                assert response.metrics["start_metrics"] == mock_metrics

@pytest.mark.asyncio
async def test_llm_response_caching(test_llm_config, mock_benchmark):
    """Test LLM response caching."""
    client = LLMClient(test_llm_config)
    
    # Mock response with streaming data
    async def mock_aiter_lines():
        yield '{"response": "Paris"}'
        yield '{"response": " is"}'
        yield '{"response": " the capital of France."}'
    
    # Mock the response
    mock_response = httpx.Response(200, text="")
    mock_response.aiter_lines = mock_aiter_lines
    
    # First request should hit the API
    with patch('src.cache.ResponseCache.get', return_value=None):
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response) as mock_post:
            response1 = await client.generate("What is the capital of France?")
            assert mock_post.called
            assert response1.text == "Paris is the capital of France."
            assert not response1.cached
    
    # Second request with same parameters should hit cache
    with patch('src.cache.ResponseCache.get', return_value="Paris is the capital of France."):
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response) as mock_post:
            response2 = await client.generate("What is the capital of France?")
            assert not mock_post.called  # API should not be called
            assert response2.text == "Paris is the capital of France."
            assert response2.cached
    
    # Different prompt should miss cache
    with patch('src.cache.ResponseCache.get', return_value=None):
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response) as mock_post:
            response3 = await client.generate("What is the capital of Spain?")
            assert mock_post.called
            assert not response3.cached

@pytest.mark.asyncio
async def test_llm_cache_with_different_params(test_llm_config, mock_benchmark):
    """Test cache behavior with different parameters."""
    client = LLMClient(test_llm_config)
    
    # Mock response
    async def mock_aiter_lines():
        yield '{"response": "Test response"}'
    
    mock_response = httpx.Response(200, text="")
    mock_response.aiter_lines = mock_aiter_lines
    
    # First request
    with patch('src.cache.ResponseCache.get', return_value=None):
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
            response1 = await client.generate("Test prompt")
            assert not response1.cached
    
    # Same request, different temperature
    client.config.temperature = 0.8
    with patch('src.cache.ResponseCache.get', return_value=None):
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
            response2 = await client.generate("Test prompt")
            assert not response2.cached  # Should miss cache due to different temperature
    
    # Same request, different model
    client.set_model("different-model")
    with patch('src.cache.ResponseCache.get', return_value=None):
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
            response3 = await client.generate("Test prompt")
            assert not response3.cached  # Should miss cache due to different model

@pytest.mark.asyncio
async def test_llm_cache_error_handling(test_llm_config, mock_benchmark):
    """Test cache behavior with API errors."""
    client = LLMClient(test_llm_config)
    
    # Mock error response
    mock_error_response = httpx.Response(500, text="Internal Server Error")
    
    # Mock system metrics
    mock_metrics = {
        "cpu_percent": 10.0,
        "memory_percent": 50.0,
        "memory_mb": 1000.0,
        "num_threads": 4
    }
    
    # Error responses should not be cached
    with patch('src.llm.get_system_metrics', return_value=mock_metrics):
        with patch('src.cache.ResponseCache.get', return_value=None):
            with patch.object(httpx.AsyncClient, 'post', return_value=mock_error_response):
                response1 = await client.generate("Test prompt")
                assert response1.error is not None
                assert "HTTP error 500" in response1.error
                assert not response1.cached
                
                # Second request should still try API
                response2 = await client.generate("Test prompt")
                assert response2.error is not None
                assert "HTTP error 500" in response2.error
                assert not response2.cached

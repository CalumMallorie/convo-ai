import pytest
import asyncio
from src.llm import LLMClient

@pytest.mark.asyncio
async def test_llm_generation(test_llm_config):
    """Test that the LLM client can generate text with a simple prompt."""
    client = LLMClient(test_llm_config)
    
    prompt = "What is Python?"
    response = await client.generate(prompt)
    
    assert response is not None
    assert response.text is not None
    assert len(response.text) > 0
    assert response.error is None or response.error == ""

@pytest.mark.asyncio
async def test_llm_model_switching(test_llm_config):
    """Test that the LLM client can switch models."""
    client = LLMClient(test_llm_config)
    
    # Store original model
    original_model = client.model
    
    # Set a different model
    new_model = "mistral" if original_model != "mistral" else "phi"
    client.set_model(new_model)
    
    assert client.model == new_model
    
    # Test generation with new model
    response = await client.generate("Test prompt")
    assert response is not None 
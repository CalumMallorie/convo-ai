import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch
from moderation import ContentModerator, ModerationResult

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client for testing."""
    with patch('moderation.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.moderations.create = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_client

@pytest.fixture
def moderator(mock_openai_client):
    """Create a ContentModerator instance with mocked client."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        return ContentModerator()

async def test_safe_content(moderator, mock_openai_client):
    """Test moderation of safe content."""
    mock_response = Mock()
    mock_response.results = [Mock(
        flagged=False,
        category_scores=Mock(model_dump=lambda: {"hate": 0.1, "violence": 0.05})
    )]
    mock_openai_client.return_value.moderations.create.return_value = mock_response
    
    result = await moderator.moderate("Hello! How are you today?")
    assert result.is_safe
    assert not result.error
    assert result.flagged_categories["hate"] == 0.1

async def test_unsafe_content(moderator, mock_openai_client):
    """Test moderation of unsafe content."""
    mock_response = Mock()
    mock_response.results = [Mock(
        flagged=True,
        category_scores=Mock(model_dump=lambda: {"hate": 0.9, "violence": 0.8})
    )]
    mock_openai_client.return_value.moderations.create.return_value = mock_response
    
    result = await moderator.moderate("I hate everything!")
    assert not result.is_safe
    assert not result.error
    assert result.flagged_categories["hate"] == 0.9

async def test_api_error_handling(moderator, mock_openai_client):
    """Test error handling when API call fails."""
    mock_openai_client.return_value.moderations.create.side_effect = Exception("API Error")
    
    result = await moderator.moderate("Test content")
    assert not result.is_safe
    assert result.error == "API Error"
    assert result.flagged_categories == {}

def test_missing_api_key():
    """Test initialization with missing API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
            ContentModerator()

async def test_rate_limiting(moderator, mock_openai_client):
    """Test handling of rate limiting."""
    mock_openai_client.return_value.moderations.create.side_effect = Exception("Rate limit exceeded")
    
    result = await moderator.moderate("Test content")
    assert not result.is_safe
    assert "Rate limit" in result.error
    assert result.flagged_categories == {}

async def test_category_validation(moderator, mock_openai_client):
    """Test validation of category scores."""
    mock_response = Mock()
    mock_response.results = [Mock(
        flagged=False,
        category_scores=Mock(model_dump=lambda: {
            "hate": 0.1,
            "violence": 0.05,
            "harassment": 0.02,
            "self-harm": 0.01
        })
    )]
    mock_openai_client.return_value.moderations.create.return_value = mock_response
    
    result = await moderator.moderate("Test content")
    assert result.is_safe
    assert all(0 <= score <= 1 for score in result.flagged_categories.values())

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
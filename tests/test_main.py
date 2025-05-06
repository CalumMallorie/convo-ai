import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app, Message, ChatResponse
from src.llm import LLMResponse
from src.moderation import ModerationResult
from src.tts import TTSResponse

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_services():
    """Mock all service instances."""
    with patch("src.main.moderator") as mock_moderator, \
         patch("src.main.llm_client") as mock_llm, \
         patch("src.main.tts_client") as mock_tts:
        
        # Setup mock responses
        mock_moderator.moderate = AsyncMock(return_value=ModerationResult(
            is_safe=True,
            flagged_categories={
                "hate": 0.0,
                "hate/threatening": 0.0,
                "self-harm": 0.0,
                "sexual": 0.0,
                "sexual/minors": 0.0,
                "violence": 0.0,
                "violence/graphic": 0.0
            }
        ))
        
        mock_llm.generate = AsyncMock(return_value=LLMResponse(text="Test response"))
        
        mock_tts.generate_speech = AsyncMock(return_value=TTSResponse(audio_url="/audio/test.wav"))
        
        yield {
            "moderator": mock_moderator,
            "llm": mock_llm,
            "tts": mock_tts
        }

def test_root_endpoint(test_client):
    """Test the root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "message": "Convo AI is running"}

def test_chat_endpoint_success(test_client, mock_services):
    """Test successful chat interaction."""
    message = {"content": "Hello", "role": "user"}
    response = test_client.post("/chat", json=message)
    
    assert response.status_code == 200
    assert response.json() == {
        "text": "Test response",
        "audio_url": "/audio/test.wav",
        "error": None
    }
    
    # Verify service calls
    mock_services["moderator"].moderate.assert_called_once_with("Hello")
    mock_services["llm"].generate.assert_called_once_with("Hello")
    mock_services["tts"].generate_speech.assert_called_once_with("Test response")

def test_chat_endpoint_moderation_failure(test_client, mock_services):
    """Test chat interaction with failed moderation."""
    # Setup mock response
    mock_services["moderator"].moderate.return_value = ModerationResult(
        is_safe=False,
        flagged_categories={
            "hate": 0.0,
            "hate/threatening": 0.0,
            "self-harm": 0.0,
            "sexual": 0.0,
            "sexual/minors": 0.0,
            "violence": 0.0,
            "violence/graphic": 0.0
        }
    )
    
    message = {"content": "Bad content", "role": "user"}
    response = test_client.post("/chat", json=message)
    
    assert response.status_code == 200
    assert response.json() == {
        "text": "I apologize, but I cannot process that content.",
        "audio_url": None,
        "error": "Content moderation failed"
    }
    
    # Verify service calls
    mock_services["moderator"].moderate.assert_called_once_with("Bad content")
    mock_services["llm"].generate.assert_not_called()
    mock_services["tts"].generate_speech.assert_not_called()

def test_chat_endpoint_llm_failure(test_client, mock_services):
    """Test chat interaction with LLM failure."""
    # Setup mock response
    mock_services["llm"].generate.return_value = LLMResponse(error="LLM error")
    
    message = {"content": "Hello", "role": "user"}
    response = test_client.post("/chat", json=message)
    
    assert response.status_code == 200
    assert response.json() == {
        "text": "I apologize, but I encountered an error.",
        "audio_url": None,
        "error": "LLM error"
    }
    
    # Verify service calls
    mock_services["moderator"].moderate.assert_called_once_with("Hello")
    mock_services["llm"].generate.assert_called_once_with("Hello")
    mock_services["tts"].generate_speech.assert_not_called()

def test_chat_endpoint_tts_failure(test_client, mock_services):
    """Test chat interaction with TTS failure."""
    # Setup mock response
    mock_services["tts"].generate_speech.return_value = TTSResponse(error="TTS error")
    
    message = {"content": "Hello", "role": "user"}
    response = test_client.post("/chat", json=message)
    
    assert response.status_code == 200
    assert response.json() == {
        "text": "Test response",
        "audio_url": None,
        "error": "TTS error"
    }
    
    # Verify service calls
    mock_services["moderator"].moderate.assert_called_once_with("Hello")
    mock_services["llm"].generate.assert_called_once_with("Hello")
    mock_services["tts"].generate_speech.assert_called_once_with("Test response")

def test_chat_endpoint_invalid_input(test_client):
    """Test chat interaction with invalid input."""
    # Missing required field
    response = test_client.post("/chat", json={"role": "user"})
    assert response.status_code == 422
    
    # Invalid role
    response = test_client.post("/chat", json={"content": "Hello", "role": "invalid"})
    assert response.status_code == 200  # Role has a default value

def test_chat_endpoint_server_error(test_client, mock_services):
    """Test chat interaction with server error."""
    # Setup mock to raise an exception
    mock_services["moderator"].moderate.side_effect = Exception("Test error")
    
    message = {"content": "Hello", "role": "user"}
    response = test_client.post("/chat", json=message)
    
    assert response.status_code == 500
    assert response.json() == {"detail": "Test error"} 
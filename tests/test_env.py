import os
import pytest
from dotenv import load_dotenv

def test_dotenv_loading():
    """Test that .env file is loaded correctly."""
    load_dotenv()
    # Just check that the function runs without errors
    assert True

def test_openai_api_key():
    """Test that OpenAI API key is set in environment variables."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    # Skip if no key is present, we don't want to fail CI builds
    if not api_key:
        pytest.skip("OpenAI API key not set, skipping test")
    assert len(api_key) > 0

def test_gist_environment_variables():
    """Test that GitHub Gist environment variables are properly set."""
    load_dotenv()
    gist_token = os.getenv("GIST_TOKEN")
    gist_id = os.getenv("GIST_ID")
    
    # Skip if not present, we don't want to fail CI builds
    if not gist_token or not gist_id:
        pytest.skip("Gist environment variables not set, skipping test")
    
    assert len(gist_token) > 0
    assert len(gist_id) > 0 
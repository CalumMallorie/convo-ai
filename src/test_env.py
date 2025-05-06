import os
from dotenv import load_dotenv

def test_env():
    """Test that environment variables are properly loaded."""
    # Load the environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key is set")
        # Show only the first and last 4 characters for verification
        print(f"Key format: {api_key[:4]}...{api_key[-4:]}")
    else:
        print("❌ OpenAI API key is not set")
        print("Please add OPENAI_API_KEY to your .env file")

if __name__ == "__main__":
    test_env() 
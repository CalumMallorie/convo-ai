import asyncio
import torch
from llm import LLMClient
from tts_native import NativeTTSClient
from config import Config

async def test_mac_optimizations():
    """Test Mac-specific optimizations."""
    config = Config.load()
    
    # Test MPS availability
    print("Testing MPS (Metal Performance Shaders) availability:")
    if torch.backends.mps.is_available():
        print("✅ MPS is available")
        print(f"Device: {torch.device('mps')}")
    else:
        print("❌ MPS is not available")
        return
    
    # Test LLM with GPU optimization
    print("\nTesting LLM with GPU optimization:")
    llm_client = LLMClient(config.llm)
    response = await llm_client.generate("What is the capital of France?")
    print(f"Response: {response.text}")
    if response.error:
        print(f"Error: {response.error}")
    
    # Test TTS with MPS
    print("\nTesting TTS with MPS:")
    try:
        tts_client = NativeTTSClient(config.tts, config.mac)
        print("✅ TTS client initialized with MPS")
        
        # Test TTS generation
        tts_response = await tts_client.generate_speech("Hello, this is a test.")
        if tts_response.audio_path:
            print(f"✅ Audio generated at: {tts_response.audio_path}")
        if tts_response.error:
            print(f"Error: {tts_response.error}")
        
        # Cleanup
        tts_client.cleanup()
    except Exception as e:
        print(f"❌ TTS test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mac_optimizations()) 
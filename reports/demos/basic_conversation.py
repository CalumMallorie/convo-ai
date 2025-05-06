#!/usr/bin/env python3
"""
Basic conversation demo for Convo-AI.
Shows the core functionality of the LLM and TTS integration.
"""

import asyncio
import time
from pathlib import Path
from src.config import Config
from src.llm import LLMClient
from src.tts import TTSClient

async def run_demo():
    """Run a basic conversation demo."""
    print("Initializing Convo-AI...")
    
    # Load configuration
    config = Config.load()
    
    # Initialize clients
    llm_client = LLMClient(config.llm)
    tts_client = TTSClient(config.tts)
    
    # Demo conversation
    prompts = [
        "What is the capital of France?",
        "Tell me a short joke.",
        "What's the weather like today?"
    ]
    
    print("\nStarting conversation demo...")
    print("=" * 50)
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nPrompt {i}: {prompt}")
        
        # Get LLM response
        start_time = time.time()
        response = await llm_client.generate(prompt)
        llm_time = time.time() - start_time
        
        if response.error:
            print(f"Error: {response.error}")
            continue
            
        print(f"Response ({llm_time:.2f}s): {response.text}")
        
        # Generate speech
        start_time = time.time()
        tts_response = await tts_client.generate(
            response.text,
            output_path=f"output/demo/response_{i}.wav"
        )
        tts_time = time.time() - start_time
        
        if tts_response.error:
            print(f"TTS Error: {tts_response.error}")
        else:
            print(f"Audio generated ({tts_time:.2f}s): {tts_response.audio_path}")
    
    print("\nDemo completed!")
    print("=" * 50)

if __name__ == "__main__":
    # Create output directory
    Path("output/demo").mkdir(parents=True, exist_ok=True)
    
    # Run demo
    asyncio.run(run_demo()) 
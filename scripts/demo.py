"""Demo script to showcase Convo-AI functionality."""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json
import matplotlib.pyplot as plt
import pandas as pd
from src.config import Config
from src.llm import LLMClient
from src.benchmarks import PerformanceMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_basic_conversation(client: LLMClient) -> None:
    """Demonstrate basic conversation capabilities.
    
    Args:
        client: The LLM client to use
    """
    logger.info("=== Basic Conversation Demo ===")
    
    prompts = [
        "Hello! How are you today?",
        "Can you explain what quantum computing is in simple terms?",
        "What are some practical applications of quantum computing?",
    ]
    
    for prompt in prompts:
        logger.info(f"\nUser: {prompt}")
        response = await client.generate(prompt)
        
        if response.error:
            logger.error(f"Error: {response.error}")
        else:
            logger.info(f"Assistant: {response.text}")
            if response.cached:
                logger.info("(Response was cached)")

async def demo_streaming_response(client: LLMClient) -> None:
    """Demonstrate streaming response capabilities.
    
    Args:
        client: The LLM client to use
    """
    logger.info("\n=== Streaming Response Demo ===")
    
    prompt = "Write a short story about a robot learning to paint."
    logger.info(f"\nUser: {prompt}")
    logger.info("Assistant: ", end="")
    
    async for chunk in client.generate_stream(prompt):
        if chunk.startswith("Error:"):
            logger.error(chunk)
            break
        print(chunk, end="", flush=True)
    print()  # New line after story

async def demo_model_switching(client: LLMClient) -> None:
    """Demonstrate model switching capabilities.
    
    Args:
        client: The LLM client to use
    """
    logger.info("\n=== Model Switching Demo ===")
    
    prompt = "What is the meaning of life?"
    models = ["mistral", "phi"]
    
    for model in models:
        client.set_model(model)
        logger.info(f"\nUsing model: {model}")
        logger.info(f"User: {prompt}")
        
        response = await client.generate(prompt)
        if response.error:
            logger.error(f"Error: {response.error}")
        else:
            logger.info(f"Assistant: {response.text}")

async def demo_performance_metrics(client: LLMClient) -> None:
    """Demonstrate performance metrics and visualization.
    
    Args:
        client: The LLM client to use
    """
    logger.info("\n=== Performance Metrics Demo ===")
    
    # Test prompts of varying complexity
    prompts = [
        "What is 2+2?",
        "Explain how a car engine works.",
        "Write a detailed analysis of Shakespeare's influence on modern literature.",
        "Explain the theory of relativity, including its mathematical foundations.",
    ]
    
    results = []
    for prompt in prompts:
        logger.info(f"\nProcessing prompt: {prompt[:50]}...")
        response = await client.generate(prompt)
        
        if response.error:
            logger.error(f"Error: {response.error}")
            continue
            
        result = {
            "prompt_length": len(prompt),
            "response_length": len(response.text),
            "memory_increase_mb": response.metrics["memory_increase_mb"],
            "cpu_percent": response.metrics["end_metrics"]["cpu_percent"]
        }
        results.append(result)
    
    # Create visualizations
    df = pd.DataFrame(results)
    output_dir = Path("output/demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Plot 1: Memory usage vs response length
    plt.figure(figsize=(10, 6))
    plt.scatter(df["response_length"], df["memory_increase_mb"])
    plt.xlabel("Response Length (characters)")
    plt.ylabel("Memory Increase (MB)")
    plt.title("Memory Usage vs Response Length")
    plt.savefig(output_dir / "memory_vs_response.png")
    plt.close()
    
    # Plot 2: CPU usage vs response length
    plt.figure(figsize=(10, 6))
    plt.scatter(df["response_length"], df["cpu_percent"])
    plt.xlabel("Response Length (characters)")
    plt.ylabel("CPU Usage (%)")
    plt.title("CPU Usage vs Response Length")
    plt.savefig(output_dir / "cpu_vs_response.png")
    plt.close()
    
    logger.info(f"\nPerformance visualizations saved to {output_dir}")

async def demo_caching(client: LLMClient) -> None:
    """Demonstrate response caching functionality.
    
    Args:
        client: The LLM client to use
    """
    logger.info("\n=== Caching Demo ===")
    
    prompt = "What is the capital of France?"
    
    # First request (should hit API)
    logger.info("\nFirst request (should hit API):")
    logger.info(f"User: {prompt}")
    response1 = await client.generate(prompt)
    
    if response1.error:
        logger.error(f"Error: {response1.error}")
    else:
        logger.info(f"Assistant: {response1.text}")
        logger.info(f"Cached: {response1.cached}")
    
    # Second request (should hit cache)
    logger.info("\nSecond request (should hit cache):")
    logger.info(f"User: {prompt}")
    response2 = await client.generate(prompt)
    
    if response2.error:
        logger.error(f"Error: {response2.error}")
    else:
        logger.info(f"Assistant: {response2.text}")
        logger.info(f"Cached: {response2.cached}")

async def main() -> None:
    """Run the demo script."""
    config = Config()
    client = LLMClient(config.llm)
    
    try:
        # Basic conversation
        await demo_basic_conversation(client)
        
        # Streaming response
        await demo_streaming_response(client)
        
        # Model switching
        await demo_model_switching(client)
        
        # Performance metrics
        await demo_performance_metrics(client)
        
        # Caching
        await demo_caching(client)
        
    except Exception as e:
        logger.error(f"Error running demo: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 
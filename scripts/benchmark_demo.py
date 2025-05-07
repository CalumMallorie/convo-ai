"""Demo script to showcase the benchmarking functionality."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import pandas as pd
from src.config import Config, LLMConfig
from src.llm import LLMClient
from src.benchmarks import PerformanceMetrics

async def run_benchmark_tests(
    client: LLMClient,
    prompts: List[str],
    output_dir: Path
) -> List[Dict[str, Any]]:
    """Run benchmark tests with different prompts.
    
    Args:
        client: The LLM client to use
        prompts: List of prompts to test
        output_dir: Directory to save results
        
    Returns:
        List of benchmark results
    """
    results = []
    
    for prompt in prompts:
        response = await client.generate(prompt)
        
        if response.error:
            print(f"Error with prompt '{prompt[:50]}...': {response.error}")
            continue
            
        result = {
            "prompt": prompt,
            "prompt_length": len(prompt),
            "response_length": len(response.text),
            "memory_increase_mb": response.metrics["memory_increase_mb"],
            "cpu_percent": response.metrics["end_metrics"]["cpu_percent"],
            "model": response.metrics["model"]
        }
        results.append(result)
        
    # Save raw results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"benchmark_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    return results

def plot_results(results: List[Dict[str, Any]], output_dir: Path) -> None:
    """Create visualizations of benchmark results.
    
    Args:
        results: List of benchmark results
        output_dir: Directory to save plots
    """
    df = pd.DataFrame(results)
    
    # Plot 1: Memory usage vs prompt length
    plt.figure(figsize=(10, 6))
    plt.scatter(df['prompt_length'], df['memory_increase_mb'])
    plt.xlabel('Prompt Length (characters)')
    plt.ylabel('Memory Increase (MB)')
    plt.title('Memory Usage vs Prompt Length')
    plt.savefig(output_dir / 'memory_vs_prompt.png')
    plt.close()
    
    # Plot 2: Response time vs prompt length
    plt.figure(figsize=(10, 6))
    plt.scatter(df['prompt_length'], df['cpu_percent'])
    plt.xlabel('Prompt Length (characters)')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage vs Prompt Length')
    plt.savefig(output_dir / 'cpu_vs_prompt.png')
    plt.close()
    
    # Plot 3: Response length vs prompt length
    plt.figure(figsize=(10, 6))
    plt.scatter(df['prompt_length'], df['response_length'])
    plt.xlabel('Prompt Length (characters)')
    plt.ylabel('Response Length (characters)')
    plt.title('Response Length vs Prompt Length')
    plt.savefig(output_dir / 'response_vs_prompt.png')
    plt.close()

async def main() -> None:
    """Run the benchmark demo."""
    # Create output directory
    output_dir = Path("output/benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize client
    config = Config()
    client = LLMClient(config.llm)
    
    # Test prompts of varying lengths and complexity
    prompts = [
        "What is 2+2?",
        "Explain how a car engine works.",
        "Write a short story about a magical forest.",
        "Explain the theory of relativity in detail, including its mathematical foundations and practical applications.",
        "Write a comprehensive analysis of the global economic impact of renewable energy adoption, including statistics and future projections." * 2,
    ]
    
    print("Running benchmark tests...")
    results = await run_benchmark_tests(client, prompts, output_dir)
    
    print("\nGenerating visualization plots...")
    plot_results(results, output_dir)
    
    print(f"\nBenchmark results and plots have been saved to {output_dir}")
    
    # Print summary statistics
    df = pd.DataFrame(results)
    print("\nSummary Statistics:")
    print("-" * 50)
    print(f"Average memory increase: {df['memory_increase_mb'].mean():.2f} MB")
    print(f"Average CPU usage: {df['cpu_percent'].mean():.2f}%")
    print(f"Average response length: {df['response_length'].mean():.2f} characters")
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 
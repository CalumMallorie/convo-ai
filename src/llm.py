from typing import Dict, Any, AsyncGenerator, Optional
import json
import httpx
from pydantic import BaseModel
from src.config import Config, LLMConfig
from src.benchmarks import benchmark, get_system_metrics
from src.cache import ResponseCache

class LLMResponse:
    """Response from LLM service."""
    def __init__(self, text: str = "", error: Optional[str] = None, metrics: Optional[Dict[str, Any]] = None, cached: bool = False):
        self.text = text
        self.error = error
        self.metrics = metrics or {}
        self.cached = cached

class LLMClient:
    """Client for LLM service."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url
        self.model = config.model or "mistral"  # Default to mistral
        self.timeout = 30.0  # Default timeout in seconds
        self.cache = ResponseCache()
    
    def set_model(self, model: str) -> None:
        """Set the model to use."""
        self.model = model
    
    @benchmark("llm_generate")
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate a response from the LLM."""
        if not prompt:
            return LLMResponse(text="", error="Prompt cannot be empty")
        
        # Check cache first
        cache_params = {
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_tokens": self.config.max_tokens
        }
        cached_response = self.cache.get(self.model, prompt, **cache_params)
        if cached_response is not None:
            return LLMResponse(text=cached_response, cached=True)
        
        try:
            start_metrics = get_system_metrics()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": self.config.temperature,
                            "top_p": self.config.top_p,
                            "num_predict": self.config.max_tokens
                        }
                    }
                )
                
                if response.status_code != 200:
                    return LLMResponse(
                        error=f"HTTP error {response.status_code}: {response.text}",
                        metrics={"start_metrics": start_metrics}
                    )
                
                # Process streaming response
                full_text = ""
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        if chunk.get("response"):
                            full_text += chunk["response"]
                    except json.JSONDecodeError:
                        continue
                
                if not full_text:
                    return LLMResponse(
                        error="No response generated",
                        metrics={"start_metrics": start_metrics}
                    )
                
                end_metrics = get_system_metrics()
                metrics = {
                    "start_metrics": start_metrics,
                    "end_metrics": end_metrics,
                    "memory_increase_mb": end_metrics["memory_mb"] - start_metrics["memory_mb"],
                    "prompt_length": len(prompt),
                    "response_length": len(full_text),
                    "model": self.model
                }
                
                # Cache successful response
                response_text = full_text.strip()
                self.cache.set(self.model, prompt, response_text, **cache_params)
                
                return LLMResponse(text=response_text, metrics=metrics)
                
        except httpx.TimeoutException:
            return LLMResponse(
                error="Request timed out: LLM service took too long to respond",
                metrics={"start_metrics": start_metrics}
            )
        except httpx.ConnectError:
            return LLMResponse(
                error="Connection error: Could not connect to LLM service",
                metrics={"start_metrics": start_metrics}
            )
        except Exception as e:
            return LLMResponse(
                error=f"Error generating response: {str(e)}",
                metrics={"start_metrics": start_metrics}
            )
    
    @benchmark("llm_stream")
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM."""
        if not prompt:
            yield "Error: Prompt cannot be empty"
            return
        
        try:
            start_metrics = get_system_metrics()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": self.config.temperature,
                            "top_p": self.config.top_p,
                            "num_predict": self.config.max_tokens
                        }
                    }
                )
                
                if response.status_code != 200:
                    yield f"Error: HTTP {response.status_code}"
                    return
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        if chunk.get("response"):
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        continue
                        
        except httpx.TimeoutException:
            yield "Error: Request timed out"
        except httpx.ConnectError:
            yield "Error: Could not connect to LLM service"
        except Exception as e:
            yield f"Error: {str(e)}" 
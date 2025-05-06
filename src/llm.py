from typing import Dict, Any, AsyncGenerator, Optional
import json
import httpx
from pydantic import BaseModel
from src.config import Config, LLMConfig

class LLMResponse:
    """Response from LLM service."""
    def __init__(self, text: str = "", error: Optional[str] = None):
        self.text = text
        self.error = error

class LLMClient:
    """Client for LLM service."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url
        self.model = config.model or "mistral"  # Default to mistral
        self.timeout = 30.0  # Default timeout in seconds
    
    def set_model(self, model: str) -> None:
        """Set the model to use."""
        self.model = model
    
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate a response from the LLM."""
        if not prompt:
            return LLMResponse(text="", error="Prompt cannot be empty")
        
        try:
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
                        error=f"HTTP error {response.status_code}: {response.text}"
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
                    return LLMResponse(error="No response generated")
                
                return LLMResponse(text=full_text.strip())
                
        except httpx.TimeoutException:
            return LLMResponse(error="Request timed out: LLM service took too long to respond")
        except httpx.ConnectError:
            return LLMResponse(error="Connection error: Could not connect to LLM service")
        except Exception as e:
            return LLMResponse(error=f"Error generating response: {str(e)}")
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM."""
        if not prompt:
            yield "Error: Prompt cannot be empty"
            return
        
        try:
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
from typing import Literal
from pydantic import BaseModel, Field, validator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MacConfig(BaseModel):
    """Configuration for Mac-specific optimizations."""
    device: Literal["mps", "mlx"] = "mps"  # Default to MPS for broader compatibility
    gpu_layers: int = Field(default=32, gt=0)  # Must be positive
    batch_size: int = Field(default=1, gt=0)  # Must be positive
    model_path: str | None = None  # Optional path to local model files

class LLMConfig(BaseModel):
    """Configuration for LLM settings."""
    base_url: str = "http://localhost:11434"
    model: str = "phi"
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048, gt=0)

class TTSConfig(BaseModel):
    """Configuration for TTS settings."""
    base_url: str = "http://localhost:5000"
    voice: str = "alloy"
    model: str = "csm-1b"

class Config(BaseModel):
    """Main configuration class."""
    mac: MacConfig = MacConfig()
    llm: LLMConfig = LLMConfig()
    tts: TTSConfig = TTSConfig()
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            mac=MacConfig(
                device=os.getenv("TTS_DEVICE", "mps"),
                gpu_layers=int(os.getenv("GPU_LAYERS", "32")),
                model_path=os.getenv("TTS_MODEL_PATH")
            ),
            llm=LLMConfig(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("LLM_MODEL", "phi")
            ),
            tts=TTSConfig(
                base_url=os.getenv("TTS_BASE_URL", "http://localhost:5000"),
                voice=os.getenv("TTS_VOICE", "alloy")
            )
        ) 
import pytest
from src.config import Config, LLMConfig, TTSConfig, MacConfig

@pytest.fixture
def test_config() -> Config:
    """Create a test configuration."""
    return Config(
        mac=MacConfig(
            device="mps",
            gpu_layers=32,
            batch_size=1
        ),
        llm=LLMConfig(
            base_url="http://localhost:11434",
            model="phi",
            temperature=0.7,
            top_p=0.9,
            max_tokens=2048
        ),
        tts=TTSConfig(
            base_url="http://localhost:5000",
            voice="alloy",
            model="csm-1b"
        )
    )

@pytest.fixture
def test_llm_config(test_config: Config) -> LLMConfig:
    """Get LLM configuration for testing."""
    return test_config.llm

@pytest.fixture
def test_tts_config(test_config: Config) -> TTSConfig:
    """Get TTS configuration for testing."""
    return test_config.tts

@pytest.fixture
def test_mac_config(test_config: Config) -> MacConfig:
    """Get Mac configuration for testing."""
    return test_config.mac

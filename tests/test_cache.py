"""Tests for the caching module."""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import pytest
from src.cache import ResponseCache

@pytest.fixture
def cache_dir(tmp_path):
    """Create a temporary cache directory."""
    return str(tmp_path / "test_cache")

@pytest.fixture
def cache(cache_dir):
    """Create a test cache instance."""
    return ResponseCache(cache_dir=cache_dir, ttl_hours=24)

def test_cache_initialization(cache_dir):
    """Test cache initialization."""
    cache = ResponseCache(cache_dir=cache_dir)
    assert Path(cache_dir).exists()
    assert Path(cache_dir).is_dir()

def test_cache_key_computation(cache):
    """Test cache key computation."""
    # Same parameters should produce same key
    key1 = cache._compute_key("model1", "test prompt", temp=0.7)
    key2 = cache._compute_key("model1", "test prompt", temp=0.7)
    assert key1 == key2
    
    # Different parameters should produce different keys
    key3 = cache._compute_key("model2", "test prompt", temp=0.7)
    key4 = cache._compute_key("model1", "different prompt", temp=0.7)
    key5 = cache._compute_key("model1", "test prompt", temp=0.8)
    
    assert len({key1, key3, key4, key5}) == 4  # All keys should be different

def test_cache_set_and_get(cache):
    """Test setting and getting cache entries."""
    model = "test-model"
    prompt = "test prompt"
    response = "test response"
    
    # Set cache entry
    cache.set(model, prompt, response, temp=0.7)
    
    # Get cache entry
    cached = cache.get(model, prompt, temp=0.7)
    assert cached == response
    
    # Different parameters should miss
    assert cache.get(model, prompt, temp=0.8) is None
    assert cache.get(model, "different prompt", temp=0.7) is None
    assert cache.get("different-model", prompt, temp=0.7) is None

def test_cache_expiration(cache_dir):
    """Test cache entry expiration."""
    # Create cache with short TTL
    cache = ResponseCache(cache_dir=cache_dir, ttl_hours=1/60)  # 1 minute TTL
    
    model = "test-model"
    prompt = "test prompt"
    response = "test response"
    
    # Set cache entry
    cache.set(model, prompt, response)
    
    # Should hit immediately
    assert cache.get(model, prompt) == response
    
    # Wait for expiration
    time.sleep(61)  # Wait just over a minute
    
    # Should miss after expiration
    assert cache.get(model, prompt) is None

def test_cache_clear(cache):
    """Test clearing the cache."""
    # Add some entries
    cache.set("model1", "prompt1", "response1")
    cache.set("model2", "prompt2", "response2")
    
    # Verify entries exist
    assert cache.get("model1", "prompt1") == "response1"
    assert cache.get("model2", "prompt2") == "response2"
    
    # Clear cache
    cache.clear()
    
    # Verify entries are gone
    assert cache.get("model1", "prompt1") is None
    assert cache.get("model2", "prompt2") is None

def test_cache_invalid_json(cache):
    """Test handling of corrupted cache files."""
    model = "test-model"
    prompt = "test prompt"
    
    # Write invalid JSON to cache file
    key = cache._compute_key(model, prompt)
    cache_file = cache._get_cache_file(key)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cache_file, 'w') as f:
        f.write("invalid json content")
    
    # Should handle gracefully and return None
    assert cache.get(model, prompt) is None
    
    # Cache file should be deleted
    assert not cache_file.exists()

def test_cache_file_structure(cache):
    """Test the structure of cache files."""
    model = "test-model"
    prompt = "test prompt"
    response = "test response"
    params = {"temp": 0.7, "max_tokens": 100}
    
    # Set cache entry
    cache.set(model, prompt, response, **params)
    
    # Get cache file
    key = cache._compute_key(model, prompt, **params)
    cache_file = cache._get_cache_file(key)
    
    # Read and verify structure
    with open(cache_file, 'r') as f:
        data = json.load(f)
        
    assert isinstance(data["timestamp"], str)
    datetime.fromisoformat(data["timestamp"])  # Should not raise
    assert data["model"] == model
    assert data["prompt"] == prompt
    assert data["response"] == response
    assert data["parameters"] == params 
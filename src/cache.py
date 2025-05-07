"""Cache implementation for LLM responses."""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

class ResponseCache:
    """Local file-based cache for LLM responses."""
    
    def __init__(self, cache_dir: str = "output/cache", ttl_hours: int = 24):
        """Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours for cache entries
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.logger = logging.getLogger(__name__)
        
    def _compute_key(self, model: str, prompt: str, **kwargs: Any) -> str:
        """Compute cache key from request parameters.
        
        Args:
            model: The LLM model name
            prompt: The input prompt
            kwargs: Additional parameters that affect the response
            
        Returns:
            Cache key string
        """
        # Create a dictionary of all parameters that affect the response
        params = {
            "model": model,
            "prompt": prompt,
            **kwargs
        }
        
        # Convert to a stable string representation and hash
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.sha256(param_str.encode()).hexdigest()
    
    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{key}.json"
    
    def get(self, model: str, prompt: str, **kwargs: Any) -> Optional[str]:
        """Get a cached response if available and not expired.
        
        Args:
            model: The LLM model name
            prompt: The input prompt
            kwargs: Additional parameters that affect the response
            
        Returns:
            Cached response text if available, None otherwise
        """
        key = self._compute_key(model, prompt, **kwargs)
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                
            # Check if entry has expired
            cached_time = datetime.fromisoformat(cache_data["timestamp"])
            if datetime.now() - cached_time > self.ttl:
                self.logger.info(f"Cache entry expired for key {key}")
                cache_file.unlink()
                return None
                
            self.logger.info(f"Cache hit for key {key}")
            return cache_data["response"]
            
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Error reading cache file {cache_file}: {e}")
            cache_file.unlink()
            return None
    
    def set(self, model: str, prompt: str, response: str, **kwargs: Any) -> None:
        """Store a response in the cache.
        
        Args:
            model: The LLM model name
            prompt: The input prompt
            response: The response to cache
            kwargs: Additional parameters that affect the response
        """
        key = self._compute_key(model, prompt, **kwargs)
        cache_file = self._get_cache_file(key)
        
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt": prompt,
            "response": response,
            "parameters": kwargs
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            self.logger.info(f"Cached response for key {key}")
        except Exception as e:
            self.logger.error(f"Error writing cache file {cache_file}: {e}")
    
    def clear(self) -> None:
        """Clear all cached responses."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                self.logger.error(f"Error deleting cache file {cache_file}: {e}")
        self.logger.info("Cache cleared") 
"""
Caching Module

Provides caching functionality for repeated operations.
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import Any, Optional, Callable, Dict
from functools import wraps
from datetime import datetime, timedelta


class Cache:
    """Simple file-based cache for function results."""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl_seconds: int = 3600):
        """
        Initialize the Cache.
        
        Args:
            cache_dir: Directory for cache files (default: output/cache)
            ttl_seconds: Time-to-live in seconds (default: 1 hour)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path("output/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[Any, datetime]] = {}
    
    def _get_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key from function name and arguments."""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a key."""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, cache_key: str) -> Optional[Any]:
        """
        Get cached value if it exists and is not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
                cached_time = cached_data.get('timestamp')
                value = cached_data.get('value')
                
                # Check if expired
                if cached_time:
                    age = datetime.now() - cached_time
                    if age.total_seconds() > self.ttl_seconds:
                        cache_path.unlink()  # Remove expired cache
                        return None
                
                return value
        except Exception:
            # If cache file is corrupted, remove it
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def set(self, cache_key: str, value: Any) -> None:
        """
        Set cached value.
        
        Args:
            cache_key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cached_data = {
                'value': value,
                'timestamp': datetime.now()
            }
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
        except Exception:
            # Silently fail if caching fails
            pass
    
    def clear(self) -> None:
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        self._cache.clear()


# Global cache instance
_global_cache = Cache()


def cached(cache_instance: Optional[Cache] = None, ttl_seconds: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Args:
        cache_instance: Optional Cache instance (uses global if None)
        ttl_seconds: Optional TTL override
    """
    cache = cache_instance or _global_cache
    if ttl_seconds:
        cache = Cache(cache_dir=cache.cache_dir, ttl_seconds=ttl_seconds)
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cache._get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator



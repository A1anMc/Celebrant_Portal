"""
Redis caching system for performance optimization.
Provides caching decorators and utilities for frequently accessed data.
"""

import json
import hashlib
from typing import Any, Optional, Callable, Union
from functools import wraps
import redis
from datetime import timedelta
import pickle

from .config import settings

# Initialize Redis connection
redis_client = redis.Redis(
    host=settings.redis_host if hasattr(settings, 'redis_host') else 'localhost',
    port=settings.redis_port if hasattr(settings, 'redis_port') else 6379,
    password=settings.redis_password if hasattr(settings, 'redis_password') else None,
    decode_responses=False,  # Keep as bytes for pickle
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)

class CacheManager:
    """Manages Redis caching operations."""
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Generate a unique cache key from function arguments."""
        # Create a string representation of arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        key_string = "|".join(key_parts)
        
        # Generate hash for consistent key length
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @staticmethod
    def set(key: str, value: Any, expire: int = 300) -> bool:
        """
        Set a value in cache with expiration.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds (default: 5 minutes)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize value using pickle for complex objects
            serialized_value = pickle.dumps(value)
            return redis_client.setex(key, expire, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = redis_client.get(key)
            if value is not None:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def delete(key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return bool(redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """
        Delete multiple keys matching a pattern.
        
        Args:
            pattern: Redis pattern (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    @staticmethod
    def exists(key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            return bool(redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    @staticmethod
    def ttl(key: str) -> int:
        """
        Get time to live for a key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            return redis_client.ttl(key)
        except Exception as e:
            print(f"Cache TTL error: {e}")
            return -2

def cache(expire: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        expire: Cache expiration time in seconds
        key_prefix: Prefix for cache key
        
    Example:
        @cache(expire=600, key_prefix="user_stats")
        async def get_user_statistics(user_id: int):
            # Function logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}"
            cache_key = f"{func_key}:{CacheManager.generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = CacheManager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            CacheManager.set(cache_key, result, expire)
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """
    Decorator to invalidate cache after function execution.
    
    Args:
        pattern: Cache key pattern to invalidate
        
    Example:
        @invalidate_cache("user_stats:*")
        async def update_user(user_id: int):
            # Update logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            CacheManager.delete_pattern(pattern)
            
            return result
        
        return wrapper
    return decorator

# Cache key constants
class CacheKeys:
    """Common cache key patterns."""
    USER_STATS = "user_stats"
    COUPLE_STATS = "couple_stats"
    INVOICE_STATS = "invoice_stats"
    CEREMONY_STATS = "ceremony_stats"
    USER_PROFILE = "user_profile"
    COUPLE_DETAILS = "couple_details"
    INVOICE_DETAILS = "invoice_details"
    CEREMONY_DETAILS = "ceremony_details"

# Utility functions for common caching operations
async def cache_user_statistics(user_id: int, data: dict, expire: int = 600):
    """Cache user statistics."""
    key = f"{CacheKeys.USER_STATS}:{user_id}"
    CacheManager.set(key, data, expire)

async def get_cached_user_statistics(user_id: int) -> Optional[dict]:
    """Get cached user statistics."""
    key = f"{CacheKeys.USER_STATS}:{user_id}"
    return CacheManager.get(key)

async def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user."""
    patterns = [
        f"{CacheKeys.USER_STATS}:{user_id}",
        f"{CacheKeys.USER_PROFILE}:{user_id}",
        f"{CacheKeys.COUPLE_STATS}:{user_id}*",
        f"{CacheKeys.INVOICE_STATS}:{user_id}*",
        f"{CacheKeys.CEREMONY_STATS}:{user_id}*"
    ]
    for pattern in patterns:
        CacheManager.delete_pattern(pattern)

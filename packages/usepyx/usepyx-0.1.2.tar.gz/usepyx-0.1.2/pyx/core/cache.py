"""
PyX Caching - Zen Mode
Simple caching for PyX applications.
"""
import time
import json
import hashlib
from typing import Optional, Any, Callable, Dict
from functools import wraps
from datetime import datetime, timedelta


class InMemoryBackend:
    """Simple in-memory cache backend"""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expires_at)
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expires_at = self._cache[key]
            if expires_at is None or time.time() < expires_at:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        expires_at = time.time() + ttl if ttl else None
        self._cache[key] = (value, expires_at)
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self):
        self._cache.clear()
    
    def exists(self, key: str) -> bool:
        return self.get(key) is not None
    
    def keys(self, pattern: str = "*") -> list:
        if pattern == "*":
            return list(self._cache.keys())
        # Simple pattern matching
        import fnmatch
        return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
    
    def ttl(self, key: str) -> Optional[int]:
        if key in self._cache:
            _, expires_at = self._cache[key]
            if expires_at:
                remaining = expires_at - time.time()
                return max(0, int(remaining))
        return None


class RedisBackend:
    """Redis cache backend (optional)"""
    
    def __init__(self, url: str = "redis://localhost:6379"):
        self.url = url
        self._redis = None
    
    def _connect(self):
        if self._redis is None:
            try:
                import redis
                self._redis = redis.from_url(self.url)
            except ImportError:
                raise ImportError("Redis not installed. Run: pip install redis")
        return self._redis
    
    def get(self, key: str) -> Optional[Any]:
        r = self._connect()
        value = r.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value.decode() if isinstance(value, bytes) else value
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        r = self._connect()
        serialized = json.dumps(value) if not isinstance(value, (str, bytes)) else value
        if ttl:
            r.setex(key, ttl, serialized)
        else:
            r.set(key, serialized)
    
    def delete(self, key: str) -> bool:
        r = self._connect()
        return r.delete(key) > 0
    
    def clear(self):
        r = self._connect()
        r.flushdb()
    
    def exists(self, key: str) -> bool:
        r = self._connect()
        return r.exists(key) > 0
    
    def keys(self, pattern: str = "*") -> list:
        r = self._connect()
        return [k.decode() for k in r.keys(pattern)]
    
    def ttl(self, key: str) -> Optional[int]:
        r = self._connect()
        result = r.ttl(key)
        return result if result > 0 else None


class ZenCache:
    """
    Zen Mode Cache - Simple caching API.
    
    Usage:
        from pyx import cache
        
        # Basic operations
        cache.set("key", {"data": "value"}, ttl=3600)
        data = cache.get("key")
        cache.delete("key")
        
        # Decorator
        @cache.memoize(ttl=300)
        def expensive_function(user_id):
            return db.get(User, user_id)
        
        # With prefix
        user_cache = cache.prefix("users")
        user_cache.set("123", user_data)  # Stored as "users:123"
        
        # Redis backend
        cache.use_redis("redis://localhost:6379")
    """
    
    def __init__(self, backend: str = "memory", prefix: str = ""):
        self._prefix = prefix
        if backend == "memory":
            self._backend = InMemoryBackend()
        else:
            self._backend = InMemoryBackend()  # Default to memory
    
    def _make_key(self, key: str) -> str:
        """Create full key with prefix"""
        if self._prefix:
            return f"{self._prefix}:{key}"
        return key
    
    def use_redis(self, url: str = "redis://localhost:6379"):
        """Switch to Redis backend"""
        self._backend = RedisBackend(url)
        return self
    
    def use_memory(self):
        """Switch to in-memory backend"""
        self._backend = InMemoryBackend()
        return self
    
    def prefix(self, prefix: str) -> "ZenCache":
        """Create cache instance with prefix"""
        new_cache = ZenCache.__new__(ZenCache)
        new_cache._backend = self._backend
        new_cache._prefix = f"{self._prefix}:{prefix}" if self._prefix else prefix
        return new_cache
    
    # Core operations
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        result = self._backend.get(self._make_key(key))
        return result if result is not None else default
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        self._backend.set(self._make_key(key), value, ttl)
        return self
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return self._backend.delete(self._make_key(key))
    
    def clear(self):
        """Clear all cache"""
        self._backend.clear()
        return self
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self._backend.exists(self._make_key(key))
    
    def keys(self, pattern: str = "*") -> list:
        """Get keys matching pattern"""
        full_pattern = self._make_key(pattern)
        return self._backend.keys(full_pattern)
    
    def ttl(self, key: str) -> Optional[int]:
        """Get TTL of key in seconds"""
        return self._backend.ttl(self._make_key(key))
    
    # Convenience methods
    
    def get_or_set(self, key: str, factory: Callable, ttl: int = None) -> Any:
        """
        Get from cache or compute and set.
        
        Usage:
            user = cache.get_or_set(
                f"user:{id}",
                lambda: db.get(User, id),
                ttl=3600
            )
        """
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value, ttl)
        return value
    
    def increment(self, key: str, delta: int = 1) -> int:
        """Increment integer value"""
        current = self.get(key, 0)
        new_value = current + delta
        self.set(key, new_value)
        return new_value
    
    def decrement(self, key: str, delta: int = 1) -> int:
        """Decrement integer value"""
        return self.increment(key, -delta)
    
    # Decorators
    
    def memoize(self, ttl: int = 300, key_prefix: str = None):
        """
        Decorator to cache function results.
        
        Usage:
            @cache.memoize(ttl=3600)
            def get_user(user_id):
                return db.get(User, user_id)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Build cache key from function name and arguments
                prefix = key_prefix or func.__name__
                key_parts = [prefix]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached = self.get(cache_key)
                if cached is not None:
                    return cached
                
                # Compute and cache
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            
            # Add cache invalidation method
            wrapper.invalidate = lambda *args, **kwargs: self.delete(
                ":".join([key_prefix or func.__name__] + 
                        [str(a) for a in args] + 
                        [f"{k}={v}" for k, v in sorted(kwargs.items())])
            )
            
            return wrapper
        return decorator
    
    def cached_property(self, ttl: int = 300):
        """
        Decorator for cached class properties.
        
        Usage:
            class User:
                @cache.cached_property(ttl=3600)
                def full_profile(self):
                    return expensive_load()
        """
        def decorator(func):
            @wraps(func)
            def wrapper(instance):
                cache_key = f"{instance.__class__.__name__}:{id(instance)}:{func.__name__}"
                return self.get_or_set(cache_key, lambda: func(instance), ttl)
            return property(wrapper)
        return decorator
    
    # Rate limiting
    
    def rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Simple rate limiting.
        
        Usage:
            if not cache.rate_limit(f"api:{user_id}", 100, 60):
                raise RateLimitExceeded()
        """
        current = self.get(key, 0)
        if current >= max_requests:
            return False
        
        self.increment(key)
        if current == 0:
            # Set TTL on first request
            self.set(key, 1, window_seconds)
        
        return True
    
    # Stats
    
    def stats(self) -> dict:
        """Get cache statistics (memory backend only)"""
        if isinstance(self._backend, InMemoryBackend):
            return {
                "keys": len(self._backend._cache),
                "backend": "memory"
            }
        return {"backend": "redis"}


# Zen Mode instance
cache = ZenCache()


__all__ = ['cache', 'ZenCache', 'InMemoryBackend', 'RedisBackend']

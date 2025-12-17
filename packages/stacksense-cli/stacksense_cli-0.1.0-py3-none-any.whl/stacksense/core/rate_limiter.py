"""
StackSense Rate Limiter
Provides rate limiting for all API calls to prevent abuse and ensure stability.
"""
import time
import threading
from typing import Dict, Optional
from functools import wraps
from dataclasses import dataclass, field


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit."""
    max_requests: int  # Maximum requests allowed
    window_seconds: float  # Time window in seconds
    cooldown_seconds: float = 60.0  # Cooldown when limit hit


@dataclass
class RateLimitState:
    """State for tracking rate limits."""
    request_times: list = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)


class RateLimiter:
    """
    Thread-safe rate limiter for API calls.
    
    Usage:
        limiter = RateLimiter()
        
        @limiter.limit('openrouter', max_requests=60, window_seconds=60)
        def call_openrouter():
            ...
    """
    
    # Default rate limits for different services
    DEFAULT_LIMITS: Dict[str, RateLimitConfig] = {
        'openrouter': RateLimitConfig(max_requests=60, window_seconds=60),
        'openrouter_free': RateLimitConfig(max_requests=20, window_seconds=60),
        'web_search': RateLimitConfig(max_requests=10, window_seconds=60),
        'diagram': RateLimitConfig(max_requests=5, window_seconds=60),
        'file_read': RateLimitConfig(max_requests=100, window_seconds=60),
        'tool_call': RateLimitConfig(max_requests=30, window_seconds=60),
    }
    
    def __init__(self):
        self._states: Dict[str, RateLimitState] = {}
        self._global_lock = threading.Lock()
    
    def _get_state(self, name: str) -> RateLimitState:
        """Get or create rate limit state for a service."""
        if name not in self._states:
            with self._global_lock:
                if name not in self._states:
                    self._states[name] = RateLimitState()
        return self._states[name]
    
    def check_limit(
        self, 
        name: str, 
        max_requests: Optional[int] = None,
        window_seconds: Optional[float] = None,
        wait_if_exceeded: bool = True
    ) -> bool:
        """
        Check if we're within rate limit.
        
        Args:
            name: Name of the rate limit (e.g., 'openrouter')
            max_requests: Override max requests (uses default if None)
            window_seconds: Override window (uses default if None)
            wait_if_exceeded: If True, wait until limit clears
            
        Returns:
            True if within limit, False if exceeded and wait_if_exceeded=False
        """
        # Get config
        config = self.DEFAULT_LIMITS.get(name, RateLimitConfig(60, 60))
        max_req = max_requests or config.max_requests
        window = window_seconds or config.window_seconds
        
        state = self._get_state(name)
        
        with state.lock:
            now = time.time()
            
            # Remove old timestamps outside window
            state.request_times = [t for t in state.request_times if now - t < window]
            
            # Check if at limit
            if len(state.request_times) >= max_req:
                if wait_if_exceeded:
                    # Calculate wait time
                    oldest = state.request_times[0]
                    wait_time = window - (now - oldest)
                    if wait_time > 0:
                        print(f"⏳ Rate limit ({name}): waiting {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        # Clear old timestamps after waiting
                        state.request_times = []
                else:
                    return False
            
            # Record this request
            state.request_times.append(time.time())
            return True
    
    def limit(
        self, 
        name: str, 
        max_requests: Optional[int] = None,
        window_seconds: Optional[float] = None
    ):
        """
        Decorator to apply rate limiting to a function.
        
        Args:
            name: Rate limit category name
            max_requests: Override default max requests
            window_seconds: Override default window
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.check_limit(name, max_requests, window_seconds)
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def async_limit(
        self, 
        name: str, 
        max_requests: Optional[int] = None,
        window_seconds: Optional[float] = None
    ):
        """
        Decorator for async functions.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                self.check_limit(name, max_requests, window_seconds)
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def reset(self, name: Optional[str] = None):
        """Reset rate limit counters."""
        if name:
            if name in self._states:
                with self._states[name].lock:
                    self._states[name].request_times = []
        else:
            with self._global_lock:
                for state in self._states.values():
                    with state.lock:
                        state.request_times = []


# Global rate limiter instance
_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter


def check_rate_limit(name: str, wait: bool = True) -> bool:
    """Convenience function to check rate limit."""
    return get_rate_limiter().check_limit(name, wait_if_exceeded=wait)

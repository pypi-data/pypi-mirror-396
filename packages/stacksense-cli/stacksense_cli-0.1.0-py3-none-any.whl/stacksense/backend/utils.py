"""
Backend Utilities
=================
Shared helpers for hashing, logging, validation.
"""

import os
import hashlib
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Optional

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

def setup_logging(name: str = "stacksense", level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


logger = setup_logging()


# ═══════════════════════════════════════════════════════════
# HASHING
# ═══════════════════════════════════════════════════════════

def hash_sha256(data: str) -> str:
    """Generate SHA256 hash of string data."""
    return hashlib.sha256(data.encode()).hexdigest()


def hash_file(filepath: str) -> str:
    """Generate SHA256 hash of file contents."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_machine_id() -> str:
    """
    Generate unique machine identifier.
    Uses multiple factors for uniqueness.
    """
    import platform
    import uuid
    
    factors = [
        platform.node(),
        platform.machine(),
        str(uuid.getnode()),
        os.getenv("USER", ""),
    ]
    
    combined = ":".join(factors)
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_license_key(key: str) -> bool:
    """Validate license key format."""
    if not key or len(key) < 10:
        return False
    # Lemon Squeezy keys are typically UUID-like or alphanumeric
    allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
    return all(c in allowed for c in key)


def validate_plan(plan: str) -> bool:
    """Validate plan name."""
    valid_plans = {'free', 'starter', 'pro', 'ultra', 'unlimited', 'enterprise'}
    return plan.lower() in valid_plans


def validate_edition(edition: str) -> bool:
    """Validate edition name."""
    valid_editions = {'starter', 'pro', 'ultra', 'unlimited', 'enterprise', 'custom'}
    return edition.lower() in valid_editions


# ═══════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[datetime]] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = datetime.utcnow()
        
        if key not in self._requests:
            self._requests[key] = []
        
        # Clean old requests
        self._requests[key] = [
            t for t in self._requests[key]
            if (now - t).total_seconds() < self.window_seconds
        ]
        
        if len(self._requests[key]) >= self.max_requests:
            return False
        
        self._requests[key].append(now)
        return True


# ═══════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════

def log_execution_time(func):
    """Decorator to log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} executed in {elapsed:.3f}s")
        return result
    return wrapper


def catch_exceptions(default_return: Any = None):
    """Decorator to catch and log exceptions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# ENVIRONMENT
# ═══════════════════════════════════════════════════════════

def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional required check.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: Raise error if not set
        
    Returns:
        Environment variable value
    """
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable {key} not set")
    return value


def is_production() -> bool:
    """Check if running in production."""
    return get_env("ENVIRONMENT", "development").lower() == "production"

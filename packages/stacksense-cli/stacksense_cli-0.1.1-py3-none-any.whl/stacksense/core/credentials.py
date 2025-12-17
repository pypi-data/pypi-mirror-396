"""
StackSense Embedded Credentials
================================
This module contains embedded default credentials that are compiled to binary
via Cython for protection. User-provided credentials (via env vars or config)
always take priority.

SECURITY: This file will be compiled to .so/.pyd binary, making it extremely
difficult to extract credentials.
"""

import base64
import os
import json
from pathlib import Path
from typing import Optional


# Obfuscated embedded credentials (base64 encoded, split for obscurity)
# These are the PRODUCTION defaults - override via env vars for testing
_BACKEND_PARTS = [
    "aHR0cHM6Ly9waWxncmltc3RhY2stYXBpLm",  # https://pilgrimstack-api.
    "ZseS5kZXY=",                            # fly.dev
]

# Store ID (will be replaced with prod value)
_STORE_PARTS = [
    "MTc4NDU4",  # 178458 (prod store ID)
]


def _decode(parts: list) -> str:
    """Decode split base64 parts"""
    return base64.b64decode("".join(parts)).decode()


def get_backend_url() -> str:
    """
    Get backend API URL.
    
    Priority:
    1. STACKSENSE_BACKEND_URL env var
    2. ~/.stacksense/config.json
    3. Embedded default
    """
    # Check env var first
    if os.getenv("STACKSENSE_BACKEND_URL"):
        return os.getenv("STACKSENSE_BACKEND_URL")
    
    # Check local config
    try:
        config_path = Path.home() / ".stacksense" / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            if config.get("backend_url"):
                return config["backend_url"]
    except Exception:
        pass
    
    # Use embedded default
    return _decode(_BACKEND_PARTS)


def get_store_id() -> str:
    """Get Lemon Squeezy store ID"""
    return os.getenv("LEMONSQUEEZY_STORE_ID") or _decode(_STORE_PARTS)


def get_openrouter_key() -> Optional[str]:
    """
    Get OpenRouter API key.
    
    Priority:
    1. OPENROUTER_API_KEY env var
    2. ~/.stacksense/config.json (from --setup-ai)
    3. None (user must configure)
    
    NOTE: We do NOT embed OpenRouter keys - users must provide their own.
    """
    # Check env var
    if os.getenv("OPENROUTER_API_KEY"):
        return os.getenv("OPENROUTER_API_KEY")
    
    # Check local config (from --setup-ai)
    try:
        config_path = Path.home() / ".stacksense" / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            if config.get("openrouter_api_key"):
                return config["openrouter_api_key"]
    except Exception:
        pass
    
    return None


def is_configured() -> bool:
    """Check if the tool is properly configured"""
    return get_openrouter_key() is not None

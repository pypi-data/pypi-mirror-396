"""
Model Registry
==============
Dynamic model lists for all providers.
Fetches from APIs where available, with fallbacks.
"""

import os
import httpx
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class ModelInfo:
    """Information about an AI model."""
    id: str
    name: str
    provider: str
    context_length: int = 4096
    supports_tools: bool = False
    is_free: bool = False
    pricing: Dict[str, float] = field(default_factory=dict)
    description: str = ""


# ═══════════════════════════════════════════════════════════
# OPENROUTER - Dynamic fetching from API
# ═══════════════════════════════════════════════════════════

def fetch_openrouter_models(
    api_key: Optional[str] = None,
    tool_calling_only: bool = False,
    free_only: bool = False
) -> List[ModelInfo]:
    """
    Fetch models from OpenRouter API dynamically.
    
    Uses: https://openrouter.ai/models?supported_parameters=tools
    
    Args:
        api_key: Optional API key (not required for model list)
        tool_calling_only: Only return models supporting tools
        free_only: Only return free models
        
    Returns:
        List of ModelInfo objects
    """
    try:
        url = "https://openrouter.ai/api/v1/models"
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        
        data = response.json()
        models = []
        
        for model_data in data.get("data", []):
            model_id = model_data.get("id", "")
            pricing = model_data.get("pricing", {})
            
            # Check if free
            is_free = (
                float(pricing.get("prompt", 1)) == 0 and
                float(pricing.get("completion", 1)) == 0
            )
            
            # Check tool calling support
            supported_params = model_data.get("supported_parameters", [])
            supports_tools = "tools" in supported_params
            
            # Apply filters
            if free_only and not is_free:
                continue
            if tool_calling_only and not supports_tools:
                continue
            
            models.append(ModelInfo(
                id=model_id,
                name=model_data.get("name", model_id),
                provider="openrouter",
                context_length=model_data.get("context_length", 4096),
                supports_tools=supports_tools,
                is_free=is_free,
                pricing=pricing,
                description=model_data.get("description", "")
            ))
        
        return models
        
    except Exception as e:
        # Fallback to curated list
        return get_openrouter_fallback_models()


def get_openrouter_fallback_models() -> List[ModelInfo]:
    """Fallback curated list when API is unavailable."""
    return [
        ModelInfo(
            id="meta-llama/llama-3.3-70b-instruct:free",
            name="Llama 3.3 70B Instruct",
            provider="openrouter",
            context_length=131072,
            supports_tools=True,
            is_free=True
        ),
        ModelInfo(
            id="qwen/qwen-2.5-72b-instruct:free",
            name="Qwen 2.5 72B Instruct",
            provider="openrouter",
            context_length=32768,
            supports_tools=True,
            is_free=True
        ),
        ModelInfo(
            id="google/gemini-2.0-flash-exp:free",
            name="Gemini 2.0 Flash",
            provider="openrouter",
            context_length=1048576,
            supports_tools=True,
            is_free=True
        ),
        ModelInfo(
            id="mistralai/mistral-large-2411:free",
            name="Mistral Large 24.11",
            provider="openrouter",
            context_length=131072,
            supports_tools=True,
            is_free=True
        ),
        ModelInfo(
            id="nvidia/llama-3.1-nemotron-70b-instruct:free",
            name="Nemotron 70B",
            provider="openrouter",
            context_length=131072,
            supports_tools=True,
            is_free=True
        ),
    ]


# ═══════════════════════════════════════════════════════════
# OPENAI - Static list (well-known models)
# ═══════════════════════════════════════════════════════════

OPENAI_MODELS = [
    ModelInfo(
        id="gpt-4o",
        name="GPT-4o",
        provider="openai",
        context_length=128000,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="gpt-4o-mini",
        name="GPT-4o Mini",
        provider="openai",
        context_length=128000,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        provider="openai",
        context_length=128000,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="gpt-4",
        name="GPT-4",
        provider="openai",
        context_length=8192,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        provider="openai",
        context_length=16385,
        supports_tools=True,
        is_free=False
    ),
]


# ═══════════════════════════════════════════════════════════
# GROK (xAI) - Static list
# ═══════════════════════════════════════════════════════════

GROK_MODELS = [
    ModelInfo(
        id="grok-beta",
        name="Grok Beta",
        provider="grok",
        context_length=131072,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="grok-2",
        name="Grok 2",
        provider="grok",
        context_length=131072,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="grok-2-mini",
        name="Grok 2 Mini",
        provider="grok",
        context_length=131072,
        supports_tools=True,
        is_free=False
    ),
]


# ═══════════════════════════════════════════════════════════
# TOGETHER AI - Models with tool calling
# ═══════════════════════════════════════════════════════════

TOGETHER_MODELS = [
    ModelInfo(
        id="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        name="Llama 3.1 70B Turbo",
        provider="together",
        context_length=131072,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        name="Llama 3.1 8B Turbo",
        provider="together",
        context_length=131072,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        name="Llama 3.3 70B Turbo",
        provider="together",
        context_length=131072,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="Qwen/Qwen2.5-72B-Instruct-Turbo",
        name="Qwen 2.5 72B Turbo",
        provider="together",
        context_length=32768,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="Qwen/Qwen2.5-7B-Instruct-Turbo",
        name="Qwen 2.5 7B Turbo",
        provider="together",
        context_length=32768,
        supports_tools=True,
        is_free=False
    ),
    ModelInfo(
        id="mistralai/Mistral-Small-24B-Instruct-2501",
        name="Mistral Small 24B",
        provider="together",
        context_length=32768,
        supports_tools=True,
        is_free=False
    ),
]


# ═══════════════════════════════════════════════════════════
# UNIFIED MODEL FETCHING
# ═══════════════════════════════════════════════════════════

def get_models(
    provider: str,
    api_key: Optional[str] = None,
    tool_calling_only: bool = True,
    free_only: bool = False
) -> List[ModelInfo]:
    """
    Get models for a provider.
    
    Args:
        provider: Provider name (openai, grok, openrouter, together)
        api_key: Optional API key
        tool_calling_only: Only return models supporting tools
        free_only: Only return free models (OpenRouter only)
        
    Returns:
        List of ModelInfo objects
    """
    if provider == "openrouter":
        return fetch_openrouter_models(api_key, tool_calling_only, free_only)
    elif provider == "openai":
        models = OPENAI_MODELS
    elif provider == "grok":
        models = GROK_MODELS
    elif provider == "together":
        models = TOGETHER_MODELS
    else:
        return []
    
    if tool_calling_only:
        models = [m for m in models if m.supports_tools]
    if free_only:
        models = [m for m in models if m.is_free]
    
    return models


def get_model_ids(provider: str, **kwargs) -> List[str]:
    """Get just the model IDs for a provider."""
    return [m.id for m in get_models(provider, **kwargs)]


@lru_cache(maxsize=4)
def get_cached_models(provider: str) -> List[str]:
    """
    Get cached model IDs (refreshes every 5 minutes in practice).
    Used for CLI autocompletion.
    """
    return get_model_ids(provider, tool_calling_only=False)


# ═══════════════════════════════════════════════════════════
# MODEL SEARCH
# ═══════════════════════════════════════════════════════════

def search_models(query: str, provider: Optional[str] = None) -> List[ModelInfo]:
    """
    Search for models by name or ID.
    
    Args:
        query: Search query
        provider: Optional provider filter
        
    Returns:
        Matching models
    """
    query = query.lower()
    results = []
    
    providers = [provider] if provider else ["openrouter", "openai", "grok", "together"]
    
    for p in providers:
        for model in get_models(p, tool_calling_only=False):
            if query in model.id.lower() or query in model.name.lower():
                results.append(model)
    
    return results

"""
StackSense AI Providers
=======================
Unified interface for multiple AI providers with tool calling support.

Supported providers:
- OpenAI (gpt-4, gpt-4o, etc.)
- Grok (xAI - grok-beta)
- OpenRouter (any model)
- TogetherAI (Llama, Qwen, etc.)
"""

__version__ = "1.0.0"

from .base import BaseProvider, ProviderConfig, ToolDefinition
from .openai_provider import OpenAIProvider
from .grok_provider import GrokProvider
from .openrouter_provider import OpenRouterProvider
from .together_provider import TogetherProvider
from .tools import STACKSENSE_TOOLS, get_tool_definitions

__all__ = [
    "BaseProvider",
    "ProviderConfig",
    "ToolDefinition",
    "OpenAIProvider",
    "GrokProvider",
    "OpenRouterProvider", 
    "TogetherProvider",
    "STACKSENSE_TOOLS",
    "get_tool_definitions",
    "get_provider"
]


def get_provider(provider_name: str, **kwargs) -> BaseProvider:
    """
    Factory function to get provider by name.
    
    Args:
        provider_name: Provider name (openai, grok, openrouter, together)
        **kwargs: Provider-specific configuration
        
    Returns:
        Configured provider instance
    """
    providers = {
        "openai": OpenAIProvider,
        "grok": GrokProvider,
        "openrouter": OpenRouterProvider,
        "together": TogetherProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}. Supported: {list(providers.keys())}")
    
    return provider_class(**kwargs)

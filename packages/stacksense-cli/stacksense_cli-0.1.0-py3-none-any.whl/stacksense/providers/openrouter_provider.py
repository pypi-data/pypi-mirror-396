"""
OpenRouter Provider
===================
OpenRouter API with access to many models and tool calling.
"""

import os
import json
from typing import Optional, List, Dict, Any, Callable, Iterator

from openai import OpenAI

from .base import (
    BaseProvider, ProviderConfig, ToolDefinition,
    ChatMessage, ChatResponse, ToolCall
)


class OpenRouterProvider(BaseProvider):
    """
    OpenRouter API provider.
    
    Supports:
    - 100+ models including free options
    - Native function/tool calling (on supported models)
    - Streaming responses
    
    Free models with tool calling:
    - meta-llama/llama-3.3-70b-instruct:free
    - qwen/qwen-2.5-72b-instruct:free
    - mistralai/mistral-large-2411:free
    """
    
    DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
    BASE_URL = "https://openrouter.ai/api/v1"
    
    # Models known to support tool calling
    TOOL_CALLING_MODELS = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.1-70b-instruct:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "mistralai/mistral-large-2411:free",
        "google/gemini-2.0-flash-exp:free",
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-sonnet",
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        config = ProviderConfig(
            name="openrouter",
            api_key=api_key or os.getenv("OPENROUTER_API_KEY", ""),
            base_url=self.BASE_URL,
            model=model or os.getenv("OPENROUTER_MODEL", self.DEFAULT_MODEL)
        )
        super().__init__(config)
        
        self._client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.BASE_URL,
            default_headers={
                "HTTP-Referer": "https://stacksense.dev",
                "X-Title": "StackSense"
            }
        )
    
    def chat(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> ChatResponse:
        """Standard chat completion."""
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=self._messages_to_dict(messages),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature)
        )
        
        choice = response.choices[0]
        
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens or 0,
                "completion_tokens": response.usage.completion_tokens or 0,
                "total_tokens": response.usage.total_tokens or 0
            }
        
        return ChatResponse(
            content=choice.message.content or "",
            finish_reason=choice.finish_reason or "stop",
            model=response.model or self.config.model,
            usage=usage
        )
    
    def chat_stream(
        self,
        messages: List[ChatMessage],
        on_token: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Iterator[str]:
        """Streaming chat completion."""
        stream = self._client.chat.completions.create(
            model=self.config.model,
            messages=self._messages_to_dict(messages),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                if on_token:
                    on_token(token)
                yield token
    
    def chat_with_tools(
        self,
        messages: List[ChatMessage],
        tools: List[ToolDefinition],
        on_token: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> ChatResponse:
        """
        Chat with tool/function calling.
        
        Note: Only certain models support tool calling.
        Check TOOL_CALLING_MODELS for supported options.
        """
        # Check if model supports tools
        model = self.config.model
        supports_tools = any(
            model.startswith(m.split(":")[0]) or model == m
            for m in self.TOOL_CALLING_MODELS
        )
        
        request_params = {
            "model": model,
            "messages": self._messages_to_dict(messages),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature)
        }
        
        if supports_tools and tools:
            request_params["tools"] = self._tools_to_dict(tools)
            request_params["tool_choice"] = "auto"
        
        response = self._client.chat.completions.create(**request_params)
        
        choice = response.choices[0]
        message = choice.message
        
        # Parse tool calls
        tool_calls = []
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {"raw": tc.function.arguments}
                
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=args
                ))
        
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens or 0,
                "completion_tokens": response.usage.completion_tokens or 0,
                "total_tokens": response.usage.total_tokens or 0
            }
        
        return ChatResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            model=response.model or model,
            usage=usage
        )
    
    def list_free_models(self) -> List[str]:
        """Get list of free models available on OpenRouter."""
        # These are known free models as of late 2024
        return [
            "meta-llama/llama-3.3-70b-instruct:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "nvidia/nemotron-4-340b-instruct:free",
        ]
    
    def supports_tools(self, model: str) -> bool:
        """Check if a model supports tool calling."""
        return any(
            model.startswith(m.split(":")[0]) or model == m
            for m in self.TOOL_CALLING_MODELS
        )

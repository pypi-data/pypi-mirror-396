"""
TogetherAI Provider
===================
Together AI API with tool calling support.
"""

import os
import json
from typing import Optional, List, Dict, Any, Callable, Iterator

from openai import OpenAI

from .base import (
    BaseProvider, ProviderConfig, ToolDefinition,
    ChatMessage, ChatResponse, ToolCall
)


class TogetherProvider(BaseProvider):
    """
    Together AI API provider.
    
    Supports:
    - Llama, Qwen, Mistral models
    - Native function/tool calling
    - Streaming responses
    
    Popular models with tool calling:
    - meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
    - Qwen/Qwen2.5-72B-Instruct-Turbo
    - mistralai/Mistral-7B-Instruct-v0.3
    """
    
    DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    BASE_URL = "https://api.together.xyz/v1"
    
    # Models known to support tool calling
    TOOL_CALLING_MODELS = [
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "Qwen/Qwen2.5-7B-Instruct-Turbo",
        "Qwen/Qwen2.5-72B-Instruct-Turbo",
        "mistralai/Mistral-Small-24B-Instruct-2501",
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        config = ProviderConfig(
            name="together",
            api_key=api_key or os.getenv("TOGETHER_API_KEY", ""),
            base_url=self.BASE_URL,
            model=model or os.getenv("TOGETHER_MODEL", self.DEFAULT_MODEL)
        )
        super().__init__(config)
        
        self._client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.BASE_URL
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
        
        TogetherAI uses OpenAI-compatible format for tool calling.
        See: https://docs.together.ai/docs/function-calling
        """
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=self._messages_to_dict(messages),
            tools=self._tools_to_dict(tools),
            tool_choice="auto",
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature)
        )
        
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
            model=response.model or self.config.model,
            usage=usage
        )
    
    def list_models(self, tool_calling_only: bool = True) -> List[str]:
        """
        Get list of available models.
        
        Args:
            tool_calling_only: Only return models that support tool calling
            
        Returns:
            List of model names
        """
        if tool_calling_only:
            return self.TOOL_CALLING_MODELS
        
        # Would need to call Together API for full list
        return self.TOOL_CALLING_MODELS
    
    def supports_tools(self, model: str) -> bool:
        """Check if a model supports tool calling."""
        return model in self.TOOL_CALLING_MODELS

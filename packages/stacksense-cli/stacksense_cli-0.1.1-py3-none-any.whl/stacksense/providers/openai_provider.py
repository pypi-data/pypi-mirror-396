"""
OpenAI Provider
===============
Native OpenAI API with tool calling support.
"""

import os
import json
from typing import Optional, List, Dict, Any, Callable, Iterator

from openai import OpenAI

from .base import (
    BaseProvider, ProviderConfig, ToolDefinition,
    ChatMessage, ChatResponse, ToolCall
)


class OpenAIProvider(BaseProvider):
    """
    OpenAI API provider.
    
    Supports:
    - GPT-4, GPT-4o, GPT-4o-mini
    - Native function/tool calling
    - Streaming responses
    """
    
    DEFAULT_MODEL = "gpt-4o-mini"
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        config = ProviderConfig(
            name="openai",
            api_key=api_key or os.getenv("OPENAI_API_KEY", ""),
            base_url=self.BASE_URL,
            model=model or os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)
        )
        super().__init__(config)
        
        self._client = OpenAI(api_key=self.config.api_key)
    
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
        
        return ChatResponse(
            content=choice.message.content or "",
            finish_reason=choice.finish_reason,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
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
        """Chat with tool/function calling."""
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
        if message.tool_calls:
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
        
        return ChatResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )

"""
Base Provider - Abstract Interface
===================================
Defines the interface all AI providers must implement.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, Iterator


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    name: str
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    supports_tools: bool = True
    supports_streaming: bool = True


@dataclass
class ToolDefinition:
    """Definition of a tool/function for AI to call."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = field(default_factory=list)
    
    def to_openai_format(self) -> Dict:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required
                }
            }
        }


@dataclass
class ToolCall:
    """A tool call from the AI."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ChatMessage:
    """A chat message."""
    role: str  # system, user, assistant, tool
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None  # For tool responses


@dataclass
class ChatResponse:
    """Response from chat completion."""
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    model: str = ""
    usage: Dict[str, int] = field(default_factory=dict)


class BaseProvider(ABC):
    """
    Base class for all AI providers.
    
    All providers must implement:
    - chat(): Standard chat completion
    - chat_stream(): Streaming chat completion
    - chat_with_tools(): Chat with tool calling
    """
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._client = None
    
    @abstractmethod
    def chat(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> ChatResponse:
        """
        Standard chat completion.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional provider-specific options
            
        Returns:
            ChatResponse with content
        """
        pass
    
    @abstractmethod
    def chat_stream(
        self,
        messages: List[ChatMessage],
        on_token: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Streaming chat completion.
        
        Args:
            messages: List of chat messages
            on_token: Callback for each token
            **kwargs: Additional options
            
        Yields:
            Response tokens
        """
        pass
    
    @abstractmethod
    def chat_with_tools(
        self,
        messages: List[ChatMessage],
        tools: List[ToolDefinition],
        on_token: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> ChatResponse:
        """
        Chat with tool/function calling.
        
        Args:
            messages: List of chat messages
            tools: Available tools
            on_token: Optional streaming callback
            **kwargs: Additional options
            
        Returns:
            ChatResponse with potential tool_calls
        """
        pass
    
    def _messages_to_dict(self, messages: List[ChatMessage]) -> List[Dict]:
        """Convert ChatMessage list to dict format for API."""
        result = []
        for msg in messages:
            d = {"role": msg.role, "content": msg.content}
            
            if msg.tool_calls:
                d["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": str(tc.arguments) if isinstance(tc.arguments, dict) else tc.arguments
                        }
                    }
                    for tc in msg.tool_calls
                ]
            
            if msg.tool_call_id:
                d["tool_call_id"] = msg.tool_call_id
            
            if msg.name:
                d["name"] = msg.name
            
            result.append(d)
        
        return result
    
    def _tools_to_dict(self, tools: List[ToolDefinition]) -> List[Dict]:
        """Convert ToolDefinition list to dict format for API."""
        return [tool.to_openai_format() for tool in tools]
    
    @classmethod
    def from_env(cls, prefix: str = "AI") -> "BaseProvider":
        """
        Create provider from environment variables.
        
        Expected env vars:
        - {PREFIX}_PROVIDER: Provider name
        - {PREFIX}_API_KEY: API key
        - {PREFIX}_MODEL: Model name
        - {PREFIX}_BASE_URL: Optional base URL override
        """
        provider = os.getenv(f"{prefix}_PROVIDER", "openrouter")
        api_key = os.getenv(f"{prefix}_API_KEY", "")
        model = os.getenv(f"{prefix}_MODEL", "")
        base_url = os.getenv(f"{prefix}_BASE_URL", "")
        
        if not api_key:
            raise ValueError(f"{prefix}_API_KEY environment variable not set")
        
        config = ProviderConfig(
            name=provider,
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        
        return cls(config)

"""
Together Agent
==============
Agent using TogetherAI API with tool calling support.
Inherits shared tools from BaseAgent.
"""

import json
import time
from typing import Optional, Callable, Dict, Any, List

from openai import OpenAI

from .base_agent import BaseAgent, ToolResult, AgentStats


class TogetherAgent(BaseAgent):
    """
    StackSense Agent using TogetherAI API.
    
    Supports:
    - Llama, Qwen, Mistral, DeepSeek models
    - Native function/tool calling
    - Streaming responses
    
    Popular models with tool calling:
    - meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
    - meta-llama/Llama-3.3-70B-Instruct-Turbo
    - Qwen/Qwen2.5-72B-Instruct-Turbo
    - deepseek-ai/DeepSeek-V3
    """
    
    DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    BASE_URL = "https://api.together.xyz/v1"
    
    # Models known to support tool calling well
    TOOL_CALLING_MODELS = [
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        "Qwen/Qwen2.5-7B-Instruct-Turbo",
        "Qwen/Qwen2.5-72B-Instruct-Turbo",
        "deepseek-ai/DeepSeek-R1",
        "deepseek-ai/DeepSeek-V3",
        "mistralai/Mistral-Small-24B-Instruct-2501",
    ]
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        model_name: str = None,
        api_key: str = None,
        debug: bool = False
    ):
        super().__init__(workspace_path, model_name, debug)
        
        import os
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY", "")
        
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY environment variable not set")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.BASE_URL
        )
        
        if self.debug:
            print(f"[TogetherAgent] Using model: {self.model_name}")
    
    def get_default_model(self) -> str:
        return self.DEFAULT_MODEL
    
    def supports_tools(self, model: str = None) -> bool:
        """Check if model supports tool calling."""
        model = model or self.model_name
        return model in self.TOOL_CALLING_MODELS
    
    async def chat(
        self,
        user_query: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str], None]] = None,
        on_tool_complete: Optional[Callable[[str, str], None]] = None
    ) -> str:
        """
        Process query using TogetherAI with tool calling.
        
        TogetherAI uses OpenAI-compatible format for function calling.
        See: https://docs.together.ai/docs/function-calling
        """
        self.stats = AgentStats()
        start_time = time.time()
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        final_response = ""
        
        # Only use tools if model supports them
        use_tools = self.workspace_path and self.supports_tools()
        
        while self.stats.tools_used < self.max_tools:
            try:
                kwargs = {
                    "model": self.model_name,
                    "messages": messages,
                }
                
                if use_tools:
                    kwargs["tools"] = self.TOOLS
                    kwargs["tool_choice"] = "auto"
                
                response = self.client.chat.completions.create(**kwargs)
                
                choice = response.choices[0]
                message = choice.message
                
                # Check for tool calls
                tool_calls = getattr(message, 'tool_calls', None)
                
                if not tool_calls:
                    final_response = message.content or ""
                    break
                
                # Execute tool calls
                for tc in tool_calls:
                    tool_name = tc.function.name
                    try:
                        tool_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}
                    
                    if on_tool_start:
                        on_tool_start(f"{tool_name}({tool_args})")
                    
                    tool_result = self._execute_tool(tool_name, tool_args)
                    
                    if on_tool_complete:
                        status = "✓" if tool_result.success else "✗"
                        on_tool_complete(tool_name, f"{status} {tool_result.elapsed:.1f}s")
                    
                    messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [{
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args)
                            }
                        }]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_result.result if tool_result.success else f"Error: {tool_result.error}"
                    })
                
            except Exception as e:
                if self.debug:
                    print(f"[TogetherAgent] Error: {e}")
                final_response = f"Error: {e}"
                break
        
        self.stats.total_time = time.time() - start_time
        return final_response

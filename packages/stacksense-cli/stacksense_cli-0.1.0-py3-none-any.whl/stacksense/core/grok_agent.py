"""
Grok Agent (xAI)
================
Agent using xAI's Grok API with tool calling support.
Inherits shared tools from BaseAgent.
"""

import json
import time
from typing import Optional, Callable, Dict, Any

from openai import OpenAI

from .base_agent import BaseAgent, ToolResult, AgentStats


class GrokAgent(BaseAgent):
    """
    StackSense Agent using xAI Grok API.
    
    Supports:
    - grok-beta, grok-2, grok-4
    - Native function/tool calling (including agentic server-side tools)
    - Streaming responses
    
    Uses OpenAI-compatible API format.
    """
    
    DEFAULT_MODEL = "grok-beta"
    BASE_URL = "https://api.x.ai/v1"
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        model_name: str = None,
        api_key: str = None,
        debug: bool = False
    ):
        super().__init__(workspace_path, model_name, debug)
        
        import os
        self.api_key = api_key or os.getenv("GROK_API_KEY", os.getenv("XAI_API_KEY", ""))
        
        if not self.api_key:
            raise ValueError("GROK_API_KEY or XAI_API_KEY environment variable not set")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.BASE_URL
        )
        
        if self.debug:
            print(f"[GrokAgent] Using model: {self.model_name}")
    
    def get_default_model(self) -> str:
        return self.DEFAULT_MODEL
    
    async def chat(
        self,
        user_query: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str], None]] = None,
        on_tool_complete: Optional[Callable[[str, str], None]] = None
    ) -> str:
        """
        Process query using Grok with tool calling.
        
        Grok uses OpenAI-compatible format for function calling.
        """
        self.stats = AgentStats()
        start_time = time.time()
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        final_response = ""
        
        while self.stats.tools_used < self.max_tools:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=self.TOOLS if self.workspace_path else [],
                    tool_choice="auto" if self.workspace_path else "none"
                )
                
                choice = response.choices[0]
                message = choice.message
                
                if not message.tool_calls:
                    final_response = message.content or ""
                    break
                
                # Execute tool calls
                for tc in message.tool_calls:
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
                    print(f"[GrokAgent] Error: {e}")
                final_response = f"Error: {e}"
                break
        
        self.stats.total_time = time.time() - start_time
        return final_response

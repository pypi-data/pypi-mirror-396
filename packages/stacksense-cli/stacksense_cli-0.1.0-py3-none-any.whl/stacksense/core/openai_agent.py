"""
OpenAI Agent
============
Agent using OpenAI API with tool calling support.
Inherits shared tools from BaseAgent.
"""

import json
import time
from typing import Optional, Callable, Dict, Any

from openai import OpenAI

from .base_agent import BaseAgent, ToolResult, AgentStats


class OpenAIAgent(BaseAgent):
    """
    StackSense Agent using OpenAI API.
    
    Supports:
    - GPT-4, GPT-4o, GPT-4o-mini
    - Native function/tool calling
    - Streaming responses
    """
    
    DEFAULT_MODEL = "gpt-4o-mini"
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        model_name: str = None,
        api_key: str = None,
        debug: bool = False
    ):
        super().__init__(workspace_path, model_name, debug)
        
        import os
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        
        if self.debug:
            print(f"[OpenAIAgent] Using model: {self.model_name}")
    
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
        Process query using OpenAI with tool calling.
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
                    
                    # Add to messages
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
                    print(f"[OpenAIAgent] Error: {e}")
                final_response = f"Error: {e}"
                break
        
        self.stats.total_time = time.time() - start_time
        return final_response

"""
StackSense OpenRouter Agent
===========================
Agent using OpenRouter API with tool calling support.
Inherits shared tools from BaseAgent.
"""

import json
import time
from typing import Optional, Dict, List, Callable, Any

from .base_agent import BaseAgent, ToolResult, AgentStats
from .openrouter_client import get_client


class OpenRouterAgent(BaseAgent):
    """
    StackSense Agent using OpenRouter API.
    
    Key features:
    - Uses free models from OpenRouter
    - Native tool/function calling
    - Streaming responses
    - Inherits tools from BaseAgent
    """
    
    # Default free model (supports tool calling)
    DEFAULT_MODEL = "nvidia/nemotron-nano-9b-v2:free"
    
    # Fallback list of known tool-capable free models
    TOOL_CAPABLE_MODELS = [
        "nvidia/nemotron-nano-9b-v2:free",
        "mistralai/devstral-2512:free",
        "amazon/nova-2-lite-v1:free",
        "arcee-ai/trinity-mini:free",
        "openai/gpt-4o-mini",  # Paid but reliable
    ]
    
    @classmethod
    def get_tool_capable_model(cls, prefer_free: bool = True) -> str:
        """
        Get a tool-capable model, preferring our curated known-good list.
        Only uses API-discovered models if curated ones are unavailable.
        
        Args:
            prefer_free: If True, prioritize free models
            
        Returns:
            Model ID that supports tool calling
        """
        try:
            import httpx
            
            url = "https://openrouter.ai/api/v1/models"
            response = httpx.get(url, timeout=10.0)
            data = response.json()
            
            # Get set of available model IDs from API
            available_models = set()
            free_tool_models = []
            
            for model in data.get("data", []):
                supported_params = model.get("supported_parameters", [])
                if "tools" in supported_params:
                    model_id = model.get("id", "")
                    available_models.add(model_id)
                    
                    # Track free tool models as backup
                    pricing = model.get("pricing", {})
                    is_free = float(pricing.get("prompt", "1")) == 0
                    if is_free:
                        free_tool_models.append(model_id)
            
            # PRIORITY 1: Use our curated known-good models (in order)
            for curated_model in cls.TOOL_CAPABLE_MODELS:
                if curated_model in available_models:
                    return curated_model
            
            # PRIORITY 2: Any free tool-capable model from API
            if prefer_free and free_tool_models:
                return free_tool_models[0]
            
            # PRIORITY 3: Any tool-capable model from API  
            if available_models:
                return list(available_models)[0]
                
        except Exception:
            pass  # Fall through to fallback
        
        # Fallback to first known good model (no API validation)
        return cls.TOOL_CAPABLE_MODELS[0]
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        model_name: str = None,
        debug: bool = False
    ):
        # Use provided model or auto-select tool-capable model
        if not model_name:
            model_name = self.get_tool_capable_model(prefer_free=True)
        
        # Initialize base class (loads system prompt, gitignore, etc.)
        super().__init__(workspace_path, model_name, debug)
        
        # OpenRouter-specific: API client
        self.client = get_client()
        
        if self.debug:
            print(f"[OpenRouterAgent] Using model: {self.model_name}")
    
    def get_default_model(self) -> str:
        """Return the default model for OpenRouter."""
        return self.DEFAULT_MODEL
    
    def _record_model_stat(self, event_type: str, success: bool, response_time: float = 0):
        """
        Record model reliability statistics (ENH-004).
        
        Tracks:
        - Tool call success/failure
        - Text permission fallbacks
        - Response times
        
        Stored in ~/.stacksense/model_stats.json
        """
        import json
        from pathlib import Path
        
        stats_path = Path.home() / ".stacksense" / "model_stats.json"
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing stats
        stats = {}
        if stats_path.exists():
            try:
                with open(stats_path) as f:
                    stats = json.load(f)
            except:
                pass
        
        # Get or create model entry
        model_stats = stats.get(self.model_name, {
            'tool_success': 0,
            'tool_total': 0,
            'text_permission_fallbacks': 0,
            'avg_response_time': 0,
            'response_count': 0
        })
        
        # Update stats based on event type
        if event_type == 'tool_call':
            model_stats['tool_total'] += 1
            if success:
                model_stats['tool_success'] += 1
        elif event_type == 'text_permission':
            model_stats['text_permission_fallbacks'] += 1
        
        # Update response time average
        if response_time > 0:
            count = model_stats['response_count']
            avg = model_stats['avg_response_time']
            new_avg = (avg * count + response_time) / (count + 1)
            model_stats['avg_response_time'] = round(new_avg, 2)
            model_stats['response_count'] = count + 1
        
        stats[self.model_name] = model_stats
        
        # Save
        try:
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
        except:
            pass  # Silently fail on write errors
    
    # ═══════════════════════════════════════════════════════════
    # MAIN CHAT INTERFACE
    # ═══════════════════════════════════════════════════════════
    
    async def chat(
        self,
        user_query: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str], None]] = None,
        on_tool_complete: Optional[Callable[[str, str], None]] = None
    ) -> str:
        """
        Process query using OpenRouter with tool calling.
        
        Args:
            user_query: User's question
            on_token: Callback for each response token
            on_tool_start: Callback when tool starts
            on_tool_complete: Callback when tool completes
            
        Returns:
            Final response text
        """
        self.stats = AgentStats()
        start_time = time.time()
        
        # Build messages with cached tool context
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Inject cached tool results from previous turns
        # This fixes the "AI forgets what it saw" issue when user says "yes, continue"
        cached_context = self.get_cached_tool_context()
        if cached_context:
            messages.append({
                "role": "system",
                "content": f"Previous tool results from this conversation (for context):\n{cached_context}"
            })
        
        # Add user query
        messages.append({"role": "user", "content": user_query})
        
        final_response = ""
        
        # Conversation loop - AI decides when to use tools
        while self.stats.tools_used < self.max_tools:
            try:
                # Call OpenRouter with tools
                result = self.client.chat_with_tools(
                    model=self.model_name,
                    messages=messages,
                    tools=self.TOOLS if self.workspace_path else [],
                    on_token=on_token
                )
                
                content = result.get('content', '')
                tool_calls = result.get('tool_calls', [])
                
                # If no tool calls, check for natural language permission request (ENH-003)
                if not tool_calls:
                    # Detect if this is a text-based permission request
                    # Must be specific patterns that indicate DESTRUCTIVE ACTIONS ONLY
                    # Not general exploration questions
                    permission_patterns = [
                        'may i create', 'can i create', 'shall i create',
                        'may i run', 'can i run', 'shall i run',
                        'may i modify', 'can i modify', 'shall i modify',
                        'may i write', 'can i write', 'shall i write',
                        'may i delete', 'can i delete', 'shall i delete',
                        'may i execute', 'can i execute', 'shall i execute',
                        'should i proceed with creating', 'should i proceed with running',
                        'should i proceed with modifying', 'should i proceed with writing'
                    ]
                    
                    content_lower = content.lower().strip()
                    
                    # Only trigger fallback if:
                    # 1. Contains a question mark (direct question to user)
                    # 2. Is relatively short (not a long explanation with tool output)
                    # 3. Matches a SPECIFIC permission asking pattern (write/run/modify/create)
                    # 4. NOT just echoing tool results (doesn't contain memory/search output)
                    is_question = '?' in content
                    is_short = len(content) < 400
                    has_no_tool_output = 'previous learnings' not in content_lower and 'saved:' not in content_lower
                    pattern_match = any(p in content_lower for p in permission_patterns)
                    
                    is_permission_request = is_question and is_short and has_no_tool_output and pattern_match
                    
                    if is_permission_request:
                        # Convert to permission signal so chat can handle it
                        self._pending_permission = {
                            'question': content,
                            'awaiting': True,
                            'fallback': True  # Mark as fallback detection
                        }
                        final_response = f"__PERMISSION_REQUIRED__\n🔔 {content}\n[yes] / [no] (or type a custom response)"
                        
                        # Track reliability stats (ENH-004)
                        self._record_model_stat('text_permission', False)
                    else:
                        final_response = content
                        # Track successful non-tool response
                        self._record_model_stat('text_response', True)
                    break
                
                # Execute tool calls
                for tc in tool_calls:
                    tool_name = tc.get('name', '')
                    tool_args = tc.get('arguments', {})
                    
                    if on_tool_start:
                        on_tool_start(f"{tool_name}({tool_args})")
                    
                    # Execute tool (inherited from BaseAgent)
                    tool_result = self._execute_tool(tool_name, tool_args)
                    
                    # Cache tool result for context persistence across turns
                    # This fixes "AI forgets what it saw" when user says "yes, continue"
                    if tool_result.success:
                        self.cache_tool_result(tool_name, tool_result.result, tool_result.elapsed)
                    
                    # Track tool call for reliability stats (ENH-004)
                    self._record_model_stat('tool_call', tool_result.success, tool_result.elapsed)
                    
                    if on_tool_complete:
                        status = "✓" if tool_result.success else "✗"
                        on_tool_complete(tool_name, f"{status} {tool_result.elapsed:.1f}s")
                    
                    # CRITICAL: If ask_user was called, stop immediately and return
                    # This allows the chat loop to show the permission prompt
                    # NOTE: Only treat __PERMISSION_REQUIRED__ as a signal if it's from ask_user/write_file/run_command
                    # NOT if it's just text content (e.g., recall_memory mentioning the permission system)
                    is_permission_tool = tool_name in ("ask_user", "write_file", "run_command")
                    has_permission_signal = "__PERMISSION_REQUIRED__" in tool_result.result
                    
                    if is_permission_tool and has_permission_signal:
                        self.stats.total_time = time.time() - start_time
                        return tool_result.result
                    
                    # Add to messages for next iteration
                    messages.append({
                        "role": "assistant",
                        "content": content,
                        "tool_calls": [{
                            "id": tc.get('id', f"call_{tool_name}"),
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args)
                            }
                        }]
                    })
                    
                    # Build tool result content with action reminder
                    tool_content = tool_result.result if tool_result.success else f"Error: {tool_result.error}"
                    
                    # Add reminder to use write_file after reading
                    if tool_name == "read_file" and tool_result.success:
                        tool_content += "\n\n[SYSTEM: If you need to modify this file, call write_file() now. Do NOT explain in text - call the tool directly.]"
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get('id', f"call_{tool_name}"),
                        "content": tool_content
                    })
                
            except Exception as e:
                if self.debug:
                    print(f"[OpenRouterAgent] Error: {e}")
                
                # Try without tools on error
                try:
                    for token in self.client.chat_stream(
                        model=self.model_name,
                        messages=messages,
                        on_token=on_token
                    ):
                        final_response += token
                except Exception as e2:
                    final_response = f"Error: {e2}"
                
                break
        
        self.stats.total_time = time.time() - start_time
        
        return final_response

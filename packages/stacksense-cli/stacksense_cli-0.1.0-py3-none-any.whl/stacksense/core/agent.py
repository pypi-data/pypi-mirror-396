"""
StackSense Agent - Agentic Architecture
========================================
AI decides what tools to use, when to use them.
Uses Option B: Simulated tool calling (reliable, proven).

The AI reads STACKSENSE.md as its system prompt and orchestrates
your existing code as "tools".
"""

import os
import re
import json
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any, AsyncGenerator
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    """Result from a tool execution"""
    success: bool
    result: str
    error: Optional[str] = None
    elapsed: float = 0.0


@dataclass
class AgentStats:
    """Performance statistics for agent"""
    tools_used: int = 0
    total_time: float = 0.0
    tool_times: Dict[str, float] = field(default_factory=dict)
    tokens_estimated: int = 0


class StackSenseAgent:
    """
    AI Agent that orchestrates existing StackSense tools.
    
    Uses simulated tool calling (Option B) for reliability.
    The AI outputs "TOOL: function()" and we parse + execute.
    
    Existing code (your slicers, grep, diagram builder) becomes
    "tools" the AI can call.
    """
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        model_name: str = "qwen2.5:7b-instruct-q4_K_M",
        ollama_url: str = "http://localhost:11434",
        debug: bool = False
    ):
        self.workspace_path = Path(workspace_path) if workspace_path else None
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.debug = debug
        
        # Load STACKSENSE.md as system prompt
        self.system_prompt = self._load_system_prompt()
        
        # Initialize tools (wrap your existing code)
        self._init_tools()
        
        # Stats
        self.stats = AgentStats()
        
        # Tool budget
        self.max_tools = 8
    
    def _load_system_prompt(self) -> str:
        """Load STACKSENSE.md as the AI's brain"""
        
        # Try to find STACKSENSE.md
        search_paths = [
            Path(__file__).parent.parent / "STACKSENSE.md",
            Path(__file__).parent.parent.parent / "STACKSENSE.md",
            Path.cwd() / "STACKSENSE.md",
        ]
        
        for path in search_paths:
            if path.exists():
                with open(path, 'r') as f:
                    return f.read()
        
        # Fallback minimal prompt
        return """You are StackSense, an AI coding assistant.
        
Available tools:
- TOOL: get_diagram() - See codebase structure
- TOOL: read_file(filepath="path") - Read a file
- TOOL: search_code(keywords="a,b,c") - Search code
- TOOL: recall_memory() - Remember past learnings
- TOOL: save_learning(topic="x", summary="y") - Save insight
- TOOL: web_search(query="x") - Search web (only with @search)

Use ONE tool at a time. Say TOOL: followed by the function call.
When done exploring, answer the user's question."""
    
    def _init_tools(self):
        """Initialize tool executors (wrap existing code)"""
        
        # Import existing code as tools
        if self.workspace_path:
            try:
                from stacksense.core.diagram_builder import DiagramBuilder
                self.diagram_builder = DiagramBuilder(str(self.workspace_path))
            except ImportError:
                self.diagram_builder = None
            
            try:
                from stacksense.agents.slice_extractor_agent import SliceExtractorAgent
                self.slicer = SliceExtractorAgent()
            except ImportError:
                self.slicer = None
            
            try:
                from stacksense.agents.memory_writer_agent import MemoryWriterAgent
                self.memory_agent = MemoryWriterAgent(str(self.workspace_path))
            except ImportError:
                self.memory_agent = None
        else:
            self.diagram_builder = None
            self.slicer = None
            self.memory_agent = None
        
        # Tool registry
        self.tools: Dict[str, Callable] = {
            "get_diagram": self._tool_get_diagram,
            "read_file": self._tool_read_file,
            "search_code": self._tool_search_code,
            "recall_memory": self._tool_recall_memory,
            "save_learning": self._tool_save_learning,
            "web_search": self._tool_web_search,
        }
    
    # ═══════════════════════════════════════════════════════════
    # TOOL IMPLEMENTATIONS (Wrap your existing code)
    # ═══════════════════════════════════════════════════════════
    
    def _tool_get_diagram(self) -> str:
        """Get codebase structure using YOUR DiagramBuilder"""
        
        if not self.workspace_path:
            return "Error: No workspace selected"
        
        # Check for cached diagram
        diagram_path = self.workspace_path / ".stacksense" / "dependency_graph.json"
        
        if diagram_path.exists():
            try:
                with open(diagram_path) as f:
                    diagram = json.load(f)
                
                nodes = diagram.get('nodes', [])
                
                # Format for AI
                lines = [f"📁 Codebase: {len(nodes)} files"]
                
                # Group by directory
                dirs = {}
                for node in nodes:
                    node_id = node.get('id', '')
                    dir_name = str(Path(node_id).parent) if '/' in node_id else 'root'
                    if dir_name not in dirs:
                        dirs[dir_name] = []
                    dirs[dir_name].append(Path(node_id).name)
                
                for dir_name, files in list(dirs.items())[:10]:
                    lines.append(f"\n{dir_name}/")
                    for f in files[:5]:
                        lines.append(f"  • {f}")
                    if len(files) > 5:
                        lines.append(f"  • ... +{len(files)-5} more")
                
                return '\n'.join(lines)
            except:
                pass
        
        # Fallback: basic file listing
        try:
            files = list(self.workspace_path.glob("**/*.py"))
            files = [f for f in files if 'venv' not in str(f) and '__pycache__' not in str(f)]
            
            lines = [f"📁 Python files: {len(files)}"]
            for f in files[:15]:
                lines.append(f"  • {f.relative_to(self.workspace_path)}")
            if len(files) > 15:
                lines.append(f"  ... +{len(files)-15} more")
            
            return '\n'.join(lines)
        except Exception as e:
            return f"Error reading workspace: {e}"
    
    def _tool_read_file(self, filepath: str, context: str = "") -> str:
        """Read file using YOUR SliceExtractorAgent for large files"""
        
        if not self.workspace_path:
            return "Error: No workspace selected"
        
        # Find the file
        full_path = self.workspace_path / filepath
        
        if not full_path.exists():
            # Try searching for it
            matches = list(self.workspace_path.glob(f"**/{Path(filepath).name}"))
            matches = [m for m in matches if 'venv' not in str(m)]
            
            if matches:
                full_path = matches[0]
            else:
                return f"Error: File not found: {filepath}"
        
        try:
            content = full_path.read_text()
            lines = content.split('\n')
            line_count = len(lines)
            
            # Decide if slicing is needed
            if line_count < 300:
                # Small file - return whole thing
                return f"📄 {filepath} ({line_count} lines)\n{'─'*50}\n{content}"
            
            elif self.slicer and context:
                # Large file with context - use YOUR slicer
                try:
                    slices = self.slicer.extract_relevant(content, context, max_chars=4000)
                    return f"📄 {filepath} ({line_count} lines, sliced for: {context})\n{'─'*50}\n{slices}"
                except:
                    pass
            
            # Fallback: truncate
            truncated = '\n'.join(lines[:200])
            return f"📄 {filepath} ({line_count} lines, showing first 200)\n{'─'*50}\n{truncated}\n\n... (truncated)"
        
        except Exception as e:
            return f"Error reading {filepath}: {e}"
    
    def _tool_search_code(self, keywords: str) -> str:
        """Search codebase using grep"""
        
        if not self.workspace_path:
            return "Error: No workspace selected"
        
        keyword_list = [k.strip() for k in keywords.split(',')]
        
        results = {}
        
        for keyword in keyword_list[:5]:  # Max 5 keywords
            try:
                import subprocess
                result = subprocess.run(
                    ['grep', '-r', '-l', '-i', keyword, str(self.workspace_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                files = [f for f in result.stdout.strip().split('\n') if f]
                files = [f for f in files if 'venv' not in f and '__pycache__' not in f]
                
                for f in files:
                    rel_path = str(Path(f).relative_to(self.workspace_path))
                    if rel_path not in results:
                        results[rel_path] = []
                    results[rel_path].append(keyword)
            except:
                pass
        
        if not results:
            return f"No results for: {keywords}"
        
        lines = [f"🔍 Search results for: {keywords}"]
        for filepath, matched_keywords in sorted(results.items(), key=lambda x: -len(x[1]))[:10]:
            lines.append(f"  • {filepath} (matched: {', '.join(matched_keywords)})")
        
        if len(results) > 10:
            lines.append(f"  ... +{len(results)-10} more files")
        
        return '\n'.join(lines)
    
    def _tool_recall_memory(self) -> str:
        """Recall learnings using YOUR MemoryWriterAgent"""
        
        if not self.workspace_path:
            return "No workspace - no memory available"
        
        memory_path = self.workspace_path / ".stacksense" / "ai_memory.json"
        
        if not memory_path.exists():
            return "No previous learnings for this workspace"
        
        try:
            with open(memory_path) as f:
                memory = json.load(f)
            
            learnings = memory.get('learnings', {})
            
            if not learnings:
                return "Memory exists but no learnings recorded"
            
            lines = ["📚 Previous learnings:"]
            for topic, entries in learnings.items():
                lines.append(f"\n**{topic}**:")
                for entry in entries[-2:]:  # Last 2 per topic
                    if 'learnings' in entry:
                        for learning in entry['learnings'][:2]:
                            insight = learning.get('insight', str(learning))
                            lines.append(f"  • {insight[:100]}")
            
            return '\n'.join(lines)
        except Exception as e:
            return f"Error reading memory: {e}"
    
    def _tool_save_learning(self, topic: str, summary: str) -> str:
        """Save learning using YOUR MemoryWriterAgent"""
        
        if not self.workspace_path:
            return "No workspace - cannot save"
        
        if self.memory_agent:
            try:
                self.memory_agent.write_ai_learning(
                    str(self.workspace_path),
                    self.workspace_path.name,
                    topic,
                    {"summary": summary, "saved_by": "agent"}
                )
                return f"✓ Saved learning about: {topic}"
            except:
                pass
        
        # Fallback: direct file write
        memory_path = self.workspace_path / ".stacksense" / "ai_memory.json"
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if memory_path.exists():
                with open(memory_path) as f:
                    memory = json.load(f)
            else:
                memory = {"learnings": {}}
            
            if topic not in memory["learnings"]:
                memory["learnings"][topic] = []
            
            memory["learnings"][topic].append({
                "summary": summary,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            })
            
            with open(memory_path, 'w') as f:
                json.dump(memory, f, indent=2)
            
            return f"✓ Saved learning about: {topic}"
        except Exception as e:
            return f"Error saving: {e}"
    
    def _tool_web_search(self, query: str) -> str:
        """Web search - only when explicitly requested or truly needed"""
        
        # This is expensive - should be rare
        try:
            from stacksense.web.web_searcher import WebSearcher
            searcher = WebSearcher(debug=False)
            results = searcher.search(query, max_results=3)
            
            if not results:
                return "No web results found"
            
            lines = [f"🌐 Web search: {query}"]
            for r in results[:3]:
                lines.append(f"\n{r.get('title', 'No title')}")
                lines.append(f"  {r.get('snippet', '')[:200]}")
                lines.append(f"  Source: {r.get('url', '')}")
            
            return '\n'.join(lines)
        except Exception as e:
            return f"Web search unavailable: {e}"
    
    # ═══════════════════════════════════════════════════════════
    # TOOL PARSING (Simulated tool calling - Option B)
    # ═══════════════════════════════════════════════════════════
    
    def _parse_tool_call(self, text: str) -> Optional[Dict]:
        """
        Parse TOOL: function(args) from AI response.
        
        Patterns supported:
        - TOOL: get_diagram()
        - TOOL: read_file(filepath="auth.py")
        - TOOL: search_code(keywords="auth, login")
        """
        
        # Pattern: TOOL: function_name(args)
        pattern = r'TOOL:\s*(\w+)\s*\(([^)]*)\)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if not match:
            return None
        
        tool_name = match.group(1)
        args_str = match.group(2).strip()
        
        # Parse arguments
        args = {}
        if args_str:
            # Pattern: key="value" or key='value'
            arg_pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
            for arg_match in re.finditer(arg_pattern, args_str):
                args[arg_match.group(1)] = arg_match.group(2)
        
        return {
            'name': tool_name,
            'args': args,
            'raw': match.group(0)
        }
    
    def _execute_tool(self, tool_call: Dict) -> ToolResult:
        """Execute a tool and return result"""
        
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                result="",
                error=f"Unknown tool: {tool_name}"
            )
        
        start = time.time()
        
        try:
            tool_fn = self.tools[tool_name]
            result = tool_fn(**tool_args)
            elapsed = time.time() - start
            
            # Track stats
            self.stats.tools_used += 1
            self.stats.tool_times[tool_name] = elapsed
            
            return ToolResult(success=True, result=result, elapsed=elapsed)
        
        except Exception as e:
            elapsed = time.time() - start
            return ToolResult(
                success=False,
                result="",
                error=str(e),
                elapsed=elapsed
            )
    
    # ═══════════════════════════════════════════════════════════
    # CHAT LOOP (TRUE STREAMING)
    # ═══════════════════════════════════════════════════════════
    
    async def chat(
        self,
        user_query: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str], None]] = None,
        on_tool_complete: Optional[Callable[[str, str], None]] = None
    ) -> str:
        """
        Process a query with true streaming.
        
        Args:
            user_query: User's question
            on_token: Callback for each token (for live display)
            on_tool_start: Callback when tool starts
            on_tool_complete: Callback when tool completes
            
        Returns:
            Final answer string
        """
        import requests
        
        self.stats = AgentStats()  # Reset stats
        start_time = time.time()
        
        # Build conversation
        messages = [
            {"role": "system", "content": self.system_prompt[:6000]},  # Truncate if needed
            {"role": "user", "content": user_query}
        ]
        
        full_response = ""
        
        # Conversation loop
        while self.stats.tools_used < self.max_tools:
            
            # Generate AI response with streaming
            response_text = await self._stream_generate(messages, on_token)
            full_response = response_text
            
            # Check for tool call
            tool_call = self._parse_tool_call(response_text)
            
            if tool_call:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                if on_tool_start:
                    on_tool_start(f"{tool_name}({tool_args})")
                
                # Execute tool
                result = self._execute_tool(tool_call)
                
                if on_tool_complete:
                    status = "✓" if result.success else "✗"
                    on_tool_complete(tool_name, f"{status} {result.elapsed:.1f}s")
                
                # Add to conversation
                messages.append({"role": "assistant", "content": response_text})
                
                tool_result = result.result if result.success else f"Error: {result.error}"
                messages.append({
                    "role": "user",
                    "content": f"TOOL RESULT:\n{tool_result[:3000]}"  # Truncate long results
                })
                
                # Continue conversation
                continue
            
            else:
                # No tool call - AI is done
                break
        
        self.stats.total_time = time.time() - start_time
        
        return full_response
    
    async def _stream_generate(
        self,
        messages: List[Dict],
        on_token: Optional[Callable[[str], None]] = None
    ) -> str:
        """Generate response with true streaming"""
        
        import requests
        
        # Convert messages to Ollama format
        prompt = ""
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt += f"{content}\n\n"
            elif role == 'user':
                prompt += f"User: {content}\n\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n\n"
        
        prompt += "Assistant: "
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': True,
                    'keep_alive': '30m',
                    'options': {
                        'num_predict': 1500,
                        'temperature': 0.3
                    }
                },
                stream=True,
                timeout=180
            )
            
            full_response = []
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        token = data.get('response', '')
                        if token:
                            full_response.append(token)
                            if on_token:
                                on_token(token)
                    except json.JSONDecodeError:
                        pass
            
            return ''.join(full_response)
        
        except Exception as e:
            return f"Error generating response: {e}"
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            'tools_used': self.stats.tools_used,
            'total_time': round(self.stats.total_time, 2),
            'tool_times': self.stats.tool_times
        }


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════

def create_agent(
    workspace_path: Optional[str] = None,
    model_name: str = "qwen2.5:7b-instruct-q4_K_M"
) -> StackSenseAgent:
    """Create a StackSense agent"""
    return StackSenseAgent(
        workspace_path=workspace_path,
        model_name=model_name
    )

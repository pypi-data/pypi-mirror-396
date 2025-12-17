"""
StackSense Agent - Native Tool Calling (Option A)
=================================================
Uses Ollama's native tool/function calling API.
AI MUST return structured JSON to call tools - can't hallucinate.

This is more reliable than simulated (Option B) because:
- AI returns structured tool calls, not text mentioning tools
- Tools either execute or fail - no fake responses
- Clear separation between thinking and tool usage
"""

import os
import re
import json
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    result: str
    error: Optional[str] = None
    elapsed: float = 0.0


@dataclass
class AgentStats:
    """Performance stats"""
    tools_used: int = 0
    total_time: float = 0.0
    tool_times: Dict[str, float] = field(default_factory=dict)


class NativeToolAgent:
    """
    StackSense Agent using Ollama's native tool calling.
    
    The AI returns structured JSON tool calls, not text.
    This prevents hallucination - tools either work or fail.
    """
    
    # Tool definitions in Ollama format
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "get_diagram",
                "description": "Get codebase structure showing files, directories, and architecture. Use this FIRST to understand what files exist.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read contents of a specific file. For large files, relevant sections are extracted automatically.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to file relative to workspace root"
                        },
                        "context": {
                            "type": "string",
                            "description": "What you're looking for (helps extract relevant sections)"
                        }
                    },
                    "required": ["filepath"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_code",
                "description": "Search for keywords across the codebase using grep. Returns files containing the terms.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "Comma-separated keywords to search for"
                        }
                    },
                    "required": ["keywords"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "recall_memory",
                "description": "Remember what you learned about this codebase in previous sessions. Always check this FIRST.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "save_learning",
                "description": "Save an important insight about the codebase for future reference.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Short topic name (e.g., 'authentication', 'database')"
                        },
                        "summary": {
                            "type": "string",
                            "description": "What you learned (1-3 sentences)"
                        }
                    },
                    "required": ["topic", "summary"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for information. Only use when user explicitly requests with @search or when codebase has no answer.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
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
        
        # Load gitignore patterns if workspace exists
        self.gitignore_patterns = self._load_gitignore()
        
        # System prompt (loads from STACKSENSE.md)
        self.system_prompt = self._load_stacksense_md()
        
        # Stats
        self.stats = AgentStats()
        self.max_tools = 6  # Updated to match STACKSENSE.md
    
    def _load_gitignore(self) -> List[str]:
        """Load ignore patterns from .gitignore, .dockerignore, etc."""
        patterns = []
        
        if not self.workspace_path:
            return patterns
        
        # Files to check
        ignore_files = ['.gitignore', '.dockerignore', '.npmignore', '.eslintignore']
        
        for ignore_file in ignore_files:
            ignore_path = self.workspace_path / ignore_file
            if ignore_path.exists():
                try:
                    with open(ignore_path) as f:
                        for line in f:
                            line = line.strip()
                            # Skip comments and empty lines
                            if line and not line.startswith('#'):
                                patterns.append(line.rstrip('/'))
                except:
                    pass
        
        # Fallback common patterns if no ignore files found
        if not patterns:
            patterns = [
                'venv', '.venv', 'env', 'node_modules', '__pycache__',
                '.git', 'dist', 'build', 'out', '.env', '.pytest_cache',
                'egg-info', '.tox', '.mypy_cache', 'coverage', '.DS_Store'
            ]
        
        return patterns
    
    def _load_stacksense_md(self) -> str:
        """Load STACKSENSE.md for AI context and inject current date/time"""
        from datetime import datetime
        
        # Try to find STACKSENSE.md
        search_paths = [
            Path(__file__).parent.parent / "STACKSENSE.md",
            Path(__file__).parent.parent.parent / "STACKSENSE.md",
            Path.cwd() / "STACKSENSE.md",
        ]
        
        content = None
        for path in search_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                    break
                except:
                    pass
        
        # Fallback minimal prompt if file not found
        if not content:
            content = """You are StackSense, an AI coding assistant created by PilgrimStack.

{{CURRENT_DATE}}

IMPORTANT RULES:
1. For simple questions (greetings, math, general knowledge) - answer directly, no tools
2. For codebase questions - use tools to find real information
3. Always use recall_memory() or get_diagram() FIRST
4. Never make up file paths - use search_code() first
5. You CANNOT modify project files - only provide helpful examples
6. Be concise and helpful

When you have enough information, provide a clear answer."""
        
        # Inject current date/time
        now = datetime.now()
        date_string = f"""**Current Date & Time**: {now.strftime("%B %d, %Y at %I:%M %p")}
- Year: {now.year}
- Month: {now.strftime("%B")}
- Day: {now.day}

**IMPORTANT**: Your training data ends before {now.year}. If asked about:
- Framework versions released in {now.year}
- Recent technologies or best practices
- "Latest" or "current" anything
→ Use web_search() to get {now.year} information!"""
        
        # Replace placeholder
        content = content.replace("{{CURRENT_DATE}}", date_string)
        
        return content

    
    # ═══════════════════════════════════════════════════════════
    # TOOL IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════
    
    def _tool_get_diagram(self) -> str:
        """Get codebase structure"""
        if not self.workspace_path:
            return "No workspace selected - general chat mode"
        
        # Check for cached diagram
        diagram_path = self.workspace_path / ".stacksense" / "dependency_graph.json"
        
        if diagram_path.exists():
            try:
                with open(diagram_path) as f:
                    diagram = json.load(f)
                
                nodes = diagram.get('nodes', [])
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
            # Filter out gitignored paths
            files = [f for f in files if not self._is_gitignored(f)]
            
            lines = [f"📁 Python files: {len(files)}"]
            for f in files[:15]:
                lines.append(f"  • {f.relative_to(self.workspace_path)}")
            if len(files) > 15:
                lines.append(f"  ... +{len(files)-15} more")
            
            return '\n'.join(lines)
        except Exception as e:
            return f"Error reading workspace: {e}"
    
    def _is_gitignored(self, filepath: Path) -> bool:
        """Check if file matches gitignore patterns"""
        if not self.gitignore_patterns:
            return False
        
        # Get path relative to workspace
        try:
            if self.workspace_path:
                rel_path = str(filepath.relative_to(self.workspace_path))
            else:
                rel_path = str(filepath)
        except:
            rel_path = str(filepath)
        
        # Check against patterns
        for pattern in self.gitignore_patterns:
            # Simple pattern matching (handles most common cases)
            if pattern in rel_path or rel_path.startswith(pattern + '/'):
                return True
            # Handle glob-like patterns
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(rel_path, pattern):
                    return True
        
        return False
    
    def _tool_read_file(self, filepath: str, context: str = "") -> str:
        """Read file contents"""
        if not self.workspace_path:
            return "No workspace selected"
        
        # Find the file
        full_path = self.workspace_path / filepath
        
        if not full_path.exists():
            # Try searching for it
            matches = list(self.workspace_path.glob(f"**/{Path(filepath).name}"))
            matches = [m for m in matches if not self._is_gitignored(m)]
            
            if matches:
                full_path = matches[0]
                filepath = str(full_path.relative_to(self.workspace_path))
            else:
                return f"File not found: {filepath}. Use search_code() to find files."
        
        if self._is_gitignored(full_path):
            return f"File {filepath} is in a gitignored directory"
        
        try:
            content = full_path.read_text()
            lines = content.split('\n')
            line_count = len(lines)
            
            if line_count < 300:
                return f"📄 {filepath} ({line_count} lines)\n{'─'*40}\n{content}"
            else:
                # Truncate large files
                truncated = '\n'.join(lines[:150])
                return f"📄 {filepath} ({line_count} lines, showing first 150)\n{'─'*40}\n{truncated}\n\n... (truncated, {line_count-150} more lines)"
        
        except Exception as e:
            return f"Error reading {filepath}: {e}"
    
    def _tool_search_code(self, keywords: str) -> str:
        """Search codebase"""
        if not self.workspace_path:
            return "No workspace selected"
        
        keyword_list = [k.strip() for k in keywords.split(',')]
        results = {}
        
        for keyword in keyword_list[:5]:
            try:
                import subprocess
                result = subprocess.run(
                    ['grep', '-r', '-l', '-i', keyword, str(self.workspace_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                files = [f for f in result.stdout.strip().split('\n') if f]
                files = [f for f in files if not self._is_gitignored(Path(f))]
                
                for f in files:
                    try:
                        rel_path = str(Path(f).relative_to(self.workspace_path))
                        if rel_path not in results:
                            results[rel_path] = []
                        results[rel_path].append(keyword)
                    except:
                        pass
            except:
                pass
        
        if not results:
            return f"No results for: {keywords}"
        
        lines = [f"🔍 Found {len(results)} files for: {keywords}"]
        for filepath, matched in sorted(results.items(), key=lambda x: -len(x[1]))[:10]:
            lines.append(f"  • {filepath}")
        
        return '\n'.join(lines)
    
    def _tool_recall_memory(self) -> str:
        """Recall learnings"""
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
                return "No learnings recorded yet"
            
            lines = ["📚 Previous learnings:"]
            for topic, entries in learnings.items():
                lines.append(f"\n**{topic}**:")
                for entry in entries[-2:]:
                    summary = entry.get('summary', str(entry))
                    lines.append(f"  • {summary[:100]}")
            
            return '\n'.join(lines)
        except Exception as e:
            return f"Error reading memory: {e}"
    
    def _tool_save_learning(self, topic: str, summary: str) -> str:
        """Save learning"""
        if not self.workspace_path:
            return "No workspace - cannot save"
        
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
        """Web search"""
        try:
            from stacksense.web.web_searcher import WebSearcher
            searcher = WebSearcher(debug=False)
            results = searcher.search(query, max_results=3)
            
            if not results:
                return "No web results found"
            
            lines = [f"🌐 Web search: {query}"]
            for r in results[:3]:
                lines.append(f"\n{r.get('title', 'No title')}")
                lines.append(f"  {r.get('snippet', '')[:150]}")
            
            return '\n'.join(lines)
        except Exception as e:
            return f"Web search unavailable: {e}"
    
    def _execute_tool(self, name: str, args: dict) -> ToolResult:
        """Execute a tool by name"""
        start = time.time()
        
        tool_map = {
            "get_diagram": lambda: self._tool_get_diagram(),
            "read_file": lambda: self._tool_read_file(
                args.get('filepath', ''),
                args.get('context', '')
            ),
            "search_code": lambda: self._tool_search_code(args.get('keywords', '')),
            "recall_memory": lambda: self._tool_recall_memory(),
            "save_learning": lambda: self._tool_save_learning(
                args.get('topic', ''),
                args.get('summary', '')
            ),
            "web_search": lambda: self._tool_web_search(args.get('query', ''))
        }
        
        if name not in tool_map:
            return ToolResult(False, "", f"Unknown tool: {name}", 0)
        
        try:
            result = tool_map[name]()
            elapsed = time.time() - start
            
            self.stats.tools_used += 1
            self.stats.tool_times[name] = elapsed
            
            return ToolResult(True, result, None, elapsed)
        except Exception as e:
            return ToolResult(False, "", str(e), time.time() - start)
    
    # ═══════════════════════════════════════════════════════════
    # NATIVE TOOL CALLING CHAT
    # ═══════════════════════════════════════════════════════════
    
    async def chat(
        self,
        user_query: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str], None]] = None,
        on_tool_complete: Optional[Callable[[str, str], None]] = None
    ) -> str:
        """
        Process query using Ollama's native tool calling.
        
        The AI returns structured tool_calls instead of text.
        This prevents hallucination.
        """
        import requests
        
        self.stats = AgentStats()
        start_time = time.time()
        
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        # Conversation loop - AI decides when to use tools
        final_response = ""
        
        while self.stats.tools_used < self.max_tools:
            try:
                # Call Ollama with tools
                response = requests.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "tools": self.TOOLS if self.workspace_path else [],  # No tools for general chat
                        "stream": True,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 1500
                        }
                    },
                    stream=True,
                    timeout=180
                )
                
                # Process streaming response
                current_content = ""
                tool_calls = []
                
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # Get message content
                        msg = data.get('message', {})
                        
                        # Stream text tokens
                        content = msg.get('content', '')
                        if content:
                            current_content += content
                            if on_token:
                                on_token(content)
                        
                        # Check for tool calls
                        if 'tool_calls' in msg:
                            tool_calls = msg['tool_calls']
                        
                        # Check if done
                        if data.get('done', False):
                            break
                            
                    except json.JSONDecodeError:
                        continue
                
                # If AI made tool calls, execute them
                if tool_calls:
                    for tool_call in tool_calls:
                        func = tool_call.get('function', {})
                        tool_name = func.get('name', '')
                        tool_args = func.get('arguments', {})
                        
                        if isinstance(tool_args, str):
                            try:
                                tool_args = json.loads(tool_args)
                            except:
                                tool_args = {}
                        
                        if on_tool_start:
                            on_tool_start(f"{tool_name}({tool_args})")
                        
                        # Execute tool
                        result = self._execute_tool(tool_name, tool_args)
                        
                        if on_tool_complete:
                            status = "✓" if result.success else "✗"
                            on_tool_complete(tool_name, f"{status} {result.elapsed:.1f}s")
                        
                        # Add tool call and result to messages
                        messages.append({
                            "role": "assistant",
                            "content": current_content,
                            "tool_calls": [tool_call]
                        })
                        
                        messages.append({
                            "role": "tool",
                            "content": result.result if result.success else f"Error: {result.error}"
                        })
                    
                    # Continue conversation with tool results
                    continue
                
                else:
                    # No tool calls - AI is done
                    final_response = current_content
                    break
                    
            except Exception as e:
                if self.debug:
                    print(f"Error in chat: {e}")
                final_response = f"Error: {e}"
                break
        
        self.stats.total_time = time.time() - start_time
        
        return final_response
    
    def get_stats(self) -> Dict:
        """Get performance stats"""
        return {
            'tools_used': self.stats.tools_used,
            'total_time': round(self.stats.total_time, 2),
            'tool_times': self.stats.tool_times
        }


# Convenience function
def create_native_agent(
    workspace_path: Optional[str] = None,
    model_name: str = "qwen2.5:7b-instruct-q4_K_M"
) -> NativeToolAgent:
    """Create a native tool calling agent"""
    return NativeToolAgent(
        workspace_path=workspace_path,
        model_name=model_name
    )

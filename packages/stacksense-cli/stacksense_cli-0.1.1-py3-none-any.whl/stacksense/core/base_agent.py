"""
Base Agent - Shared Tool Implementation
=======================================
Base class for all AI agents with tool calling support.
All providers (OpenRouter, OpenAI, Grok, Together) inherit from this.
"""

import os
import re
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Import centralized path resolution
from .config import get_workspace_path

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


class BaseAgent(ABC):
    """
    Base class for StackSense AI Agents.
    
    Provides:
    - Shared tool definitions (OpenAI format)
    - Tool implementations (get_diagram, read_file, search_code, etc.)
    - Permission system for dangerous operations
    
    Subclasses must implement:
    - chat() - The actual API call to the provider
    - get_stats() - Return performance stats
    """
    
    # Tool definitions (OpenAI format - works with all providers)
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
                "description": "Remember what you learned about this codebase in previous sessions.",
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
                "description": "Search the web for information about technologies, frameworks, or APIs you don't know.",
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
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Create or modify a file. Returns PERMISSION_REQUIRED signal - permission is handled automatically by the chat loop.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to file relative to workspace root"
                        },
                        "content": {
                            "type": "string",
                            "description": "Full content to write to the file"
                        },
                        "description": {
                            "type": "string",
                            "description": "What this change does"
                        }
                    },
                    "required": ["filepath", "content", "description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "Execute a terminal command. Returns PERMISSION_REQUIRED signal - permission is handled automatically by the chat loop.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute"
                        },
                        "working_directory": {
                            "type": "string",
                            "description": "Directory to run command in (optional)"
                        }
                    },
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "ask_user",
                "description": "MANDATORY for permissions. Call this to ask the user a question or request permission. DO NOT write permission requests in text - the user cannot respond to text. Always use this tool for any yes/no decisions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to ask the user"
                        },
                        "options": {
                            "type": "string",
                            "description": "Comma-separated options (e.g., 'yes,no' or 'option1,option2')"
                        }
                    },
                    "required": ["question"]
                }
            }
        }
    ]
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        model_name: str = None,
        debug: bool = False
    ):
        self.workspace_path = Path(workspace_path) if workspace_path else None
        self.model_name = model_name or self.get_default_model()
        self.debug = debug
        
        # Load gitignore patterns
        self.gitignore_patterns = self._load_gitignore()
        
        # Load system prompt from STACKSENSE.md with subscription info
        self.system_prompt = self._load_stacksense_md()
        
        # Stats
        self.stats = AgentStats()
        self.max_tools = 6
        
        # Permission system
        self._permission_granted = False
        self._pending_permission = {}
        
        # Cache subscription-based tools
        self._available_tools = None
        
        # Tool results cache - persists tool outputs across conversation turns
        # This fixes the "AI forgets what it saw" issue when user says "yes, continue"
        self.tool_results_cache: List[Dict[str, Any]] = []
        self.max_cached_results = 5  # Keep last 5 tool results
    
    # Static fallback tools (all tools, no filtering)
    _STATIC_TOOLS = [
        {"type": "function", "function": {"name": "get_diagram", "description": "Get codebase structure", "parameters": {"type": "object", "properties": {}, "required": []}}},
        {"type": "function", "function": {"name": "read_file", "description": "Read file contents", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]}}},
        {"type": "function", "function": {"name": "search_code", "description": "Search for keywords", "parameters": {"type": "object", "properties": {"keywords": {"type": "string"}}, "required": ["keywords"]}}},
        {"type": "function", "function": {"name": "ask_user", "description": "Ask the user a question", "parameters": {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]}}},
    ]
    
    def get_available_tools(self) -> List[dict]:
        """
        Get tools available to the current user based on their subscription.
        
        This method respects feature gating - users only see tools
        they have access to in their plan.
        """
        if self._available_tools is not None:
            return self._available_tools
        
        try:
            from stacksense.providers.tools import get_tools_for_subscription
            tools = get_tools_for_subscription(include_dangerous=True)
            self._available_tools = [t.to_openai_format() for t in tools]
        except Exception as e:
            if self.debug:
                print(f"[BaseAgent] Error loading subscription tools: {e}")
            # Fall back to static tools (free tier)
            self._available_tools = self._STATIC_TOOLS
        
        return self._available_tools
    
    @property
    def TOOLS(self) -> List[dict]:
        """
        Tools property for backwards compatibility.
        Now returns subscription-aware tools.
        """
        return self.get_available_tools()
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Return the default model for this provider."""
        pass
    
    @abstractmethod
    async def chat(
        self,
        user_query: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str], None]] = None,
        on_tool_complete: Optional[Callable[[str, str], None]] = None
    ) -> str:
        """Process query with tool calling. Must be implemented by subclasses."""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current stats"""
        return {
            'tools_used': self.stats.tools_used,
            'total_time': self.stats.total_time,
            'tool_times': self.stats.tool_times
        }
    
    def _get_storage_path(self, *subdirs: str) -> Path:
        """
        Get the storage path for this workspace.
        
        Uses centralized ~/.stacksense/workspaces/{parent}/{repo}/ structure.
        This prevents accidental git pushes of .stacksense folders.
        
        Args:
            *subdirs: Optional subdirectories to append (e.g., "scan", "memory")
            
        Returns:
            Path to storage directory
        """
        base = get_workspace_path(str(self.workspace_path) if self.workspace_path else None)
        if subdirs:
            path = base.joinpath(*subdirs)
        else:
            path = base
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def cache_tool_result(self, tool_name: str, result: str, elapsed: float = 0.0):
        """
        Cache a tool result for context persistence across conversation turns.
        
        Keeps the last `max_cached_results` results so the AI can reference
        what it saw even when the user just says "yes" or "continue".
        """
        import time
        
        self.tool_results_cache.append({
            "tool": tool_name,
            "result": result,
            "elapsed": elapsed,
            "timestamp": time.time()
        })
        
        # Keep only last N results to manage context size
        if len(self.tool_results_cache) > self.max_cached_results:
            self.tool_results_cache.pop(0)
    
    def get_cached_tool_context(self) -> str:
        """
        Format cached tool results as context for API messages.
        
        This is injected into the beginning of each chat() call so the AI
        remembers what tools it used and what they returned.
        
        Returns:
            Formatted string of recent tool results, or empty string if none.
        """
        if not self.tool_results_cache:
            return ""
        
        lines = ["<recent_tool_results>"]
        for item in self.tool_results_cache[-3:]:  # Last 3 results only
            # Truncate long results to manage token usage
            result_str = str(item.get("result", ""))[:800]
            if len(str(item.get("result", ""))) > 800:
                result_str += "...[truncated]"
            lines.append(f"[{item['tool']}]: {result_str}")
        lines.append("</recent_tool_results>")
        
        return "\n".join(lines)
    
    # ═══════════════════════════════════════════════════════════
    # TOOL IMPLEMENTATIONS (Shared across all providers)
    # ═══════════════════════════════════════════════════════════
    
    def _load_gitignore(self) -> List[str]:
        """Load ignore patterns from .gitignore"""
        patterns = []
        
        if not self.workspace_path:
            return patterns
        
        ignore_files = ['.gitignore', '.dockerignore']
        
        for ignore_file in ignore_files:
            ignore_path = self.workspace_path / ignore_file
            if ignore_path.exists():
                try:
                    with open(ignore_path) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                patterns.append(line.rstrip('/'))
                except:
                    pass
        
        if not patterns:
            patterns = [
                'venv', '.venv', 'node_modules', '__pycache__',
                '.git', '.idea', '.vscode', 'dist', 'build'
            ]
        
        return patterns
    
    def _load_stacksense_md(self) -> str:
        """Load system prompt from STACKSENSE.md with subscription info"""
        from datetime import datetime
        
        # Build live datetime header (always included)
        now = datetime.now()
        datetime_header = f"""📅 CURRENT DATE & TIME (LIVE):
- Date: {now.strftime("%d/%m/%Y")} ({now.strftime("%A, %B %d, %Y")})
- Time: {now.strftime("%H:%M:%S")} (24-hour format)
- Year: {now.year}

⚠️ IMPORTANT: When searching for "today's news" or "latest" information, use the date above. We are in {now.year}, not 2024.

"""
        
        base_prompt = ""
        
        if self.workspace_path:
            md_path = self.workspace_path / "STACKSENSE.md"
            if md_path.exists():
                try:
                    base_prompt = md_path.read_text(encoding='utf-8')
                    base_prompt = base_prompt.replace("{{CURRENT_DATE}}", now.strftime("%Y-%m-%d"))
                    base_prompt = base_prompt.replace("{{CURRENT_TIME}}", now.strftime("%H:%M"))
                except:
                    pass
        
        if not base_prompt:
            base_prompt = """You are StackSense, an AI code assistant.
            
When answering questions:
1. Use tools to explore the codebase
2. Be specific and reference actual code
3. Provide working code examples
4. Stay concise but thorough"""
        
        # Add credit status info
        try:
            from stacksense.providers.tools import get_credit_status_message
            credit_status = get_credit_status_message()
            base_prompt = credit_status + "\n\n" + datetime_header + base_prompt
        except Exception:
            base_prompt = datetime_header + base_prompt
        
        return base_prompt
    
    def _smart_slice(self, content: str, format: str = "summary", max_lines: int = 50) -> dict:
        """
        Universal smart slicer for tool outputs.
        
        Args:
            content: Full text output
            format: Slicing strategy
                - "summary": First 30 + last 10 lines (default)
                - "full": No truncation
                - "first:N": First N lines
                - "last:N": Last N lines
                - "count": Just show count + preview
                - "structure": For code - show classes/functions only
            max_lines: Threshold before slicing kicks in
            
        Returns:
            dict with content, truncated flag, and metadata
        """
        if not content:
            return {"content": "", "truncated": False, "total_lines": 0}
        
        lines = content.split('\n')
        total = len(lines)
        
        # No slicing needed if under limit
        if format == "full" or total <= max_lines:
            return {
                "content": content,
                "truncated": False,
                "total_lines": total
            }
        
        # Summary: First 30 + last 10
        if format == "summary":
            head_count = min(30, total // 2)
            tail_count = min(10, total // 4)
            
            preview = '\n'.join(lines[:head_count])
            trailer = '\n'.join(lines[-tail_count:]) if tail_count > 0 else ""
            hidden = total - head_count - tail_count
            
            sliced = f"{preview}\n\n... ({hidden} lines hidden, use format='full' for complete output) ...\n\n{trailer}"
            return {
                "content": sliced,
                "truncated": True,
                "total_lines": total,
                "hint": f"Showing {head_count} + {tail_count} of {total} lines"
            }
        
        # First N lines
        if format.startswith("first:"):
            try:
                n = int(format.split(":")[1])
                return {
                    "content": '\n'.join(lines[:n]),
                    "truncated": n < total,
                    "total_lines": total,
                    "hint": f"Showing first {n} of {total} lines"
                }
            except:
                pass
        
        # Last N lines
        if format.startswith("last:"):
            try:
                n = int(format.split(":")[1])
                return {
                    "content": '\n'.join(lines[-n:]),
                    "truncated": n < total,
                    "total_lines": total,
                    "hint": f"Showing last {n} of {total} lines"
                }
            except:
                pass
        
        # Count + preview
        if format == "count":
            preview = '\n'.join(lines[:5])
            return {
                "content": f"Total: {total} lines\n\nPreview:\n{preview}\n...",
                "truncated": True,
                "total_lines": total,
                "hint": f"Showing preview of {total} lines"
            }
        
        # Structure (for code files)
        if format == "structure":
            structure_lines = []
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith(('class ', 'def ', 'async def ', 'function ', 'export ', 'import ')):
                    structure_lines.append(f"L{i+1}: {line}")
            
            if structure_lines:
                return {
                    "content": '\n'.join(structure_lines[:30]),
                    "truncated": True,
                    "total_lines": total,
                    "hint": f"Showing structure of {total} line file ({len(structure_lines)} items)"
                }
        
        # Default fallback: simple truncation
        return {
            "content": content[:3000] + f"\n\n... (truncated at 3000 chars, total: {len(content)} chars)",
            "truncated": True,
            "total_lines": total
        }
    
    def _tool_slice_output(self, content: str, format: str = "summary", search: str = "") -> str:
        """
        Re-slice content with a different format. AI can use this when default slicing
        didn't show what it was looking for.
        
        Args:
            content: The content to slice (or 'last' to use last tool output)
            format: Slicing format - summary, full, first:N, last:N, search
            search: If format='search', find lines containing this pattern
        """
        # If format is 'search', find matching lines
        if format == "search" and search:
            lines = content.split('\n')
            matches = []
            for i, line in enumerate(lines, 1):
                if search.lower() in line.lower():
                    # Show context: 2 lines before and after
                    start = max(0, i - 3)
                    end = min(len(lines), i + 2)
                    context = lines[start:end]
                    matches.append(f"Line {i}:\n" + '\n'.join(context))
            
            if not matches:
                return f"No matches found for '{search}'"
            
            return f"""🔍 **Found {len(matches)} matches for '{search}':**

""" + "\n\n---\n".join(matches[:10])
        
        # Use standard smart slicing
        result = self._smart_slice(content, format=format, max_lines=100)
        return result["content"] + (f"\n\n*{result.get('hint', '')}*" if result.get('truncated') else "")
    
    def _tool_get_diagram(self) -> str:
        """Get codebase structure"""
        if not self.workspace_path:
            return "No workspace loaded."
        
        # Use centralized storage path
        diagram_path = self._get_storage_path("scan", "diagrams") / "dependency_graph.json"
        
        # Also check legacy project path for backwards compatibility
        project_diagram = self.workspace_path / ".stacksense" / "dependency_graph.json"
        
        if diagram_path.exists():
            diagram_file = diagram_path
        elif project_diagram.exists():
            diagram_file = project_diagram
        else:
            diagram_file = None
        
        if diagram_file:
            try:
                with open(diagram_file) as f:
                    data = json.load(f)
                    nodes = [n.get('id', '') for n in data.get('nodes', [])][:50]
                    return f"Codebase files:\n" + "\n".join(f"- {n}" for n in nodes)
            except:
                pass
        
        # Build simple file tree
        files = []
        for item in self.workspace_path.rglob('*'):
            if item.is_file():
                rel_path = str(item.relative_to(self.workspace_path))
                
                skip = False
                for pattern in self.gitignore_patterns:
                    if pattern in rel_path:
                        skip = True
                        break
                
                if not skip and not rel_path.startswith('.'):
                    files.append(rel_path)
        
        files = files[:50]
        return "Files in workspace:\n" + "\n".join(f"- {f}" for f in files)
    
    def _tool_update_diagram(self, action: str, node_path: str, node_type: str = "file", description: str = "") -> str:
        """
        Update the codebase diagram incrementally.
        
        Actions:
        - add: Add a new node (file/folder created)
        - remove: Remove a node (file/folder deleted)
        - update: Update node metadata
        
        Args:
            action: "add", "remove", or "update"
            node_path: Path to the file/folder (relative to workspace)
            node_type: "file" or "directory"
            description: Optional description of the change
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        # Use centralized storage path
        diagram_dir = self._get_storage_path("scan", "diagrams")
        diagram_path = diagram_dir / "dependency_graph.json"
        
        try:
            from datetime import datetime
            
            # Load existing or create new
            if diagram_path.exists():
                with open(diagram_path) as f:
                    data = json.load(f)
            else:
                data = {
                    'nodes': [],
                    'edges': [],
                    'metadata': {
                        'created': datetime.now().isoformat(),
                        'workspace': str(self.workspace_path)
                    }
                }
            
            nodes = data.get('nodes', [])
            
            if action == "add":
                # Check if already exists
                existing = [n for n in nodes if n.get('id') == node_path]
                if existing:
                    return f"Node '{node_path}' already exists in diagram."
                
                new_node = {
                    'id': node_path,
                    'type': node_type,
                    'label': node_path.split('/')[-1],
                    'added_at': datetime.now().isoformat()
                }
                if description:
                    new_node['description'] = description
                
                nodes.append(new_node)
                data['nodes'] = nodes
                data['metadata']['updated'] = datetime.now().isoformat()
                
                with open(diagram_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return f"✅ Added '{node_path}' to diagram ({len(nodes)} total nodes)"
            
            elif action == "remove":
                original_count = len(nodes)
                nodes = [n for n in nodes if n.get('id') != node_path]
                
                if len(nodes) == original_count:
                    return f"Node '{node_path}' not found in diagram."
                
                # Also remove related edges
                edges = data.get('edges', [])
                edges = [e for e in edges if e.get('source') != node_path and e.get('target') != node_path]
                
                data['nodes'] = nodes
                data['edges'] = edges
                data['metadata']['updated'] = datetime.now().isoformat()
                
                with open(diagram_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return f"✅ Removed '{node_path}' from diagram ({len(nodes)} remaining)"
            
            elif action == "update":
                updated = False
                for node in nodes:
                    if node.get('id') == node_path:
                        node['updated_at'] = datetime.now().isoformat()
                        if description:
                            node['description'] = description
                        updated = True
                        break
                
                if not updated:
                    return f"Node '{node_path}' not found. Use action='add' first."
                
                data['nodes'] = nodes
                data['metadata']['updated'] = datetime.now().isoformat()
                
                with open(diagram_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return f"✅ Updated '{node_path}' in diagram"
            
            else:
                return f"Unknown action '{action}'. Use 'add', 'remove', or 'update'."
        
        except Exception as e:
            return f"Error updating diagram: {e}"

    
    def _tool_read_file(self, filepath: str, context: str = "", format: str = "summary") -> str:
        """
        Read a file's contents with smart slicing.
        
        Args:
            filepath: Path to file relative to workspace
            context: Optional context hint (unused but kept for compatibility)
            format: Output format - summary, full, first:N, last:N, structure
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        file_path = self.workspace_path / filepath
        
        if not file_path.exists():
            return f"File not found: {filepath}"
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Use smart slicing
            sliced = self._smart_slice(content, format=format, max_lines=100)
            result = f"Contents of {filepath}:\n```\n{sliced['content']}\n```"
            
            if sliced.get("truncated"):
                result += f"\n\n*{sliced.get('hint', 'Output truncated')}*"
            
            return result
        except Exception as e:
            return f"Error reading file: {e}"
    
    def _tool_search_code(self, keywords: str) -> str:
        """Search codebase for keywords"""
        if not self.workspace_path:
            return "No workspace loaded."
        
        keyword_list = [k.strip() for k in keywords.split(',')]
        results = {}
        
        for item in self.workspace_path.rglob('*'):
            if not item.is_file():
                continue
            
            rel_path = str(item.relative_to(self.workspace_path))
            
            skip = False
            for pattern in self.gitignore_patterns:
                if pattern in rel_path:
                    skip = True
                    break
            
            if skip:
                continue
            
            if item.suffix not in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.md']:
                continue
            
            try:
                content = item.read_text(encoding='utf-8', errors='ignore').lower()
                matches = sum(1 for k in keyword_list if k.lower() in content)
                if matches > 0:
                    results[rel_path] = matches
            except:
                continue
        
        if not results:
            return f"No files found matching: {keywords}"
        
        sorted_files = sorted(results.items(), key=lambda x: -x[1])[:10]
        
        return "Files matching keywords:\n" + "\n".join(
            f"- {f} ({c} matches)" for f, c in sorted_files
        )
    
    def _tool_recall_memory(self) -> str:
        """Recall previous learnings from centralized storage"""
        if not self.workspace_path:
            return "No workspace - no memory available."
        
        # Use centralized storage path
        memory_path = self._get_storage_path("scan") / "ai_memory.json"
        
        if not memory_path.exists():
            return "No previous memories found. This is a fresh session."
        
        try:
            with open(memory_path) as f:
                data = json.load(f)
            
            learnings = data.get('learnings', [])
            if not learnings:
                return "No learnings saved yet."
            
            recent = learnings[-5:]
            return "Previous learnings:\n" + "\n".join(
                f"- [{l['topic']}] {l['summary']}" for l in recent
            )
        except:
            return "Error reading memory."
    
    def _tool_save_learning(self, topic: str, summary: str) -> str:
        """
        Save a learning for future reference.
        If a topic already exists, it UPDATES (replaces) the existing entry.
        Saves to ~/.stacksense/{workspace}/{repo}/scan/ai_memory.json
        """
        if not self.workspace_path:
            return "No workspace - cannot save."
        
        # Use centralized storage path
        memory_path = self._get_storage_path("scan") / "ai_memory.json"
        
        try:
            if memory_path.exists():
                with open(memory_path) as f:
                    data = json.load(f)
            else:
                data = {'learnings': []}
            
            from datetime import datetime
            
            # Check if topic already exists - REPLACE if so
            existing_idx = None
            for i, learning in enumerate(data['learnings']):
                if learning.get('topic', '').lower() == topic.lower():
                    existing_idx = i
                    break
            
            new_entry = {
                'topic': topic,
                'summary': summary,
                'timestamp': datetime.now().isoformat()
            }
            
            if existing_idx is not None:
                # Update existing entry
                old_summary = data['learnings'][existing_idx].get('summary', '')[:50]
                data['learnings'][existing_idx] = new_entry
                action = f"Updated (was: {old_summary}...)"
            else:
                # Add new entry
                data['learnings'].append(new_entry)
                action = "Saved new"
            
            # Keep last 30
            data['learnings'] = data['learnings'][-30:]
            
            with open(memory_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return f"✅ {action}: [{topic}] {summary[:100]}"
        except Exception as e:
            return f"Error saving: {e}"
    
    def _tool_save_search_learning(self, topic: str, insight: str, source: str = "") -> str:
        """
        Save an important learning from web search to important.json.
        These help guide future searches and avoid repeating research.
        
        Examples:
        - Topic: "FastAPI Celery integration"
        - Insight: "Use celery[redis] package, configure broker in lifespan"
        - Source: "stackoverflow.com/..."
        """
        if not self.workspace_path:
            return "No workspace."
        
        # Use centralized storage path
        important_path = self._get_storage_path("search") / "important.json"
        
        try:
            from datetime import datetime
            
            if important_path.exists():
                with open(important_path) as f:
                    data = json.load(f)
            else:
                data = {'insights': []}
            
            insights = data.get('insights', [])
            
            # Check if topic exists - UPDATE if so
            existing_idx = None
            for i, item in enumerate(insights):
                if item.get('topic', '').lower() == topic.lower():
                    existing_idx = i
                    break
            
            new_entry = {
                'topic': topic,
                'insight': insight,
                'source': source,
                'timestamp': datetime.now().isoformat()
            }
            
            if existing_idx is not None:
                # Update existing
                old_insight = insights[existing_idx].get('insight', '')[:30]
                insights[existing_idx] = new_entry
                action = f"Updated (was: {old_insight}...)"
            else:
                insights.append(new_entry)
                action = "Saved new"
            
            # Keep last 50 insights
            data['insights'] = insights[-50:]
            data['updated_at'] = datetime.now().isoformat()
            
            with open(important_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return f"✅ {action} insight: [{topic}] {insight[:80]}"
        except Exception as e:
            return f"Error saving search learning: {e}"
    
    def _tool_recall_search_learnings(self, query: str = "") -> str:
        """
        Recall important insights from previous web searches.
        Helps avoid repeating research on solved problems.
        
        Args:
            query: Optional filter to find relevant insights
        """
        if not self.workspace_path:
            return "No workspace."
        
        # Use centralized storage path
        important_path = self._get_storage_path("search") / "important.json"
        
        if not important_path.exists():
            return "No search learnings yet. Use save_search_learning after web searches to build knowledge."
        
        try:
            with open(important_path) as f:
                data = json.load(f)
            
            insights = data.get('insights', [])
            
            if not insights:
                return "No insights saved yet."
            
            # Filter if query provided
            if query:
                query_lower = query.lower()
                filtered = [i for i in insights if 
                    query_lower in i.get('topic', '').lower() or 
                    query_lower in i.get('insight', '').lower()]
                if filtered:
                    insights = filtered
            
            lines = ["📚 **Search Learnings:**"]
            for item in insights[-10:]:  # Last 10
                topic = item.get('topic', 'Unknown')
                insight = item.get('insight', '')[:100]
                lines.append(f"\n**{topic}:**")
                lines.append(f"  {insight}")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error reading search learnings: {e}"
    
    def _tool_group_files(self, group_name: str, files: list, description: str = "") -> str:
        """
        Group related files together in group.json for better project understanding.
        Use this when you discover files that work together for a feature/functionality.
        
        Args:
            group_name: Name for this group (e.g., "authentication_files", "api_routes")
            files: List of file paths that belong together
            description: What this group does/represents
            
        Examples:
            - group_name="auth_flow", files=["auth.py", "jwt.py", "login.py"], description="User authentication"
            - group_name="api_routes", files=["routes/api.js", "routes/health.js"], description="API endpoints"
        """
        if not self.workspace_path:
            return "No workspace - cannot group files."
        
        if not files or not isinstance(files, list):
            return "Error: files must be a non-empty list of file paths."
        
        # Use centralized storage path
        group_path = self._get_storage_path("scan") / "group.json"
        
        try:
            from datetime import datetime
            
            if group_path.exists():
                with open(group_path) as f:
                    data = json.load(f)
            else:
                data = {
                    'groups': {},
                    'characteristics_detected': [],
                    'last_updated': None
                }
            
            # Check if group exists - update or create
            existing = group_name in data.get('groups', {})
            
            data['groups'][group_name] = {
                'files': files,
                'description': description,
                'file_count': len(files),
                'created_at': data['groups'].get(group_name, {}).get('created_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat()
            }
            data['last_updated'] = datetime.now().isoformat()
            
            with open(group_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            action = "Updated" if existing else "Created"
            return f"✅ {action} group '{group_name}' with {len(files)} files"
        except Exception as e:
            return f"Error grouping files: {e}"
    
    def _tool_list_groups(self) -> str:
        """
        List all file groups from group.json.
        Returns group names, file counts, and descriptions.
        """
        if not self.workspace_path:
            return "No workspace."
        
        # Use centralized storage path
        group_path = self._get_storage_path("scan") / "group.json"
        
        if not group_path.exists():
            return "No groups defined yet. Use group_files() to create groups."
        
        try:
            with open(group_path) as f:
                data = json.load(f)
            
            groups = data.get('groups', {})
            if not groups:
                return "No groups defined yet."
            
            lines = ["📁 **File Groups:**"]
            for name, info in groups.items():
                files = info.get('files', [])
                desc = info.get('description', '')
                lines.append(f"\n**{name}** ({len(files)} files)")
                if desc:
                    lines.append(f"  {desc}")
                for f in files[:5]:  # Show first 5
                    lines.append(f"  - {f}")
                if len(files) > 5:
                    lines.append(f"  ... and {len(files) - 5} more")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error reading groups: {e}"

    
    # =========================================
    # GIT INTEGRATION TOOLS
    # =========================================
    
    def _tool_git_status(self) -> str:
        """
        Show git status - changed, staged, and untracked files.
        FREE tool (0 credits) - essential for context.
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        try:
            import subprocess
            
            # Run git status --porcelain for machine-readable output
            result = subprocess.run(
                ['git', 'status', '--porcelain', '-b'],
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return f"Git error: {result.stderr.strip()}"
            
            output = result.stdout.strip()
            if not output:
                return "✅ Working tree clean - no changes."
            
            # Parse the output for better formatting
            lines = output.split('\n')
            branch_line = lines[0] if lines[0].startswith('##') else None
            file_lines = lines[1:] if branch_line else lines
            
            # Categorize changes
            staged = []
            modified = []
            untracked = []
            
            for line in file_lines:
                if not line or len(line) < 3:
                    continue
                status = line[:2]
                filepath = line[3:]
                
                if status[0] in 'MADRC':  # Staged
                    staged.append(f"  {status[0]} {filepath}")
                if status[1] in 'MADRC':  # Modified (not staged)
                    modified.append(f"  {status[1]} {filepath}")
                if status == '??':  # Untracked
                    untracked.append(f"  ? {filepath}")
            
            # Format output
            parts = []
            if branch_line:
                branch = branch_line.replace('## ', '').split('...')[0]
                parts.append(f"📌 **Branch:** {branch}")
            
            if staged:
                parts.append(f"\n✅ **Staged ({len(staged)}):**")
                parts.extend(staged[:10])
                if len(staged) > 10:
                    parts.append(f"  ... and {len(staged) - 10} more")
            
            if modified:
                parts.append(f"\n📝 **Modified ({len(modified)}):**")
                parts.extend(modified[:10])
                if len(modified) > 10:
                    parts.append(f"  ... and {len(modified) - 10} more")
            
            if untracked:
                parts.append(f"\n❓ **Untracked ({len(untracked)}):**")
                parts.extend(untracked[:5])
                if len(untracked) > 5:
                    parts.append(f"  ... and {len(untracked) - 5} more")
            
            return "\n".join(parts)
            
        except subprocess.TimeoutExpired:
            return "Git command timed out."
        except FileNotFoundError:
            return "Git not found. Is git installed?"
        except Exception as e:
            return f"Error running git status: {e}"
    
    def _tool_git_diff(self, file_path: str = "", staged: bool = False, format: str = "summary") -> str:
        """
        Show git diff for a file or all changes.
        
        Args:
            file_path: Optional file path to diff (empty = all files)
            staged: If True, show staged changes (--cached)
            format: Output format - "summary" (default), "full", "first:N", "last:N"
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        try:
            import subprocess
            
            # Build command
            cmd = ['git', 'diff', '--stat']
            if staged:
                cmd.append('--cached')
            if file_path:
                cmd.append(file_path)
            
            # Get stat first
            stat_result = subprocess.run(
                cmd,
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Get actual diff
            diff_cmd = ['git', 'diff']
            if staged:
                diff_cmd.append('--cached')
            if file_path:
                diff_cmd.append(file_path)
            
            diff_result = subprocess.run(
                diff_cmd,
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if diff_result.returncode != 0:
                return f"Git error: {diff_result.stderr.strip()}"
            
            diff_output = diff_result.stdout.strip()
            if not diff_output:
                scope = f"'{file_path}'" if file_path else "files"
                staged_msg = " (staged)" if staged else ""
                return f"No changes{staged_msg} in {scope}."
            
            # Use smart slicing
            sliced = self._smart_slice(diff_output, format=format, max_lines=60)
            diff_output = sliced["content"]
            
            # Add stat summary
            stat_output = stat_result.stdout.strip()
            result_parts = []
            
            if stat_output:
                result_parts.append(f"**Summary:**\n```\n{stat_output}\n```")
            
            result_parts.append(f"**Diff:**\n```diff\n{diff_output}\n```")
            
            if sliced.get("truncated"):
                result_parts.append(f"\n*{sliced.get('hint', 'Output truncated')}*")
            
            return "\n\n".join(result_parts)
            
        except subprocess.TimeoutExpired:
            return "Git diff timed out."
        except FileNotFoundError:
            return "Git not found."
        except Exception as e:
            return f"Error running git diff: {e}"

    
    # =========================================
    # FILE OPERATION TOOLS
    # =========================================
    
    def _tool_find_file(self, pattern: str, max_results: int = 20) -> str:
        """
        Find files by name pattern (glob-style).
        Different from search_code - this finds by filename, not content.
        
        Args:
            pattern: Glob pattern (e.g., "*.py", "auth*", "test_*.js")
            max_results: Maximum results to return (default 20)
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        try:
            import subprocess
            
            # Use find command with pattern
            cmd = ['find', '.', '-type', 'f', '-name', pattern, '-not', '-path', '*/.*', '-not', '-path', '*/node_modules/*', '-not', '-path', '*/venv/*', '-not', '-path', '*/__pycache__/*']
            
            result = subprocess.run(
                cmd,
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode != 0 and not result.stdout:
                return f"Find error: {result.stderr.strip()}"
            
            files = [f.lstrip('./') for f in result.stdout.strip().split('\n') if f]
            
            if not files:
                return f"No files matching '{pattern}' found."
            
            total = len(files)
            files = files[:max_results]
            
            lines = [f"🔍 **Found {total} files matching '{pattern}':**"]
            for f in files:
                lines.append(f"  - {f}")
            
            if total > max_results:
                lines.append(f"  ... and {total - max_results} more")
            
            return "\n".join(lines)
            
        except subprocess.TimeoutExpired:
            return "Find command timed out."
        except Exception as e:
            return f"Error finding files: {e}"
    
    def _tool_compare_files(self, file1: str, file2: str) -> str:
        """
        Compare two files and show differences.
        
        Args:
            file1: First file path (relative to workspace)
            file2: Second file path (relative to workspace)
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        path1 = self.workspace_path / file1
        path2 = self.workspace_path / file2
        
        if not path1.exists():
            return f"File not found: {file1}"
        if not path2.exists():
            return f"File not found: {file2}"
        
        try:
            import subprocess
            
            result = subprocess.run(
                ['diff', '-u', str(path1), str(path2)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # diff returns 0 if same, 1 if different, 2 if error
            if result.returncode == 0:
                return f"✅ Files are identical: {file1} and {file2}"
            
            if result.returncode == 2:
                return f"Diff error: {result.stderr.strip()}"
            
            diff_output = result.stdout.strip()
            
            # Truncate if too long
            if len(diff_output) > 3000:
                diff_output = diff_output[:3000] + f"\n\n... (truncated, {len(result.stdout)} chars total)"
            
            return f"**Comparing:** `{file1}` vs `{file2}`\n\n```diff\n{diff_output}\n```"
            
        except subprocess.TimeoutExpired:
            return "Diff command timed out."
        except Exception as e:
            return f"Error comparing files: {e}"
    
    def _tool_summarize_file(self, file_path: str) -> str:
        """
        Generate a one-line summary of what a file does.
        Analyzes first few lines, imports, and structure.
        
        Args:
            file_path: Path to file (relative to workspace)
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        full_path = self.workspace_path / file_path
        
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        try:
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Get file extension
            ext = full_path.suffix.lower()
            
            # Extract summary based on file type
            summary_parts = []
            
            # Check for docstring/comment at top
            if ext in ['.py']:
                # Python - look for module docstring
                if content.startswith('"""') or content.startswith("'''"):
                    end = content.find('"""', 3) or content.find("'''", 3)
                    if end > 0:
                        docstring = content[3:end].strip().split('\n')[0]
                        if docstring:
                            summary_parts.append(docstring[:100])
                
                # Count classes and functions
                classes = len([l for l in lines if l.strip().startswith('class ')])
                funcs = len([l for l in lines if l.strip().startswith('def ')])
                if classes or funcs:
                    summary_parts.append(f"{classes} class(es), {funcs} function(s)")
                    
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                # JavaScript/TypeScript
                exports = len([l for l in lines if 'export ' in l])
                imports = len([l for l in lines if 'import ' in l])
                summary_parts.append(f"{imports} imports, {exports} exports")
                
            elif ext in ['.md']:
                # Markdown - first heading
                for line in lines[:10]:
                    if line.startswith('# '):
                        summary_parts.append(line[2:].strip())
                        break
                        
            elif ext in ['.json']:
                # JSON - key count
                import json
                data = json.loads(content)
                if isinstance(data, dict):
                    summary_parts.append(f"Object with {len(data)} keys")
                elif isinstance(data, list):
                    summary_parts.append(f"Array with {len(data)} items")
                    
            elif ext in ['.html', '.htm']:
                if '<title>' in content:
                    start = content.find('<title>') + 7
                    end = content.find('</title>')
                    if end > start:
                        summary_parts.append(content[start:end].strip()[:50])
            
            # Add line count
            line_count = len(lines)
            size = full_path.stat().st_size
            
            if summary_parts:
                summary = " | ".join(summary_parts)
            else:
                # Generic summary
                summary = f"{ext} file"
            
            return f"📄 **{file_path}**: {summary} ({line_count} lines, {size:,} bytes)"
            
        except Exception as e:
            return f"Error summarizing file: {e}"

    
    # =========================================
    # ERROR ANALYSIS TOOLS
    # =========================================
    
    def _tool_explain_error(self, error_message: str) -> str:
        """
        Parse and explain an error message with context and suggestions.
        
        Args:
            error_message: The error text to analyze
        """
        if not error_message:
            return "No error message provided."
        
        # Common error patterns and explanations
        patterns = {
            "ModuleNotFoundError": {
                "cause": "Python can't find the module/package",
                "fix": "Install with: pip install <package_name>"
            },
            "ImportError": {
                "cause": "Module exists but specific import failed",
                "fix": "Check spelling, or the module may not export that name"
            },
            "SyntaxError": {
                "cause": "Invalid Python syntax",
                "fix": "Check for missing colons, brackets, or quotes"
            },
            "IndentationError": {
                "cause": "Inconsistent indentation",
                "fix": "Use consistent spaces (4 spaces recommended)"
            },
            "TypeError": {
                "cause": "Wrong type passed to function/operation",
                "fix": "Check function signature and argument types"
            },
            "AttributeError": {
                "cause": "Object doesn't have that attribute/method",
                "fix": "Check object type or if attribute exists"
            },
            "KeyError": {
                "cause": "Dictionary key doesn't exist",
                "fix": "Use .get() method or check if key exists first"
            },
            "FileNotFoundError": {
                "cause": "File or directory doesn't exist",
                "fix": "Check path spelling or if file was created"
            },
            "PermissionError": {
                "cause": "No permission to access file/resource",
                "fix": "Check file permissions or run with appropriate access"
            },
            "ConnectionError": {
                "cause": "Network connection failed",
                "fix": "Check internet connection or server availability"
            },
            "TimeoutError": {
                "cause": "Operation took too long",
                "fix": "Increase timeout or check for slow operations"
            },
            "npm ERR!": {
                "cause": "npm package manager error",
                "fix": "Try: npm cache clean --force && npm install"
            },
            "ENOENT": {
                "cause": "File/directory not found (Node.js)",
                "fix": "Check if path exists"
            },
            "EACCES": {
                "cause": "Permission denied (Node.js)",
                "fix": "Check permissions or avoid using sudo with npm"
            }
        }
        
        result = ["🔍 **Error Analysis:**\n"]
        result.append(f"```\n{error_message[:500]}\n```\n")
        
        # Find matching patterns
        matched = False
        for pattern, info in patterns.items():
            if pattern in error_message:
                result.append(f"\n**Error Type:** `{pattern}`")
                result.append(f"**Likely Cause:** {info['cause']}")
                result.append(f"**Suggested Fix:** {info['fix']}")
                matched = True
                break
        
        if not matched:
            result.append("\n**Analysis:** Unknown error pattern")
            result.append("**Suggestion:** Search the error message online or check logs for more context")
        
        # Extract file/line info if present
        import re
        file_match = re.search(r'File ["\']([^"\']+)["\'], line (\d+)', error_message)
        if file_match:
            result.append(f"\n**Location:** `{file_match.group(1)}` line {file_match.group(2)}")
        
        return "\n".join(result)
    
    def _tool_analyze_stack_trace(self, stack_trace: str) -> str:
        """
        Parse a stack trace and extract key information.
        
        Args:
            stack_trace: The full stack trace text
        """
        if not stack_trace:
            return "No stack trace provided."
        
        import re
        
        result = ["📊 **Stack Trace Analysis:**\n"]
        
        # Python stack trace pattern
        py_pattern = r'File ["\']([^"\']+)["\'], line (\d+), in (\w+)'
        py_matches = re.findall(py_pattern, stack_trace)
        
        # Node.js stack trace pattern
        node_pattern = r'at (\w+) \(([^:]+):(\d+):(\d+)\)'
        node_matches = re.findall(node_pattern, stack_trace)
        
        if py_matches:
            result.append("**Stack (Python):**")
            for file, line, func in py_matches[-5:]:  # Last 5 frames
                short_file = file.split('/')[-1]
                result.append(f"  → `{short_file}:{line}` in `{func}()`")
        
        elif node_matches:
            result.append("**Stack (Node.js):**")
            for func, file, line, col in node_matches[:5]:  # First 5 frames
                short_file = file.split('/')[-1]
                result.append(f"  → `{short_file}:{line}` in `{func}()`")
        
        else:
            result.append("Could not parse stack trace format.")
            sliced = self._smart_slice(stack_trace, "last:15", max_lines=20)
            result.append(f"\n**Raw output (last 15 lines):**\n```\n{sliced['content']}\n```")
        
        # Find the actual error message (usually last line)
        lines = stack_trace.strip().split('\n')
        for line in reversed(lines):
            if 'Error' in line or 'Exception' in line:
                result.append(f"\n**Error:** `{line.strip()[:100]}`")
                break
        
        return "\n".join(result)

    
    # =========================================
    # DEPENDENCY ANALYSIS TOOLS
    # =========================================
    
    def _tool_get_dependencies(self) -> str:
        """
        Get project dependencies from package.json, requirements.txt, etc.
        Parses and returns installed packages and their versions.
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        results = []
        
        # Check for Python (requirements.txt, pyproject.toml)
        req_path = self.workspace_path / "requirements.txt"
        if req_path.exists():
            try:
                content = req_path.read_text()
                deps = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
                results.append(f"📦 **Python (requirements.txt):** {len(deps)} packages")
                for dep in deps[:15]:
                    results.append(f"  - {dep}")
                if len(deps) > 15:
                    results.append(f"  ... and {len(deps) - 15} more")
            except Exception as e:
                results.append(f"Error reading requirements.txt: {e}")
        
        # Check for pyproject.toml
        pyproject_path = self.workspace_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text()
                if 'dependencies' in content or 'requires' in content:
                    results.append(f"📦 **pyproject.toml:** Found (parse manually with read_file)")
            except:
                pass
        
        # Check for Node.js (package.json)
        pkg_path = self.workspace_path / "package.json"
        if pkg_path.exists():
            try:
                import json
                data = json.loads(pkg_path.read_text())
                
                deps = data.get('dependencies', {})
                dev_deps = data.get('devDependencies', {})
                
                if deps:
                    results.append(f"\n📦 **Node.js (dependencies):** {len(deps)} packages")
                    for name, version in list(deps.items())[:10]:
                        results.append(f"  - {name}: {version}")
                    if len(deps) > 10:
                        results.append(f"  ... and {len(deps) - 10} more")
                
                if dev_deps:
                    results.append(f"\n🔧 **devDependencies:** {len(dev_deps)} packages")
                    for name, version in list(dev_deps.items())[:5]:
                        results.append(f"  - {name}: {version}")
                    if len(dev_deps) > 5:
                        results.append(f"  ... and {len(dev_deps) - 5} more")
            except Exception as e:
                results.append(f"Error reading package.json: {e}")
        
        # Check for Go (go.mod)
        go_mod = self.workspace_path / "go.mod"
        if go_mod.exists():
            results.append(f"📦 **Go (go.mod):** Found")
        
        # Check for Rust (Cargo.toml)
        cargo_toml = self.workspace_path / "Cargo.toml"
        if cargo_toml.exists():
            results.append(f"📦 **Rust (Cargo.toml):** Found")
        
        if not results:
            return "No dependency files found (requirements.txt, package.json, go.mod, Cargo.toml)."
        
        return "\n".join(results)
    
    def _tool_dependency_tree(self, package: str = "") -> str:
        """
        Show dependency tree - why a package is installed.
        
        Args:
            package: Optional package name to show tree for
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        try:
            import subprocess
            
            # Detect package manager
            has_npm = (self.workspace_path / "package-lock.json").exists() or (self.workspace_path / "node_modules").exists()
            has_pip = (self.workspace_path / "requirements.txt").exists() or (self.workspace_path / "venv").exists()
            
            if has_npm and package:
                # npm ls for specific package
                result = subprocess.run(
                    ['npm', 'ls', package, '--depth=2'],
                    cwd=str(self.workspace_path),
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                output = result.stdout.strip() or result.stderr.strip()
                if output:
                    return f"📦 **npm dependency tree for '{package}':**\n```\n{output[:2000]}\n```"
                return f"Package '{package}' not found in node_modules."
            
            elif has_npm:
                # npm ls overview
                result = subprocess.run(
                    ['npm', 'ls', '--depth=0'],
                    cwd=str(self.workspace_path),
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                output = result.stdout.strip()[:1500] if result.stdout else "No npm packages installed."
                return f"📦 **npm packages (depth 0):**\n```\n{output}\n```"
            
            elif has_pip and package:
                # pip show for specific package
                result = subprocess.run(
                    ['pip', 'show', package],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return f"📦 **pip info for '{package}':**\n```\n{result.stdout.strip()}\n```"
                return f"Package '{package}' not found."
            
            elif has_pip:
                # pip list
                result = subprocess.run(
                    ['pip', 'list', '--format=columns'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                output = result.stdout.strip()[:1500] if result.stdout else "No pip packages."
                return f"📦 **pip packages:**\n```\n{output}\n```"
            
            else:
                return "No package manager detected (npm/pip)."
            
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except FileNotFoundError as e:
            return f"Package manager not found: {e}"
        except Exception as e:
            return f"Error getting dependency tree: {e}"

    
    # =========================================
    # CODE QUALITY TOOLS
    # =========================================
    
    def _tool_estimate_complexity(self, file_path: str) -> str:
        """
        Estimate code complexity of a file.
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        full_path = self.workspace_path / file_path
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        try:
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Basic metrics
            total_lines = len(lines)
            code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            blank_lines = len([l for l in lines if not l.strip()])
            comment_lines = len([l for l in lines if l.strip().startswith('#')])
            
            # Complexity indicators
            classes = len([l for l in lines if l.strip().startswith('class ')])
            functions = len([l for l in lines if 'def ' in l])
            imports = len([l for l in lines if l.strip().startswith(('import ', 'from '))])
            
            # Nesting depth (approximate)
            max_indent = max([len(l) - len(l.lstrip()) for l in lines if l.strip()], default=0) // 4
            
            # Complexity score (simple heuristic)
            score = min(10, (functions / 5) + (classes * 2) + (max_indent / 2))
            
            if score < 3:
                rating = "🟢 Low"
            elif score < 6:
                rating = "🟡 Medium"
            else:
                rating = "🔴 High"
            
            return f"""📊 **Complexity Analysis: {file_path}**

**Lines:** {total_lines} total ({code_lines} code, {blank_lines} blank, {comment_lines} comments)
**Structure:** {classes} classes, {functions} functions, {imports} imports
**Max Nesting:** {max_indent} levels
**Complexity Score:** {score:.1f}/10 ({rating})"""
            
        except Exception as e:
            return f"Error analyzing file: {e}"
    
    def _tool_code_smell_scan(self, file_path: str = "") -> str:
        """
        Quick scan for common code issues.
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        issues = []
        files_checked = 0
        
        # If specific file, just scan that
        if file_path:
            files = [self.workspace_path / file_path]
        else:
            # Scan Python files
            import subprocess
            result = subprocess.run(
                ['find', '.', '-name', '*.py', '-not', '-path', '*/venv/*', '-not', '-path', '*/__pycache__/*'],
                cwd=str(self.workspace_path),
                capture_output=True, text=True, timeout=10
            )
            files = [self.workspace_path / f.strip().lstrip('./') for f in result.stdout.split('\n') if f.strip()][:20]
        
        for fp in files:
            if not fp.exists():
                continue
            
            try:
                content = fp.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                rel_path = str(fp.relative_to(self.workspace_path))
                files_checked += 1
                
                for i, line in enumerate(lines, 1):
                    # Check for common issues
                    if 'print(' in line and 'debug' not in str(fp).lower():
                        issues.append(f"⚠️ `{rel_path}:{i}` - print() statement")
                    if 'TODO' in line or 'FIXME' in line:
                        issues.append(f"📝 `{rel_path}:{i}` - {line.strip()[:50]}")
                    if 'password' in line.lower() and '=' in line:
                        issues.append(f"🔒 `{rel_path}:{i}` - Possible hardcoded password")
                    if len(line) > 120:
                        issues.append(f"📏 `{rel_path}:{i}` - Line too long ({len(line)} chars)")
                        
                # Check function length
                func_lines = 0
                for line in lines:
                    if line.strip().startswith('def '):
                        func_lines = 1
                    elif func_lines > 0:
                        func_lines += 1
                        if func_lines > 50:
                            issues.append(f"📐 `{rel_path}` - Function > 50 lines")
                            break
                            
            except:
                continue
        
        if not issues:
            return f"✅ No code smells found in {files_checked} files scanned."
        
        return f"""🔍 **Code Smell Scan** ({files_checked} files)

Found {len(issues)} issues:

""" + "\n".join(issues[:15]) + (f"\n... and {len(issues) - 15} more" if len(issues) > 15 else "")
    
    def _tool_project_health(self) -> str:
        """
        Overall project health check.
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        health = []
        score = 100
        
        # Check for README
        if (self.workspace_path / "README.md").exists():
            health.append("✅ README.md exists")
        else:
            health.append("❌ Missing README.md")
            score -= 10
        
        # Check for requirements/package.json
        if (self.workspace_path / "requirements.txt").exists():
            health.append("✅ requirements.txt exists")
        elif (self.workspace_path / "package.json").exists():
            health.append("✅ package.json exists")
        else:
            health.append("❌ No dependency file found")
            score -= 15
        
        # Check for .gitignore
        if (self.workspace_path / ".gitignore").exists():
            health.append("✅ .gitignore exists")
        else:
            health.append("⚠️ No .gitignore")
            score -= 5
        
        # Check for tests
        tests_dir = self.workspace_path / "tests"
        if tests_dir.exists() or (self.workspace_path / "test").exists():
            health.append("✅ Tests directory found")
        else:
            health.append("⚠️ No tests directory")
            score -= 10
        
        # Check for docs
        if (self.workspace_path / "docs").exists():
            health.append("✅ Docs directory found")
        else:
            health.append("⚠️ No docs directory")
            score -= 5
        
        # Rate health
        if score >= 90:
            rating = "🟢 Excellent"
        elif score >= 70:
            rating = "🟡 Good"
        elif score >= 50:
            rating = "🟠 Fair"
        else:
            rating = "🔴 Needs Work"
        
        return f"""📋 **Project Health Check**

**Score:** {score}/100 ({rating})

""" + "\n".join(health)
    
    # =========================================
    # CODE INTELLIGENCE TOOLS
    # =========================================
    
    def _tool_suggest_related_files(self, file_path: str) -> str:
        """
        Find files related to the given file via imports/references.
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        full_path = self.workspace_path / file_path
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        try:
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            related = set()
            
            # Python imports
            import re
            py_imports = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
            for imp in py_imports:
                # Convert module.name to module/name.py
                path = imp.replace('.', '/') + '.py'
                if (self.workspace_path / path).exists():
                    related.add(path)
            
            # JS/TS imports
            js_imports = re.findall(r"(?:import|from)\s+['\"]([^'\"]+)['\"]", content)
            for imp in js_imports:
                if imp.startswith('.'):
                    related.add(imp.lstrip('./'))
            
            if not related:
                return f"No local file references found in {file_path}"
            
            return f"""🔗 **Files Related to {file_path}:**

""" + "\n".join([f"  - {f}" for f in sorted(related)[:15]])
            
        except Exception as e:
            return f"Error analyzing file: {e}"
    
    def _tool_create_snippet(self, name: str, code: str, language: str = "python") -> str:
        """
        Save a reusable code snippet.
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        if not name or not code:
            return "Name and code are required."
        
        # Use centralized storage path
        snippets_dir = self._get_storage_path("snippets")
        
        snippet_file = snippets_dir / f"{name}.json"
        
        import json
        from datetime import datetime
        
        snippet_data = {
            "name": name,
            "language": language,
            "code": code,
            "created": datetime.now().isoformat()
        }
        
        with open(snippet_file, 'w') as f:
            json.dump(snippet_data, f, indent=2)
        
        return f"✅ Snippet '{name}' saved ({len(code)} chars, {language})"
    
    # =========================================
    # DEV SERVER TOOLS
    # =========================================
    
    def _tool_hot_reload_status(self) -> str:
        """
        Check if dev server is running and on what port.
        """
        import subprocess
        
        try:
            # Check common dev ports
            common_ports = [3000, 5000, 5173, 8000, 8080, 8888]
            active = []
            
            for port in common_ports:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'],
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 1:
                            active.append(f"Port {port}: {parts[0]}")
            
            if not active:
                return "❌ No dev servers detected on common ports (3000, 5000, 5173, 8000, 8080)"
            
            return f"""🖥️ **Dev Server Status:**

""" + "\n".join([f"✅ {a}" for a in active])
            
        except Exception as e:
            return f"Error checking ports: {e}"
    
    def _tool_run_tests(self, test_path: str = "") -> str:
        """
        Execute test suite and return results.
        """
        if not self.workspace_path:
            return "No workspace loaded."
        
        try:
            import subprocess
            
            # Detect test runner
            if (self.workspace_path / "package.json").exists():
                cmd = ['npm', 'test']
            elif (self.workspace_path / "pytest.ini").exists() or (self.workspace_path / "tests").exists():
                cmd = ['python', '-m', 'pytest', '-v', '--tb=short']
                if test_path:
                    cmd.append(test_path)
            else:
                return "No test runner detected (npm test or pytest)"
            
            result = subprocess.run(
                cmd,
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            sliced = self._smart_slice(output, "last:30", max_lines=40)
            
            if result.returncode == 0:
                return f"✅ **Tests Passed**\n\n```\n{sliced['content']}\n```"
            else:
                return f"❌ **Tests Failed**\n\n```\n{sliced['content']}\n```"
            
        except subprocess.TimeoutExpired:
            return "⏱️ Tests timed out (60s limit)"
        except Exception as e:
            return f"Error running tests: {e}"
    
    # =========================================
    # EXTERNAL TOOLS
    # =========================================
    
    def _tool_read_url(self, url: str, format: str = "auto") -> str:
        """
        Fetch content from a URL with hybrid strategy and fallback chain.
        
        Strategies (tried in order if one fails):
        - 'jina': Jina Reader for clean markdown (best for SPAs, hard sites)
        - 'clean': Readability for article extraction
        - 'raw': Direct HTML with text extraction
        - 'auto': Smart detection with fallback chain
        """
        from urllib.parse import urlparse
        import re
        
        # Security: Block internal/dangerous URLs
        blocked_patterns = [
            'localhost', '127.0.0.1', '0.0.0.0',
            '169.254.169.254', 'metadata.google.internal',
            '.local', '.internal'
        ]
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if parsed.scheme != 'https':
            return "❌ Only HTTPS URLs are allowed for security."
        
        for pattern in blocked_patterns:
            if pattern in domain:
                return f"❌ Domain blocked for security: {domain}"
        
        # Determine strategy order (fallback chain)
        jina_domains = [
            'twitter.com', 'x.com', 'medium.com', 'substack.com',
            'notion.so', 'figma.com', 'miro.com', 'linear.app',
            'vercel.com', 'netlify.com', 'github.com', 'gitlab.com'
        ]
        article_patterns = ['/blog/', '/article/', '/post/', '/news/', '-guide', '/docs/']
        
        if format == "auto":
            # Determine strategy order based on URL
            if any(d in domain for d in jina_domains):
                strategies = ["jina", "readability", "raw"]
            elif any(p in url.lower() for p in article_patterns):
                strategies = ["readability", "jina", "raw"]
            else:
                strategies = ["raw", "readability", "jina"]
        else:
            strategies = [format]  # User explicitly requested a strategy
        
        import httpx
        last_error = None
        
        for strategy in strategies:
            try:
                result = self._fetch_with_strategy(url, strategy)
                if result and not result.startswith("❌"):
                    return result
            except Exception as e:
                last_error = str(e)
                continue
        
        return f"❌ All strategies failed. Last error: {last_error}"
    
    def _fetch_with_strategy(self, url: str, strategy: str) -> str:
        """Execute a specific fetch strategy."""
        import httpx
        import re
        
        if strategy == "jina":
            # Jina Reader (FREE - 1000 req/month)
            jina_url = f"https://r.jina.ai/{url}"
            with httpx.Client(timeout=20.0) as client:
                response = client.get(jina_url, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; StackSense/1.0)'
                })
                
                if response.status_code == 200 and len(response.text) > 200:
                    sliced = self._smart_slice(response.text, format="summary", max_lines=80)
                    return f"""🌐 **Fetched via Jina Reader: {url}**
Strategy: Clean Markdown (handles SPAs)

{sliced['content']}""" + (f"\n\n*{sliced.get('hint', '')}*" if sliced.get('truncated') else "")
                else:
                    raise Exception("Jina returned insufficient content")
        
        elif strategy == "readability":
            # Mozilla Readability
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                response = client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; StackSense/1.0)'
                })
                
                from readability import Document
                doc = Document(response.text)
                title = doc.title()
                summary = doc.summary()
                
                # Strip HTML tags
                text = re.sub(r'<[^>]+>', ' ', summary)
                text = re.sub(r'\s+', ' ', text).strip()
                
                if len(text) < 100:
                    raise Exception("Readability extracted insufficient content")
                
                sliced = self._smart_slice(text, format="summary", max_lines=80)
                return f"""🌐 **Fetched via Readability: {url}**
Strategy: Article Extraction
**Title:** {title}

{sliced['content']}""" + (f"\n\n*{sliced.get('hint', '')}*" if sliced.get('truncated') else "")
        
        elif strategy == "raw":
            # Raw HTML extraction
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                response = client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; StackSense/1.0; AI Code Assistant)'
                })
                
                content_type = response.headers.get('content-type', '')
                
                # Handle JSON
                if 'application/json' in content_type:
                    sliced = self._smart_slice(response.text, format="summary", max_lines=100)
                    return f"""🌐 **Fetched: {url}**
Status: {response.status_code} | Type: JSON

```json
{sliced['content']}
```""" + (f"\n\n*{sliced.get('hint', '')}*" if sliced.get('truncated') else "")
                
                html = response.text
                
                # Remove script/style
                html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
                html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
                
                # Extract title
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else "No title"
                
                # Extract body text
                body_match = re.search(r'<body[^>]*>(.*?)</body>', html, flags=re.DOTALL | re.IGNORECASE)
                body_html = body_match.group(1) if body_match else html
                
                text = re.sub(r'<[^>]+>', ' ', body_html)
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Format into lines
                words = text.split()
                lines = []
                current = []
                for word in words:
                    current.append(word)
                    if len(' '.join(current)) > 80:
                        lines.append(' '.join(current))
                        current = []
                if current:
                    lines.append(' '.join(current))
                
                content = '\n'.join(lines)
                
                if len(content.strip()) < 100:
                    raise Exception("Raw extraction found minimal content")
                
                sliced = self._smart_slice(content, format="summary", max_lines=80)
                return f"""🌐 **Fetched (raw): {url}**
Status: {response.status_code}
**Title:** {title}

{sliced['content']}""" + (f"\n\n*{sliced.get('hint', '')}*" if sliced.get('truncated') else "")
        
        raise Exception(f"Unknown strategy: {strategy}")

    
    # =========================================
    # TASK MANAGEMENT TOOLS
    # =========================================
    
    def _get_todo_path(self) -> Path:
        """Get path to todo.json in ~/.stacksense/{workspace}/{repo}/todo/"""
        if not self.workspace_path:
            return Path.home() / ".stacksense" / "todo" / "todo.json"
        
        # Use centralized storage path
        return self._get_storage_path("todo") / "todo.json"
    
    def _tool_create_task(self, title: str, description: str = "", priority: str = "medium") -> str:
        """Create a new task in todo.json. Use for breaking down work into 1-3 small chunks."""
        if not self.workspace_path:
            return "No workspace - cannot create task."
        
        todo_path = self._get_todo_path()
        todo_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            from datetime import datetime
            
            if todo_path.exists():
                with open(todo_path) as f:
                    data = json.load(f)
            else:
                data = {
                    'project': self.workspace_path.name,
                    'workspace': self.workspace_path.parent.name,
                    'created_at': datetime.now().isoformat(),
                    'tasks': []
                }
            
            # Generate next task ID
            existing_ids = [t.get('id', 0) for t in data['tasks']]
            next_id = max(existing_ids, default=0) + 1
            
            new_task = {
                'id': next_id,
                'title': title,
                'description': description,
                'status': 'pending',
                'priority': priority,
                'created_at': datetime.now().isoformat(),
                'completed_at': None,
                'notes': None
            }
            
            data['tasks'].append(new_task)
            data['updated_at'] = datetime.now().isoformat()
            
            with open(todo_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            pending = sum(1 for t in data['tasks'] if t['status'] == 'pending')
            return f"✅ Created Task #{next_id}: {title} ({pending} pending)"
        except Exception as e:
            return f"Error creating task: {e}"

    
    def _tool_update_task(self, task_id: int, status: str, notes: str = "") -> str:
        """Update task status (pending/in_progress/done). Auto-clears todo when all done."""
        if not self.workspace_path:
            return "No workspace."
        
        todo_path = self._get_todo_path()
        
        if not todo_path.exists():
            return "No todo.json found. Create tasks first."
        
        try:
            from datetime import datetime
            
            with open(todo_path) as f:
                data = json.load(f)
            
            # Find and update task
            task_found = False
            for task in data['tasks']:
                if task['id'] == task_id:
                    task['status'] = status
                    if notes:
                        task['notes'] = notes
                    if status == 'done':
                        task['completed_at'] = datetime.now().isoformat()
                    elif status == 'in_progress':
                        task['started_at'] = datetime.now().isoformat()
                    task_found = True
                    break
            
            if not task_found:
                return f"Task #{task_id} not found."
            
            data['updated_at'] = datetime.now().isoformat()
            
            # Check if all tasks are done
            all_done = all(t['status'] == 'done' for t in data['tasks'])
            
            if all_done and data['tasks']:
                # Clear tasks but keep project info
                completed_count = len(data['tasks'])
                data['tasks'] = []
                data['cleared_at'] = datetime.now().isoformat()
                data['last_completed_count'] = completed_count
                
                with open(todo_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return f"✅ Task #{task_id} done! 🎉 All {completed_count} tasks complete - todo cleared!"
            
            with open(todo_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            pending = sum(1 for t in data['tasks'] if t['status'] == 'pending')
            done = sum(1 for t in data['tasks'] if t['status'] == 'done')
            
            return f"✅ Task #{task_id} → {status}. Progress: {done}/{len(data['tasks'])} done, {pending} pending"
        except Exception as e:
            return f"Error updating task: {e}"
    
    def _tool_list_tasks(self) -> str:
        """List all current tasks from todo.json"""
        if not self.workspace_path:
            return "No workspace."
        
        todo_path = self._get_todo_path()
        
        if not todo_path.exists():
            return "No tasks yet. Use create_task to add tasks."
        
        try:
            with open(todo_path) as f:
                data = json.load(f)
            
            tasks = data.get('tasks', [])
            
            if not tasks:
                return "📋 No active tasks. All complete!"
            
            lines = ["📋 **Current Tasks:**"]
            
            status_icons = {
                'pending': '⬜',
                'in_progress': '🔄',
                'done': '✅',
                'blocked': '🚫'
            }
            
            for t in tasks:
                icon = status_icons.get(t['status'], '❓')
                priority_mark = "⚡" if t.get('priority') == 'high' else ""
                lines.append(f"{icon} #{t['id']}: {t['title']} {priority_mark}")
                if t.get('notes'):
                    lines.append(f"   📝 {t['notes'][:50]}")
            
            pending = sum(1 for t in tasks if t['status'] == 'pending')
            done = sum(1 for t in tasks if t['status'] == 'done')
            
            lines.append(f"\n**Progress:** {done}/{len(tasks)} complete, {pending} pending")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing tasks: {e}"
    
    def _tool_clear_tasks(self) -> str:
        """Clear all tasks from todo.json (use when all work is complete)"""
        if not self.workspace_path:
            return "No workspace."
        
        todo_path = self._get_todo_path()
        
        if not todo_path.exists():
            return "No todo.json to clear."
        
        try:
            from datetime import datetime
            
            with open(todo_path) as f:
                data = json.load(f)
            
            task_count = len(data.get('tasks', []))
            
            data['tasks'] = []
            data['cleared_at'] = datetime.now().isoformat()
            
            with open(todo_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return f"🧹 Cleared {task_count} tasks. Ready for new work!"
        except Exception as e:
            return f"Error clearing tasks: {e}"

    
    def _tool_web_search(self, query: str) -> str:
        """Search the web with deep content fetching. Results are saved to ~/.stacksense search folder."""
        try:
            from ddgs import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            
            if not results:
                return f"No results found for: {query}"
            
            # Prioritize developer sources
            dev_sources = ['stackoverflow', 'github', 'reddit', 'medium', 'dev.to']
            
            def priority(r):
                url = r.get('href', '').lower()
                for i, source in enumerate(dev_sources):
                    if source in url:
                        return i
                return len(dev_sources)
            
            sorted_results = sorted(results, key=priority)
            top_urls = [r.get('href', '') for r in sorted_results[:2] if r.get('href')]
            
            # Format snippets
            output = f"Search results for '{query}':\n\n"
            for r in sorted_results[:3]:
                output += f"**{r.get('title', 'No title')}**\n"
                output += f"{r.get('body', '')[:200]}...\n"
                output += f"URL: {r.get('href', '')}\n\n"
            
            # Fetch content from top URLs
            deep_content = []
            if top_urls:
                try:
                    import httpx
                    from newspaper import Article
                    
                    output += "\n--- Deep Content ---\n"
                    
                    for url in top_urls[:2]:
                        try:
                            response = httpx.get(url, timeout=10.0, follow_redirects=True)
                            
                            article = Article(url)
                            article.set_html(response.text)
                            article.parse()
                            
                            if article.text:
                                content = article.text[:2000]
                                output += f"\n**From {url}:**\n{content}\n"
                                deep_content.append({'url': url, 'content': content[:500]})
                        except:
                            continue
                except ImportError:
                    pass
            
            # Save search results to centralized storage
            if self.workspace_path:
                try:
                    from datetime import datetime
                    
                    search_dir = self._get_storage_path("search")
                    search_file = search_dir / "search.json"
                    
                    # Load or create search history
                    if search_file.exists():
                        with open(search_file) as f:
                            search_data = json.load(f)
                    else:
                        search_data = {'searches': []}
                    
                    # Add this search
                    search_data['searches'].append({
                        'query': query,
                        'timestamp': datetime.now().isoformat(),
                        'result_count': len(results),
                        'top_results': [
                            {'title': r.get('title', ''), 'url': r.get('href', '')}
                            for r in sorted_results[:3]
                        ],
                        'deep_content': deep_content
                    })
                    
                    # Keep last 50 searches
                    search_data['searches'] = search_data['searches'][-50:]
                    
                    with open(search_file, 'w') as f:
                        json.dump(search_data, f, indent=2)
                except Exception:
                    pass  # Don't fail if storage fails
            
            return output
            
        except Exception as e:
            return f"Search error: {e}"

    
    def _tool_write_file(self, filepath: str, content: str, description: str) -> str:
        """Write content to a file (auto-approved after ask_user confirmation)"""
        if not self.workspace_path:
            return "No workspace - cannot write files."
        
        if not getattr(self, '_permission_granted', False):
            self._pending_permission = {
                'question': f"Create/modify file '{filepath}'?\nDescription: {description}",
                'options': 'yes, no',
                'awaiting': True,
                'pending_action': ('write_file', filepath, content, description)
            }
            return f"__PERMISSION_REQUIRED__\n🔔 May I create/modify '{filepath}'?\n{description}\n[yes] / [no] (or suggest changes)"
        
        file_path = self.workspace_path / filepath
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            self._permission_granted = False
            return f"✅ Successfully wrote to '{filepath}': {description}"
        except Exception as e:
            return f"❌ Failed to write '{filepath}': {e}"
    
    def _tool_run_command(self, command: str, working_directory: str = "", timeout: int = 30) -> str:
        """
        Execute a terminal command with smart output slicing.
        Commands can be stopped using stop_command if they take too long.
        """
        if not getattr(self, '_permission_granted', False):
            self._pending_permission = {
                'question': f"Run command: `{command}`?",
                'options': 'yes, no',
                'awaiting': True,
                'pending_action': ('run_command', command, working_directory)
            }
            return f"__PERMISSION_REQUIRED__\n🔔 May I run this command?\n`{command}`\n[yes] / [no] (or suggest a different command)"
        
        cwd = working_directory or (str(self.workspace_path) if self.workspace_path else None)
        
        try:
            # Use Popen for more control (can be terminated)
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
            
            # Store for potential stopping
            self._running_process = process
            self._running_command = command
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                self._running_process = None
                return f"⏱️ Command timed out after {timeout}s. Partial output:\n{stdout[:500]}"
            
            self._running_process = None
            self._permission_granted = False
            
            # Smart slice the output based on command type and content
            output = self._smart_slice_output(command, stdout, stderr)
            
            return f"Command output (exit {process.returncode}):\n{output or '(no output)'}"
        except Exception as e:
            self._running_process = None
            return f"Command failed: {e}"
    
    def _tool_stop_command(self) -> str:
        """
        Stop the currently running command.
        Use if a command is taking too long or needs to be changed.
        """
        if hasattr(self, '_running_process') and self._running_process:
            try:
                self._running_process.terminate()
                # Give it a moment to terminate gracefully
                try:
                    self._running_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._running_process.kill()
                
                command_name = getattr(self, '_running_command', 'unknown')
                self._running_process = None
                self._running_command = None
                
                return f"⛔ Stopped command: `{command_name}`"
            except Exception as e:
                return f"Error stopping command: {e}"
        else:
            return "No command is currently running."

    
    def _smart_slice_output(self, command: str, stdout: str, stderr: str) -> str:
        """
        Intelligently extract relevant parts of command output.
        Uses heuristics to prioritize errors, warnings, and key results.
        
        The AI can understand what's important based on context.
        """
        cmd_lower = command.lower()
        full_output = stdout or ""
        lines = full_output.split('\n')
        
        # Priority extraction patterns
        result_parts = []
        
        # 1. Always include stderr (errors are critical)
        if stderr and stderr.strip():
            # Extract key error lines, not full trace
            error_lines = stderr.strip().split('\n')
            key_errors = [l for l in error_lines if any(x in l.lower() for x in 
                ['error', 'fail', 'exception', 'traceback', 'cannot', 'denied', 'not found'])]
            if key_errors:
                result_parts.append("ERRORS:\n" + '\n'.join(key_errors[:10]))
            else:
                result_parts.append(f"STDERR: {stderr[:500]}")
        
        # 2. Detect output type and extract accordingly
        if 'npm' in cmd_lower or 'yarn' in cmd_lower or 'pnpm' in cmd_lower:
            # NPM: Focus on added/removed packages, warnings, errors
            key_lines = [l for l in lines if any(x in l.lower() for x in 
                ['added', 'removed', 'packages', 'vulnerabilities', 'warn', 'err', 'up to date'])]
            if key_lines:
                result_parts.append("NPM Summary:\n" + '\n'.join(key_lines[:15]))
            else:
                result_parts.append(full_output[:1000])
        
        elif 'git' in cmd_lower:
            # Git: Focus on branch names, commit info, changes
            if 'status' in cmd_lower:
                result_parts.append(full_output[:1500])  # Status is usually readable
            elif 'log' in cmd_lower:
                # Just first few commits
                result_parts.append('\n'.join(lines[:20]))
            elif 'diff' in cmd_lower:
                # Summary of changes
                change_lines = [l for l in lines if l.startswith('+') or l.startswith('-') or l.startswith('@@')]
                result_parts.append('\n'.join(change_lines[:30]))
            else:
                result_parts.append(full_output[:1000])
        
        elif 'test' in cmd_lower or 'pytest' in cmd_lower or 'jest' in cmd_lower:
            # Tests: Focus on pass/fail summary and failed test names
            summary_lines = [l for l in lines if any(x in l.lower() for x in 
                ['passed', 'failed', 'error', 'skip', 'total', 'test', 'ok', 'fail'])]
            failed_lines = [l for l in lines if 'fail' in l.lower() or 'error' in l.lower()]
            
            if failed_lines:
                result_parts.append("FAILURES:\n" + '\n'.join(failed_lines[:10]))
            if summary_lines:
                result_parts.append("SUMMARY:\n" + '\n'.join(summary_lines[-10:]))
        
        elif 'ls' in cmd_lower or 'find' in cmd_lower or 'tree' in cmd_lower:
            # Directory listings: Just show structure
            result_parts.append('\n'.join(lines[:50]))
        
        elif 'curl' in cmd_lower or 'wget' in cmd_lower or 'http' in cmd_lower:
            # HTTP: Try to extract JSON or key response parts
            import re
            json_match = re.search(r'\{[^{}]*\}', full_output)
            if json_match:
                result_parts.append("Response:\n" + json_match.group()[:1000])
            else:
                result_parts.append(full_output[:1000])
        
        else:
            # Default: First 1000 chars + last 500 chars if output is long
            if len(full_output) > 1500:
                result_parts.append(f"OUTPUT (first 1000 chars):\n{full_output[:1000]}")
                result_parts.append(f"\n...(truncated {len(full_output)-1500} chars)...\n")
                result_parts.append(f"OUTPUT (last 500 chars):\n{full_output[-500:]}")
            else:
                result_parts.append(full_output)
        
        # Combine and limit total size
        combined = '\n'.join(result_parts)
        if len(combined) > 3000:
            combined = combined[:3000] + "\n...(output truncated)..."
        
        return combined

    
    def _tool_ask_user(self, question: str, options: str = "") -> str:
        """Ask user a question - signals permission request to chat loop"""
        self._pending_permission = {
            'question': question,
            'options': options,
            'awaiting': True
        }
        
        if options:
            opt_list = [o.strip() for o in options.split(',')]
            opt_str = " / ".join(f"[{o}]" for o in opt_list)
            return f"__PERMISSION_REQUIRED__\n🔔 {question}\n{opt_str} (or type a custom response)"
        else:
            return f"__PERMISSION_REQUIRED__\n🔔 {question}\n[yes] / [no] (or type a custom response)"
    
    def _execute_tool(self, name: str, args: dict) -> ToolResult:
        """Execute a tool by name. Deducts credits before execution."""
        start_time = time.time()
        
        # Deduct credits before execution
        try:
            from stacksense.credits import use_credits
            from stacksense.providers.tools import TOOL_COSTS
            
            cost = TOOL_COSTS.get(name, 1)
            
            if cost > 0:  # Free tools (cost=0) skip deduction
                allowed, remaining, warning = use_credits(name)
                
                if not allowed:
                    return ToolResult(
                        success=False,
                        result=f"🔒 Insufficient credits ({remaining} remaining). Buy more: stacksense upgrade",
                        error="insufficient_credits",
                        elapsed=0.0
                    )
                
                if self.debug:
                    print(f"[Credits] Used {cost} for {name}. Remaining: {remaining}")
        except Exception as e:
            if self.debug:
                print(f"[Credits] Error checking credits: {e}")
            # Allow execution if credit system unavailable
            pass
        
        try:
            if name == "get_diagram":
                result = self._tool_get_diagram()
            elif name == "read_file":
                result = self._tool_read_file(args.get("filepath", ""), args.get("context", ""))
            elif name == "search_code":
                result = self._tool_search_code(args.get("keywords", ""))
            elif name == "recall_memory":
                result = self._tool_recall_memory()
            elif name == "save_learning":
                result = self._tool_save_learning(args.get("topic", ""), args.get("summary", ""))
            elif name == "web_search":
                result = self._tool_web_search(args.get("query", ""))
            elif name == "write_file":
                result = self._tool_write_file(
                    args.get("filepath", ""),
                    args.get("content", ""),
                    args.get("description", "")
                )
            elif name == "run_command":
                result = self._tool_run_command(
                    args.get("command", ""),
                    args.get("working_directory", "")
                )
            elif name == "ask_user":
                result = self._tool_ask_user(args.get("question", ""), args.get("options", ""))
            
            # Task Management Tools
            elif name == "create_task":
                result = self._tool_create_task(
                    args.get("title", ""),
                    args.get("description", ""),
                    args.get("priority", "medium")
                )
            elif name == "update_task":
                result = self._tool_update_task(
                    args.get("task_id", 0),
                    args.get("status", "pending"),
                    args.get("notes", "")
                )
            elif name == "list_tasks":
                result = self._tool_list_tasks()
            elif name == "clear_tasks":
                result = self._tool_clear_tasks()
            
            # Diagram Tools
            elif name == "update_diagram":
                result = self._tool_update_diagram(
                    args.get("action", "add"),
                    args.get("node_path", ""),
                    args.get("node_type", "file"),
                    args.get("description", "")
                )
            
            # Command Control
            elif name == "stop_command":
                result = self._tool_stop_command()
            
            # Search Learning Tools
            elif name == "save_search_learning":
                result = self._tool_save_search_learning(
                    args.get("topic", ""),
                    args.get("insight", ""),
                    args.get("source", "")
                )
            elif name == "recall_search_learnings":
                result = self._tool_recall_search_learnings(args.get("query", ""))
            elif name == "group_files":
                result = self._tool_group_files(
                    args.get("group_name", ""),
                    args.get("files", []),
                    args.get("description", "")
                )
            elif name == "list_groups":
                result = self._tool_list_groups()
            
            # Git Integration Tools
            elif name == "git_status":
                result = self._tool_git_status()
            elif name == "git_diff":
                result = self._tool_git_diff(
                    args.get("file_path", ""),
                    args.get("staged", False)
                )
            
            # File Operation Tools
            elif name == "find_file":
                result = self._tool_find_file(
                    args.get("pattern", "*"),
                    args.get("max_results", 20)
                )
            elif name == "compare_files":
                result = self._tool_compare_files(
                    args.get("file1", ""),
                    args.get("file2", "")
                )
            elif name == "summarize_file":
                result = self._tool_summarize_file(args.get("file_path", ""))
            
            # Dependency Analysis Tools
            elif name == "get_dependencies":
                result = self._tool_get_dependencies()
            elif name == "dependency_tree":
                result = self._tool_dependency_tree(args.get("package", ""))
            
            # Phase 4: Error Analysis Tools
            elif name == "explain_error":
                result = self._tool_explain_error(args.get("error_message", ""))
            elif name == "analyze_stack_trace":
                result = self._tool_analyze_stack_trace(args.get("stack_trace", ""))
            
            # Phase 5: Code Quality Tools
            elif name == "estimate_complexity":
                result = self._tool_estimate_complexity(args.get("file_path", ""))
            elif name == "code_smell_scan":
                result = self._tool_code_smell_scan(args.get("file_path", ""))
            elif name == "project_health":
                result = self._tool_project_health()
            
            # Phase 6: Code Intelligence Tools
            elif name == "suggest_related_files":
                result = self._tool_suggest_related_files(args.get("file_path", ""))
            elif name == "create_snippet":
                result = self._tool_create_snippet(
                    args.get("name", ""),
                    args.get("code", ""),
                    args.get("language", "python")
                )
            
            # Phase 7: Dev Server Tools
            elif name == "hot_reload_status":
                result = self._tool_hot_reload_status()
            elif name == "run_tests":
                result = self._tool_run_tests(args.get("test_path", ""))
            
            # Phase 8: External Tools
            elif name == "read_url":
                result = self._tool_read_url(
                    args.get("url", ""),
                    args.get("format", "summary")
                )
            
            # AI-Controlled Slicing (FREE)
            elif name == "slice_output":
                result = self._tool_slice_output(
                    args.get("content", ""),
                    args.get("format", "summary"),
                    args.get("search", "")
                )
            
            else:
                result = f"Unknown tool: {name}"
            
            elapsed = time.time() - start_time
            self.stats.tools_used += 1
            self.stats.tool_times[name] = elapsed
            
            return ToolResult(success=True, result=result, elapsed=elapsed)
            
        except Exception as e:
            elapsed = time.time() - start_time
            return ToolResult(success=False, result="", error=str(e), elapsed=elapsed)

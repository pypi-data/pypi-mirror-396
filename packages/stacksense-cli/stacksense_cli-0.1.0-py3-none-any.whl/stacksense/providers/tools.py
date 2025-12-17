"""
Shared Tool Definitions
=======================
StackSense tools available to all AI providers.
All features are available - users pay per-use via credits.
"""

from typing import List, Optional
from .base import ToolDefinition


# Credit costs per tool
# All tools available to all users - payment is per-use
TOOL_COSTS = {
    # Free (0 credits)
    "ask_user": 0,
    "stop_command": 0,  # Free - stopping is always allowed
    "git_status": 0,  # Free - essential context
    "slice_output": 0,  # Free - AI can re-slice content
    
    # Basic operations (1 credit)
    "git_diff": 1,  # View changes
    "get_diagram": 1,
    "read_file": 1,
    "search_code": 1,
    "recall_memory": 1,
    "list_tasks": 1,
    "update_diagram": 1,
    "recall_search_learnings": 1,
    "list_groups": 1,  # View file groups
    "find_file": 1,  # Find files by name pattern
    "summarize_file": 1,  # One-line file summary
    "get_dependencies": 1,  # List project dependencies
    "hot_reload_status": 1,  # Check dev server status
    
    # Medium operations (2-3 credits)
    "compare_files": 2,  # Diff two files
    "dependency_tree": 2,  # Show why package is installed
    "explain_error": 2,  # Parse and explain errors
    "analyze_stack_trace": 2,  # Extract stack trace info
    "estimate_complexity": 2,  # File complexity score
    "code_smell_scan": 2,  # Scan for code issues
    "project_health": 2,  # Overall project health
    "suggest_related_files": 2,  # Find related files
    "create_snippet": 2,  # Save code snippets
    "read_url": 2,  # Fetch URL content (HTTPS only)
    "save_learning": 2,
    "save_search_learning": 2,
    "create_task": 2,
    "update_task": 2,
    "clear_tasks": 2,
    "group_files": 2,  # Group related files together
    "web_search": 3,
    "write_file": 3,
    "run_command": 3,
    "run_tests": 3,  # Execute test suite
    
    # Premium operations (4-5 credits)
    "diagram_generate": 4,
    "agent": 5,
    "repo_scan": 5,
}



STACKSENSE_TOOLS: List[ToolDefinition] = [
    # Git Integration Tools (FREE/1 credit)
    ToolDefinition(
        name="git_status",
        description="Show git status - changed, staged, and untracked files. FREE tool - use to understand what's modified.",
        parameters={},
        required=[]
    ),
    
    ToolDefinition(
        name="slice_output",
        description="Re-slice content with different format. FREE tool - use when default slicing didn't show what you need.",
        parameters={
            "content": {"type": "string", "description": "Content to slice"},
            "format": {"type": "string", "description": "Format: summary, full, first:N, last:N, or search"},
            "search": {"type": "string", "description": "If format='search', pattern to find with context"}
        },
        required=["content"]
    ),
    
    ToolDefinition(
        name="git_diff",
        description="Show git diff for changed files. See exactly what was modified.",
        parameters={
            "file_path": {
                "type": "string",
                "description": "Optional file path to diff (empty = all files)"
            },
            "staged": {
                "type": "boolean",
                "description": "If true, show staged changes (--cached)"
            }
        },
        required=[]
    ),
    
    # File Operation Tools
    ToolDefinition(
        name="find_file",
        description="Find files by name pattern (glob-style). Different from search_code - finds by filename, not content.",
        parameters={
            "pattern": {
                "type": "string",
                "description": "Glob pattern (e.g., '*.py', 'auth*', 'test_*.js')"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum results (default 20)"
            }
        },
        required=["pattern"]
    ),
    
    ToolDefinition(
        name="compare_files",
        description="Compare two files and show differences (unified diff).",
        parameters={
            "file1": {
                "type": "string",
                "description": "First file path (relative to workspace)"
            },
            "file2": {
                "type": "string",
                "description": "Second file path (relative to workspace)"
            }
        },
        required=["file1", "file2"]
    ),
    
    ToolDefinition(
        name="summarize_file",
        description="Generate a one-line summary of what a file does (docstrings, classes, exports).",
        parameters={
            "file_path": {
                "type": "string",
                "description": "Path to file (relative to workspace)"
            }
        },
        required=["file_path"]
    ),
    
    # Dependency Analysis Tools
    ToolDefinition(
        name="get_dependencies",
        description="Get project dependencies from package.json, requirements.txt, etc. Lists installed packages.",
        parameters={},
        required=[]
    ),
    
    ToolDefinition(
        name="dependency_tree",
        description="Show dependency tree - why a package is installed (npm ls or pip show).",
        parameters={
            "package": {
                "type": "string",
                "description": "Optional package name to get tree for"
            }
        },
        required=[]
    ),
    
    # Phase 4: Error Analysis Tools
    ToolDefinition(
        name="explain_error",
        description="Parse and explain an error message with likely cause and suggested fix.",
        parameters={
            "error_message": {"type": "string", "description": "The error text to analyze"}
        },
        required=["error_message"]
    ),
    
    ToolDefinition(
        name="analyze_stack_trace",
        description="Parse a stack trace to extract file locations and error info.",
        parameters={
            "stack_trace": {"type": "string", "description": "The full stack trace text"}
        },
        required=["stack_trace"]
    ),
    
    # Phase 5: Code Quality Tools
    ToolDefinition(
        name="estimate_complexity",
        description="Get complexity score for a file (lines, functions, nesting depth).",
        parameters={
            "file_path": {"type": "string", "description": "Path to file to analyze"}
        },
        required=["file_path"]
    ),
    
    ToolDefinition(
        name="code_smell_scan",
        description="Scan for common code issues (print statements, TODOs, long lines).",
        parameters={
            "file_path": {"type": "string", "description": "Optional file path (empty=scan project)"}
        },
        required=[]
    ),
    
    ToolDefinition(
        name="project_health",
        description="Overall project health check (README, tests, docs, dependencies).",
        parameters={},
        required=[]
    ),
    
    # Phase 6: Code Intelligence Tools
    ToolDefinition(
        name="suggest_related_files",
        description="Find files related via imports/references.",
        parameters={
            "file_path": {"type": "string", "description": "Path to file to analyze"}
        },
        required=["file_path"]
    ),
    
    ToolDefinition(
        name="create_snippet",
        description="Save a reusable code snippet for later use.",
        parameters={
            "name": {"type": "string", "description": "Snippet name"},
            "code": {"type": "string", "description": "The code to save"},
            "language": {"type": "string", "description": "Language (default: python)"}
        },
        required=["name", "code"]
    ),
    
    # Phase 7: Dev Server Tools
    ToolDefinition(
        name="hot_reload_status",
        description="Check if dev server is running and on what port.",
        parameters={},
        required=[]
    ),
    
    ToolDefinition(
        name="run_tests",
        description="Execute test suite (pytest or npm test).",
        parameters={
            "test_path": {"type": "string", "description": "Optional specific test path"}
        },
        required=[]
    ),
    
    # Phase 8: External Tools
    ToolDefinition(
        name="read_url",
        description="Fetch content from HTTPS URL (with security restrictions).",
        parameters={
            "url": {"type": "string", "description": "HTTPS URL to fetch"},
            "format": {"type": "string", "description": "Output format: summary, full, first:N, last:N"}
        },
        required=["url"]
    ),
    
    ToolDefinition(
        name="get_diagram",
        description="Get codebase structure showing files, directories, and architecture. Use this FIRST to understand what files exist.",
        parameters={},
        required=[]
    ),
    
    ToolDefinition(
        name="update_diagram",
        description="Update the codebase diagram when files are created, deleted, or modified. Use after write_file to keep diagram current.",
        parameters={
            "action": {
                "type": "string",
                "description": "Action: 'add' (new file), 'remove' (deleted file), or 'update' (modified file)"
            },
            "node_path": {
                "type": "string",
                "description": "Path to the file/folder relative to workspace root"
            },
            "node_type": {
                "type": "string",
                "description": "Type of node: 'file' or 'directory'"
            },
            "description": {
                "type": "string",
                "description": "Optional description of what the file does"
            }
        },
        required=["action", "node_path"]
    ),
    
    ToolDefinition(
        name="read_file",
        description="Read contents of a specific file. For large files, relevant sections are extracted automatically.",
        parameters={
            "filepath": {
                "type": "string",
                "description": "Path to file relative to workspace root"
            },
            "context": {
                "type": "string",
                "description": "What you're looking for (helps extract relevant sections)"
            }
        },
        required=["filepath"]
    ),
    
    ToolDefinition(
        name="search_code",
        description="Search for keywords across the codebase using grep. Returns files containing the terms.",
        parameters={
            "keywords": {
                "type": "string",
                "description": "Comma-separated keywords to search for"
            }
        },
        required=["keywords"]
    ),
    
    ToolDefinition(
        name="recall_memory",
        description="Remember what you learned about this codebase in previous sessions. [REQUIRES: Ultra plan]",
        parameters={},
        required=[]
    ),
    
    ToolDefinition(
        name="save_learning",
        description="Save an important insight about the codebase for future reference. [REQUIRES: Pro plan]",
        parameters={
            "topic": {
                "type": "string",
                "description": "Short topic name (e.g., 'authentication', 'database')"
            },
            "summary": {
                "type": "string",
                "description": "What you learned (1-3 sentences)"
            }
        },
        required=["topic", "summary"]
    ),
    
    ToolDefinition(
        name="web_search",
        description="Search the web for information about technologies, frameworks, or APIs you don't know. [REQUIRES: Starter plan]",
        parameters={
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        required=["query"]
    ),
    
    ToolDefinition(
        name="write_file",
        description="Create or modify a file. Permission is handled automatically. [REQUIRES: Pro plan]",
        parameters={
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
        required=["filepath", "content", "description"]
    ),
    
    ToolDefinition(
        name="run_command",
        description="Execute a terminal command. Permission is handled automatically. [REQUIRES: Pro plan]",
        parameters={
            "command": {
                "type": "string",
                "description": "The shell command to execute"
            },
            "description": {
                "type": "string",
                "description": "What this command does"
            }
        },
        required=["command", "description"]
    ),
    
    ToolDefinition(
        name="ask_user",
        description="MANDATORY for permissions. Call this to ask the user a question or request permission.",
        parameters={
            "question": {
                "type": "string",
                "description": "The question to ask the user"
            },
            "options": {
                "type": "string",
                "description": "Comma-separated options (e.g., 'yes,no' or 'option1,option2')"
            }
        },
        required=["question"]
    ),
    
    # Task Management Tools
    ToolDefinition(
        name="create_task",
        description="Create a task in todo.json. Use for breaking down work into 1-3 small chunks.",
        parameters={
            "title": {
                "type": "string",
                "description": "Short task title"
            },
            "description": {
                "type": "string",
                "description": "Detailed description of what to do"
            },
            "priority": {
                "type": "string",
                "description": "Task priority: high, medium, or low"
            }
        },
        required=["title"]
    ),
    
    ToolDefinition(
        name="update_task",
        description="Update task status. When all tasks are done, todo is auto-cleared.",
        parameters={
            "task_id": {
                "type": "integer",
                "description": "Task ID number"
            },
            "status": {
                "type": "string",
                "description": "New status: pending, in_progress, done, or blocked"
            },
            "notes": {
                "type": "string",
                "description": "Notes about what was done"
            }
        },
        required=["task_id", "status"]
    ),
    
    ToolDefinition(
        name="list_tasks",
        description="List all current tasks from todo.json with status.",
        parameters={},
        required=[]
    ),
    
    ToolDefinition(
        name="clear_tasks",
        description="Clear all tasks from todo.json when work is complete.",
        parameters={},
        required=[]
    ),
    
    # Command Control
    ToolDefinition(
        name="stop_command",
        description="Stop a currently running terminal command. Use if command is taking too long or needs to be changed.",
        parameters={},
        required=[]
    ),
    
    # Search Learning Tools
    ToolDefinition(
        name="save_search_learning",
        description="Save an important insight from web search to important.json. Helps avoid repeating research. Updates existing topics instead of duplicating.",
        parameters={
            "topic": {
                "type": "string",
                "description": "Topic name (e.g., 'FastAPI Celery integration')"
            },
            "insight": {
                "type": "string",
                "description": "Key insight learned (e.g., 'Use celery[redis], configure broker in lifespan')"
            },
            "source": {
                "type": "string",
                "description": "Optional URL source of the information"
            }
        },
        required=["topic", "insight"]
    ),
    
    ToolDefinition(
        name="recall_search_learnings",
        description="Recall important insights from previous web searches. Check this BEFORE doing a new web search to avoid repeating research.",
        parameters={
            "query": {
                "type": "string",
                "description": "Optional filter to find relevant insights"
            }
        },
        required=[]
    ),
    
    # File Grouping Tools
    ToolDefinition(
        name="group_files",
        description="Group related files together for better project understanding. Use when you discover files that work together for a feature/functionality.",
        parameters={
            "group_name": {
                "type": "string",
                "description": "Name for this group (e.g., 'authentication_files', 'api_routes')"
            },
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths that belong together"
            },
            "description": {
                "type": "string",
                "description": "What this group does/represents"
            }
        },
        required=["group_name", "files"]
    ),
    
    ToolDefinition(
        name="list_groups",
        description="List all file groups from group.json. Shows group names, file counts, and descriptions.",
        parameters={},
        required=[]
    ),
    
    # Premium Tools (4-5 credits)
    ToolDefinition(
        name="diagram_generate",
        description="Generate a visual architecture diagram for the codebase. Creates flowcharts, dependency graphs, or system diagrams. Use for complex projects.",
        parameters={
            "type": {
                "type": "string",
                "description": "Diagram type: 'flowchart', 'dependency', 'sequence', or 'architecture'"
            },
            "description": {
                "type": "string", 
                "description": "What to visualize (e.g., 'API request flow', 'module dependencies')"
            }
        },
        required=["type", "description"]
    ),
    
    ToolDefinition(
        name="agent",
        description="Spawn a sub-agent to handle a complex task in the background. Use for research, analysis, or parallel work. Returns task ID to check status.",
        parameters={
            "task": {
                "type": "string",
                "description": "Task description for the sub-agent"
            },
            "context": {
                "type": "string",
                "description": "Additional context to provide the sub-agent"
            }
        },
        required=["task"]
    ),
    
    ToolDefinition(
        name="repo_scan",
        description="Full repository scan - analyzes all files, generates dependency graph, and builds comprehensive codebase understanding. Use when first exploring a new project.",
        parameters={
            "depth": {
                "type": "integer",
                "description": "How deep to scan (1=shallow, 3=deep, default=2)"
            },
            "include_tests": {
                "type": "boolean",
                "description": "Whether to include test files in analysis"
            }
        },
        required=[]
    )
]



def get_tool_definitions(include_dangerous: bool = False) -> List[ToolDefinition]:
    """
    Get tool definitions for AI.
    
    Args:
        include_dangerous: Include write_file and run_command
        
    Returns:
        List of tool definitions
    """
    if include_dangerous:
        return STACKSENSE_TOOLS
    
    # Exclude dangerous tools
    safe_tools = ["get_diagram", "read_file", "search_code", "recall_memory", 
                  "save_learning", "web_search", "ask_user"]
    return [t for t in STACKSENSE_TOOLS if t.name in safe_tools]


def get_tools_for_subscription(include_dangerous: bool = True) -> List[ToolDefinition]:
    """
    Get all tools (credit-based system - all features available).
    
    Args:
        include_dangerous: Include write_file and run_command
        
    Returns:
        List of all tools
    """
    if include_dangerous:
        return STACKSENSE_TOOLS
    
    # Exclude dangerous tools
    safe_tools = ["get_diagram", "read_file", "search_code", "recall_memory", 
                  "save_learning", "web_search", "ask_user"]
    return [t for t in STACKSENSE_TOOLS if t.name in safe_tools]


def get_tools_for_provider(provider_name: str) -> List[dict]:
    """
    Get all tools in the format expected by a provider.
    
    Args:
        provider_name: Provider name (openai, grok, openrouter, together)
        
    Returns:
        List of tool definitions in provider format
    """
    tools = get_tools_for_subscription(include_dangerous=True)
    return [t.to_openai_format() for t in tools]


def get_tool_cost(tool_name: str) -> int:
    """Get credit cost for a tool."""
    return TOOL_COSTS.get(tool_name, 1)


def get_credit_status_message() -> str:
    """
    Get a message describing credit status for the AI.
    
    Returns:
        Message with balance and costs for system prompt
    """
    try:
        from stacksense.credits import get_balance
        balance = get_balance()
        remaining = balance["credits_remaining"]
        tier = "Free" if balance["is_free_tier"] else "Paid"
    except Exception:
        remaining = 250
        tier = "Free"
    
    message = f"""
## CREDITS: {remaining:,} remaining ({tier})

### TOOL COSTS:
- ask_user: FREE
- get_diagram, read_file, search_code, recall_memory: 1 credit
- save_learning: 2 credits
- web_search, write_file, run_command: 3 credits

All tools are AVAILABLE. Each use deducts credits.
If credits run out, suggest: stacksense upgrade
"""
    
    return message

"""
Tool Executor - Centralized Tool Execution
==========================================
Executes tools safely with:
- Error handling
- Performance monitoring
- Budget enforcement
- Logging
"""

import time
import asyncio
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class ToolCost(Enum):
    """Tool cost classification"""
    FREE = "free"      # Instant, cached
    CHEAP = "cheap"    # < 1s
    EXPENSIVE = "expensive"  # > 1s


@dataclass
class ToolExecution:
    """Record of a tool execution"""
    name: str
    args: Dict[str, Any]
    success: bool
    result: str
    error: Optional[str]
    elapsed: float
    cost: ToolCost
    timestamp: float = field(default_factory=time.time)


@dataclass
class ToolBudget:
    """Budget tracking for tool usage"""
    max_tools: int = 8
    max_expensive: int = 3
    max_time: float = 60.0
    
    tools_used: int = 0
    expensive_used: int = 0
    time_spent: float = 0.0
    
    def can_use(self, cost: ToolCost) -> bool:
        """Check if budget allows another tool"""
        if self.tools_used >= self.max_tools:
            return False
        if self.time_spent >= self.max_time:
            return False
        if cost == ToolCost.EXPENSIVE and self.expensive_used >= self.max_expensive:
            return False
        return True
    
    def record(self, cost: ToolCost, elapsed: float):
        """Record tool usage"""
        self.tools_used += 1
        self.time_spent += elapsed
        if cost == ToolCost.EXPENSIVE:
            self.expensive_used += 1
    
    def get_warning(self) -> Optional[str]:
        """Get warning if approaching limits"""
        if self.tools_used >= self.max_tools - 1:
            return "⚠️ Tool budget almost exhausted. Answer with what you have."
        if self.expensive_used >= self.max_expensive:
            return "⚠️ Expensive tool limit reached. Use cached/free tools only."
        return None


class ToolExecutor:
    """
    Centralized tool execution with monitoring and safety.
    
    Features:
    - Budget enforcement
    - Error handling
    - Performance tracking
    - Audit logging
    """
    
    # Tool cost classifications
    TOOL_COSTS = {
        "get_diagram": ToolCost.FREE,
        "recall_memory": ToolCost.FREE,
        "save_learning": ToolCost.FREE,
        "search_code": ToolCost.CHEAP,
        "read_file": ToolCost.CHEAP,  # May become EXPENSIVE for large files
        "web_search": ToolCost.EXPENSIVE,
    }
    
    def __init__(
        self,
        tools: Dict[str, Callable],
        max_tools: int = 8,
        max_time: float = 60.0,
        debug: bool = False
    ):
        """
        Initialize executor.
        
        Args:
            tools: Dict mapping tool names to callable functions
            max_tools: Maximum tool calls per query
            max_time: Maximum total tool time in seconds
            debug: Whether to print debug info
        """
        self.tools = tools
        self.budget = ToolBudget(max_tools=max_tools, max_time=max_time)
        self.debug = debug
        
        # Execution history
        self.history: List[ToolExecution] = []
    
    def reset(self):
        """Reset for new query"""
        self.budget = ToolBudget(
            max_tools=self.budget.max_tools,
            max_time=self.budget.max_time
        )
        self.history = []
    
    def execute(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> ToolExecution:
        """
        Execute a tool safely.
        
        Args:
            tool_name: Name of tool to execute
            tool_args: Arguments to pass to tool
            
        Returns:
            ToolExecution record with result/error
        """
        
        # Get tool cost
        cost = self.TOOL_COSTS.get(tool_name, ToolCost.CHEAP)
        
        # Check for large file (upgrade to expensive)
        if tool_name == "read_file":
            # Could check file size here
            pass
        
        # Check budget
        if not self.budget.can_use(cost):
            return ToolExecution(
                name=tool_name,
                args=tool_args,
                success=False,
                result="",
                error="Tool budget exceeded",
                elapsed=0.0,
                cost=cost
            )
        
        # Execute
        start = time.time()
        error = None
        result = ""
        success = True
        
        try:
            tool_fn = self.tools.get(tool_name)
            
            if tool_fn is None:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            result = tool_fn(**tool_args)
            
        except Exception as e:
            success = False
            error = str(e)
            result = ""
        
        elapsed = time.time() - start
        
        # Upgrade cost if slow
        if elapsed > 2.0 and cost != ToolCost.EXPENSIVE:
            cost = ToolCost.EXPENSIVE
        
        # Record in budget
        self.budget.record(cost, elapsed)
        
        # Create execution record
        execution = ToolExecution(
            name=tool_name,
            args=tool_args,
            success=success,
            result=result,
            error=error,
            elapsed=elapsed,
            cost=cost
        )
        
        self.history.append(execution)
        
        if self.debug:
            status = "✓" if success else "✗"
            print(f"  {status} {tool_name}: {elapsed:.2f}s")
        
        return execution
    
    def get_budget_warning(self) -> Optional[str]:
        """Get any budget warnings"""
        return self.budget.get_warning()
    
    def get_stats(self) -> Dict:
        """Get execution statistics"""
        return {
            "total_calls": len(self.history),
            "successful": sum(1 for e in self.history if e.success),
            "failed": sum(1 for e in self.history if not e.success),
            "total_time": sum(e.elapsed for e in self.history),
            "by_tool": self._group_by_tool(),
            "budget": {
                "tools_used": self.budget.tools_used,
                "max_tools": self.budget.max_tools,
                "time_spent": round(self.budget.time_spent, 2),
                "max_time": self.budget.max_time
            }
        }
    
    def _group_by_tool(self) -> Dict:
        """Group stats by tool name"""
        groups = {}
        for e in self.history:
            if e.name not in groups:
                groups[e.name] = {"calls": 0, "time": 0.0, "errors": 0}
            groups[e.name]["calls"] += 1
            groups[e.name]["time"] += e.elapsed
            if not e.success:
                groups[e.name]["errors"] += 1
        return groups
    
    def format_performance_summary(self) -> str:
        """Format a nice performance summary for display"""
        stats = self.get_stats()
        
        lines = [
            "╭───────────── Query Performance ─────────────╮",
            f"│ Tools: {stats['total_calls']} ({stats['successful']} ✓, {stats['failed']} ✗)".ljust(46) + "│",
            f"│ Time: {stats['total_time']:.1f}s".ljust(46) + "│",
        ]
        
        for tool, data in stats['by_tool'].items():
            line = f"│   • {tool}: {data['calls']}x, {data['time']:.1f}s"
            if data['errors'] > 0:
                line += f" ({data['errors']} errors)"
            lines.append(line.ljust(46) + "│")
        
        lines.append("╰─────────────────────────────────────────────╯")
        
        return '\n'.join(lines)


async def execute_with_retry(
    executor: ToolExecutor,
    tool_name: str,
    tool_args: Dict[str, Any],
    max_retries: int = 2
) -> ToolExecution:
    """
    Execute tool with retry on failure.
    
    Args:
        executor: ToolExecutor instance
        tool_name: Tool to execute
        tool_args: Tool arguments
        max_retries: Maximum retry attempts
        
    Returns:
        ToolExecution record
    """
    for attempt in range(max_retries + 1):
        result = executor.execute(tool_name, tool_args)
        
        if result.success:
            return result
        
        if attempt < max_retries:
            await asyncio.sleep(0.5)  # Brief pause before retry
    
    return result

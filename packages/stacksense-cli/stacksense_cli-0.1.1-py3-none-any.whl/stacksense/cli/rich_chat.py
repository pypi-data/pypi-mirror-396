"""
StackSense Rich Chat UI
========================
Claude Code / Antigravity-style chat interface with collapsible panels,
streaming responses, and polished UX.
"""

import os
import sys
import time
import re
import subprocess
from typing import Optional, List, Dict, Any, Callable, Tuple
from dataclasses import dataclass, field

# Rich imports
try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.text import Text
    from rich.table import Table
    from rich.rule import Rule
    from rich.style import Style
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Prompt toolkit for tab completion
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.shortcuts import CompleteStyle
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

# Console instance
console = Console() if RICH_AVAILABLE else None


def get_openrouter_models() -> List[str]:
    """Get list of available free OpenRouter models"""
    try:
        from stacksense.core.openrouter_client import get_client
        client = get_client()
        models = client.get_free_models()
        return [m.id for m in models]
    except Exception:
        return []


@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    model: Optional[str] = None  # Model used for this response
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ThinkingPanel:
    """
    Collapsible thinking panel that shows progress steps with LIVE STREAMING.
    
    Features:
    - Real-time step updates
    - Per-step timing
    - Streaming indicator for AI response
    - Auto-collapse on completion
    
    Usage:
        with ThinkingPanel("Analyzing codebase...") as panel:
            panel.step("Searching for: authentication")
            panel.step("Found 3 files")
            panel.stream_start()  # Start streaming indicator
        # Auto-collapses to: "✓ Analyzing codebase... (3 steps, 1.2s)"
    """
    
    def __init__(self, title: str, console: Console = None):
        self.title = title
        self.console = console or Console()
        self.steps: List[tuple] = []  # (message, elapsed_time or None)
        self.start_time: float = 0
        self.step_start_time: float = 0
        self.live: Optional[Live] = None
        self.is_streaming: bool = False
        self._spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self._stream_frames = ['●○○', '○●○', '○○●', '○●○']
        self._frame_idx = 0
    
    def _render(self) -> Panel:
        """Render the current state of the thinking panel"""
        # Spinner animation
        spinner = self._spinner_frames[self._frame_idx % len(self._spinner_frames)]
        self._frame_idx += 1
        
        # Build content
        lines = []
        
        # Show all steps with timing
        for i, (step_msg, step_time) in enumerate(self.steps[-6:]):  # Show last 6 steps
            if step_time is not None:
                # Completed step with timing
                lines.append(f"   [green]✓[/green] {step_msg} [dim]({step_time:.1f}s)[/dim]")
            else:
                # In-progress step
                lines.append(f"   [cyan]▸[/cyan] {step_msg}")
        
        # Show streaming indicator if active
        if self.is_streaming:
            stream_indicator = self._stream_frames[self._frame_idx % len(self._stream_frames)]
            lines.append(f"   [yellow]{stream_indicator}[/yellow] [italic]Generating response...[/italic]")
        
        if not lines:
            lines.append("   [dim]Starting...[/dim]")
        
        content = "\n".join(lines)
        
        # Calculate elapsed time
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        return Panel(
            content,
            title=f"{spinner} [bold cyan]{self.title}[/bold cyan] [dim]({elapsed:.1f}s)[/dim]",
            border_style="cyan",
            expand=False,
            padding=(0, 1)
        )
    
    def step(self, message: str, completed: bool = False, elapsed: float = None):
        """
        Add or update a step in the thinking panel.
        
        Args:
            message: Step description
            completed: Whether this step is complete
            elapsed: Time taken for this step (auto-calculated if None)
        """
        now = time.time()
        
        if elapsed is None and completed and self.step_start_time:
            elapsed = now - self.step_start_time
        
        self.steps.append((message, elapsed if completed else None))
        self.step_start_time = now
        
        if self.live:
            self.live.update(self._render())
    
    def stream_start(self):
        """Mark that AI response is now streaming"""
        self.is_streaming = True
        if self.live:
            self.live.update(self._render())
    
    def stream_stop(self):
        """Mark that AI response streaming is complete"""
        self.is_streaming = False
        if self.live:
            self.live.update(self._render())
    
    def update_last_step(self, new_message: str = None, elapsed: float = None):
        """Update the last step (e.g., to mark it complete)"""
        if self.steps:
            old_msg, _ = self.steps[-1]
            self.steps[-1] = (new_message or old_msg, elapsed)
            if self.live:
                self.live.update(self._render())
    
    def __enter__(self):
        self.start_time = time.time()
        self.step_start_time = time.time()
        if RICH_AVAILABLE:
            self.live = Live(
                self._render(),
                console=self.console,
                refresh_per_second=10,
                transient=True  # Will be replaced by summary
            )
            self.live.start()
        else:
            print(f"🔍 {self.title}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        
        if self.live:
            self.live.stop()
        
        # Print collapsed summary
        step_count = len(self.steps)
        if RICH_AVAILABLE:
            summary = Text()
            summary.append("✓ ", style="green")
            summary.append(self.title, style="dim")
            summary.append(f" ({step_count} steps, {elapsed:.1f}s)", style="dim")
            self.console.print(summary)
        else:
            print(f"✓ {self.title} ({step_count} steps, {elapsed:.1f}s)")


class StatusLine:
    """
    Single-line status that auto-clears.
    
    Usage:
        with StatusLine("Loading model..."):
            # do work
        # Status line disappears
    """
    
    def __init__(self, message: str, console: Console = None):
        self.message = message
        self.console = console or Console()
        self.live: Optional[Live] = None
        self._spinner_frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        self._frame_idx = 0
    
    def _render(self) -> Text:
        spinner = self._spinner_frames[self._frame_idx % len(self._spinner_frames)]
        self._frame_idx += 1
        text = Text()
        text.append(f"{spinner} ", style="cyan")
        text.append(self.message, style="dim")
        return text
    
    def update(self, message: str):
        """Update the status message"""
        self.message = message
        if self.live:
            self.live.update(self._render())
    
    def __enter__(self):
        if RICH_AVAILABLE:
            self.live = Live(
                self._render(),
                console=self.console,
                refresh_per_second=10,
                transient=True
            )
            self.live.start()
        else:
            print(f"⏳ {self.message}", end='\r')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()
        elif not RICH_AVAILABLE:
            # Clear the line
            print(' ' * (len(self.message) + 5), end='\r')


class ContextBar:
    """
    Context window usage bar based on model's token limit.
    
    Shows how much of the model's context window is being used
    with color-coded health status:
    - Green: <50% used (healthy)
    - Yellow: 50-80% used (caution)
    - Red: >80% used (danger)
    
    Usage:
        bar = ContextBar(model_id="google/gemini-2.0-flash-exp:free")
        bar.update(tokens_used=5000)
        bar.render()  # Displays: [████████░░░░░░░░░░░░] 5K / 1M tokens
    """
    
    def __init__(
        self, 
        model_id: str = None,
        context_length: int = None,
        console: Console = None
    ):
        self.console = console or Console() if RICH_AVAILABLE else None
        self.model_id = model_id or "default"
        self.tokens_used = 0
        
        # Get context length from OpenRouter or use fallback
        if context_length:
            self.context_length = context_length
        else:
            self.context_length = self._get_model_context_length(model_id)
    
    def _get_model_context_length(self, model_id: str) -> int:
        """Get context length from OpenRouter for this model."""
        if not model_id:
            return 4096  # Default fallback
        
        try:
            from stacksense.core.openrouter_client import get_client
            client = get_client()
            models = client.get_models(filter_type='all')
            
            for model in models:
                if model.id == model_id:
                    return model.context_length
            
            # Fallback context lengths for common models
            fallbacks = {
                "google/gemini": 1048576,
                "anthropic/claude": 200000,
                "openai/gpt-4": 128000,
                "openai/gpt-3.5": 16385,
                "mistral": 32768,
                "llama": 8192,
            }
            
            model_lower = model_id.lower()
            for pattern, ctx in fallbacks.items():
                if pattern in model_lower:
                    return ctx
            
        except Exception:
            pass
        
        return 4096  # Final fallback
    
    def update(self, tokens_used: int = None, messages: list = None):
        """
        Update the token count.
        
        Args:
            tokens_used: Direct token count (if known)
            messages: Chat messages to estimate tokens from
        """
        if tokens_used is not None:
            self.tokens_used = tokens_used
        elif messages:
            # Estimate: ~4 chars per token on average
            total_chars = sum(len(str(m.get('content', ''))) for m in messages)
            self.tokens_used = total_chars // 4
    
    def get_percentage(self) -> float:
        """Get usage percentage."""
        if self.context_length <= 0:
            return 0
        return (self.tokens_used / self.context_length) * 100
    
    def get_health_color(self) -> str:
        """Get color based on usage percentage."""
        pct = self.get_percentage()
        if pct < 50:
            return "green"
        elif pct < 80:
            return "yellow"
        else:
            return "red"
    
    def _format_tokens(self, tokens: int) -> str:
        """Format token count for display."""
        if tokens >= 1_000_000:
            return f"{tokens / 1_000_000:.1f}M"
        elif tokens >= 1_000:
            return f"{tokens / 1_000:.0f}K"
        else:
            return str(tokens)
    
    def _format_percentage(self) -> str:
        """Format percentage for display."""
        pct = self.get_percentage()
        if pct < 0.01:
            return "0%"
        elif pct < 1:
            return f"{pct:.2f}%"
        elif pct < 10:
            return f"{pct:.1f}%"
        else:
            return f"{pct:.0f}%"
    
    def get_model_short_name(self) -> str:
        """Get short display name for the model."""
        if not self.model_id:
            return "default"
        # Extract last part and clean up
        name = self.model_id.split('/')[-1]
        name = name.replace(':free', '').replace('-exp', '')
        # Truncate if too long
        if len(name) > 20:
            name = name[:17] + "..."
        return name
    
    def reset(self):
        """Reset token count to 0 (for model switch)."""
        self.tokens_used = 0
    
    def render(self) -> str:
        """Render the context bar as a string with percentage."""
        pct = self.get_percentage()
        color = self.get_health_color()
        
        # Build progress bar
        bar_len = 20
        filled = int(bar_len * pct / 100)
        filled = min(filled, bar_len)  # Cap at 100%
        
        bar = "█" * filled + "░" * (bar_len - filled)
        pct_str = self._format_percentage()
        model_name = self.get_model_short_name()
        
        return f"[{color}]{bar}[/{color}] [bold]{pct_str}[/bold] [dim]({model_name})[/dim]"
    
    def render_compact(self) -> str:
        """Render a compact version for the prompt."""
        pct = self.get_percentage()
        color = self.get_health_color()
        pct_str = self._format_percentage()
        model_name = self.get_model_short_name()
        
        return f"[{color}]⬤[/{color}] {pct_str} ({model_name})"
    
    def print(self):
        """Print the context bar to console."""
        if self.console and RICH_AVAILABLE:
            self.console.print(self.render())
        else:
            pct_str = self._format_percentage()
            model_name = self.get_model_short_name()
            print(f"[Context: {pct_str} ({model_name})]")


class RichChatUI:

    """
    Main chat UI manager with Claude/Antigravity-style interface.
    
    Features:
    - Collapsible thinking panels
    - Markdown response rendering
    - Clean input handling
    - Model switching (model:name for one-shot, /model for permanent)
    - Context bar showing token usage as percentage
    
    Model Switch Behavior:
    - Temporary (model:deepseek query): Shows temp model at 0%, then reverts
    - Permanent (/model deepseek): Switches to new model, resets to 0%
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.console = Console() if RICH_AVAILABLE else None
        self.history: List[ChatMessage] = []
        self.current_model: Optional[str] = None
        self.session_id: Optional[str] = None
        self.workspace_name: Optional[str] = None
        self.context_bar: Optional[ContextBar] = None
        
        # For temporary model switches
        self._saved_model: Optional[str] = None
        self._saved_context_bar: Optional[ContextBar] = None
    
    def set_model(self, model_id: str, context_length: int = None):
        """
        Set the current model and initialize context bar (PERMANENT switch).
        Resets context to 0%.
        """
        self.current_model = model_id
        self.context_bar = ContextBar(
            model_id=model_id,
            context_length=context_length,
            console=self.console
        )
        # Clear any saved state
        self._saved_model = None
        self._saved_context_bar = None
    
    def use_temp_model(self, model_id: str, context_length: int = None):
        """
        Temporarily switch to a model for one call.
        Saves current model state and creates a fresh 0% context bar.
        
        After the call, use restore_model() to go back.
        """
        # Save current state
        self._saved_model = self.current_model
        self._saved_context_bar = self.context_bar
        
        # Set temporary model with fresh 0% context
        self.current_model = model_id
        self.context_bar = ContextBar(
            model_id=model_id,
            context_length=context_length,
            console=self.console
        )
        
        if self.debug:
            print(f"[UI] Temp switch to {model_id} (0%)")
    
    def restore_model(self):
        """
        Restore the previous model after a temporary switch.
        Returns to saved model and its context percentage.
        """
        if self._saved_model and self._saved_context_bar:
            self.current_model = self._saved_model
            self.context_bar = self._saved_context_bar
            
            if self.debug:
                pct = self.context_bar.get_percentage()
                print(f"[UI] Restored to {self._saved_model} ({pct:.1f}%)")
            
            # Clear saved state
            self._saved_model = None
            self._saved_context_bar = None
            return True
        return False
    
    def has_temp_model(self) -> bool:
        """Check if currently using a temporary model."""
        return self._saved_model is not None
    
    def switch_model_permanent(self, model_id: str, context_length: int = None):
        """
        Permanently switch to a new model.
        Resets context to 0% and clears any temp state.
        """
        # Clear any temp state first
        self._saved_model = None
        self._saved_context_bar = None
        
        # Set new model with 0% context
        self.set_model(model_id, context_length)
        
        if self.debug:
            print(f"[UI] Permanent switch to {model_id} (0%)")
    
    def update_context(self, tokens_used: int = None, messages: list = None):
        """Update the context bar with current token usage."""
        if self.context_bar:
            self.context_bar.update(tokens_used=tokens_used, messages=messages)
    
    def show_context_bar(self):

        """Display the current context usage bar."""
        if self.context_bar and RICH_AVAILABLE:
            self.console.print(self.context_bar.render())
        elif self.context_bar:
            self.context_bar.print()

    
    def show_banner(
        self,
        model_name: str = "Unknown",
        session_id: str = "",
        workspace: Optional[str] = None,
        tech_stack: Optional[str] = None,
        provider: Optional[str] = None
    ):
        """Display the welcome banner (logo shown at startup)"""
        self.current_model = model_name
        self.session_id = session_id
        self.workspace_name = workspace
        
        if not RICH_AVAILABLE:
            provider_str = f" • Provider: {provider}" if provider else ""
            print(f"  Model: {model_name}{provider_str} | Workspace: {workspace or 'None'}")
            if tech_stack:
                print(f"  Tech Stack: {tech_stack}")
            return
        
        # Compact model display (logo already shown at startup)
        model_short = model_name.split('/')[-1].replace(':free', '') if model_name else "default"
        
        # Detect provider from model name if not provided
        if not provider:
            if model_name:
                if 'openai' in model_name.lower() or 'gpt' in model_name.lower():
                    provider = "OpenAI"
                elif 'grok' in model_name.lower():
                    provider = "Grok"
                elif 'together' in model_name.lower():
                    provider = "TogetherAI"
                else:
                    provider = "OpenRouter"
            else:
                provider = "OpenRouter"
        
        # Build info line with provider
        info_parts = [
            f"[cyan]Model:[/cyan] {model_short}",
            f"[dim]•[/dim] [magenta]{provider}[/magenta]",
            "[dim]/help • /model • exit[/dim]"
        ]
        
        info = "  ".join(info_parts)
        
        self.console.print(f"  {info}")
        self.console.print()
    
    def show_help(self):
        """Display help information"""
        if not RICH_AVAILABLE:
            print("""
Commands:
  exit, quit, q        - Exit StackSense
  /help                - Show this help
  /(free)model [name]  - Switch to free model (picker or direct)
  /(paid)model [name]  - Switch to paid model (picker or direct)
  /clear               - Clear screen
  /status              - Show session status
  
One-shot Model (use for one query, then revert):
  model:name query       - All models
  model(free):name query - Free models only
  model(paid):name query - Paid models only

Tool Calling Reliability:
  RELIABLE (use tools correctly):
    - anthropic/claude-3.5-sonnet (PAID)
    - openai/gpt-4o, gpt-4o-mini (PAID)
    - google/gemini-2.0-flash-exp:free (FREE, may rate limit)
  
  UNRELIABLE (often hallucinate instead of using tools):
    - Most free models (llama, qwen, mistral free tiers)
            """)
            return
        
        help_table = Table(title="📖 Commands", show_header=True, header_style="bold cyan")
        help_table.add_column("Command", style="green")
        help_table.add_column("Description")
        
        help_table.add_row("exit / quit / q", "Exit StackSense")
        help_table.add_row("/help", "Show this help")
        help_table.add_row("/clear", "Clear screen")
        help_table.add_row("/status", "Show session status")
        help_table.add_row("", "")
        help_table.add_row("[bold cyan]Permanent Switch[/bold cyan]", "")
        help_table.add_row("/(free)model [name]", "Switch to free model")
        help_table.add_row("/(paid)model [name]", "Switch to paid model")
        help_table.add_row("", "")
        help_table.add_row("[bold cyan]One-shot (reverts after)[/bold cyan]", "")
        help_table.add_row("model:name query", "Use model for ONE query")
        help_table.add_row("model(free):name query", "Use free model once")
        help_table.add_row("model(paid):name query", "Use paid model once")
        
        self.console.print()
        self.console.print(help_table)
        self.console.print()
        
        # Tool calling recommendations
        tool_panel = Panel(
            "[bold green]✅ RELIABLE TOOL CALLING:[/bold green]\n"
            "  • anthropic/claude-3.5-sonnet [yellow](PAID)[/yellow]\n"
            "  • openai/gpt-4o, gpt-4o-mini [yellow](PAID)[/yellow]\n"
            "  • google/gemini-2.0-flash-exp:free [green](FREE)[/green]\n\n"
            "[bold red]⚠️ OFTEN HALLUCINATE:[/bold red]\n"
            "  • Most free models (llama, qwen, mistral free tiers)\n"
            "  • They may explain actions instead of using tools",
            title="🔧 Tool Calling Models",
            border_style="cyan"
        )
        self.console.print(tool_panel)
        self.console.print()
        
        # CLI Commands section
        cli_panel = Panel(
            "[bold cyan]Credits & Account:[/bold cyan]\n"
            "  • [green]stacksense credits[/green]   - View your credit balance\n"
            "  • [green]stacksense login[/green]     - Restore credits on new device\n"
            "  • [green]stacksense redeem[/green]    - Redeem a license key\n"
            "  • [green]stacksense upgrade[/green]   - Buy more credits\n\n"
            "[bold cyan]Diagnostics:[/bold cyan]\n"
            "  • [green]stacksense doctor[/green]    - Check installation health\n"
            "  • [green]stacksense status[/green]    - View account status",
            title="💳 CLI Commands",
            border_style="green"
        )
        self.console.print(cli_panel)
        self.console.print()
        
        # Examples
        examples = Panel(
            "[green]/(free)model[/green] google/gemini-2.0-flash-exp:free\n"
            "[green]/(paid)model[/green] anthropic/claude-3.5-sonnet\n"
            "[green]model:gemini-2.0-flash-exp:free[/green] search the web for AI news",
            title="💡 Examples",
            border_style="dim"
        )
        self.console.print(examples)
        self.console.print()
    
    def show_status(
        self,
        session_id: str,
        model_type: str,
        model_name: str,
        workspace_scanned: bool,
        orchestrator_active: bool
    ):
        """Display session status"""
        if not RICH_AVAILABLE:
            print(f"\nSession: {session_id}")
            print(f"Model: {model_type} ({model_name})")
            print(f"Workspace scanned: {workspace_scanned}")
            print(f"Diagram system: {'Active' if orchestrator_active else 'Inactive'}\n")
            return
        
        status_table = Table(show_header=False, box=None, padding=(0, 2))
        status_table.add_column("Key", style="cyan")
        status_table.add_column("Value", style="bold")
        
        status_table.add_row("Session ID", session_id)
        status_table.add_row("Model Type", model_type)
        status_table.add_row("Model Name", model_name)
        status_table.add_row("Workspace Scanned", "✅ Yes" if workspace_scanned else "❌ No")
        status_table.add_row("Diagram System", "✅ Active" if orchestrator_active else "⚪ Inactive")
        
        panel = Panel(status_table, title="📊 Session Status", border_style="blue")
        self.console.print()
        self.console.print(panel)
        self.console.print()
    
    def get_input(self, prompt: str = "You: ", models: Optional[List[str]] = None, workspace_path: Optional[str] = None) -> str:
        """
        Get user input with tab completion.
        
        Completions:
        - model:<TAB> → model dropdown (all)
        - model(free):<TAB> → free models only
        - model(paid):<TAB> → paid models only
        - @<TAB> → file completion
        - /model<TAB> → model dropdown
        """
        if models is None:
            models = get_openrouter_models()
        
        try:
            if PROMPT_TOOLKIT_AVAILABLE:
                # Use the external completer with full command support
                from .completer import StackSenseCompleter
                
                session = PromptSession(
                    completer=StackSenseCompleter(workspace_path=workspace_path),
                    complete_while_typing=False,  # Only complete on TAB
                    complete_style=CompleteStyle.MULTI_COLUMN
                )
                user_input = session.prompt(
                    HTML(f'<b><cyan>{prompt.rstrip(": ")}</cyan></b>: '),
                    complete_while_typing=False
                )
                return user_input.strip()
            
            elif RICH_AVAILABLE:
                self.console.print()
                user_input = Prompt.ask(f"[bold cyan]{prompt.rstrip(': ')}[/bold cyan]")
                return user_input.strip()
            else:
                return input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            raise
    
    def parse_file_attachments(self, message: str) -> Tuple[List[str], str]:
        """
        Extract @file paths from message.
        
        Files are identified by having an extension (e.g., @file.py, @src/auth.ts)
        Models don't have extensions (e.g., @llama3, @qwen2.5)
        
        Returns:
            (list of file paths, cleaned message)
        """
        # Pattern: @path/to/file.ext (must have extension)
        pattern = r'@([^\s@]+\.[a-zA-Z0-9]+)'
        files = re.findall(pattern, message)
        
        # Remove file references from message
        cleaned = re.sub(pattern, '', message).strip()
        # Clean up multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return files, cleaned
    
    def parse_model_switch(self, user_input: str, available_models: Optional[List[str]] = None) -> Tuple[Optional[str], str]:
        """
        Parse model:name or model(free):name or model(paid):name prefix from input.
        
        Formats:
            model:phi3 your question here
            model(free):gemini query
            model(paid):gpt-4o query
        
        Returns:
            (model_name or None, remaining_query)
        """
        # Pattern: model(free):something query... or model(paid):something query...
        match = re.match(r'^model\((free|paid)\):(\S+)\s+(.+)$', user_input, re.DOTALL)
        if match:
            # filter_type = match.group(1)  # 'free' or 'paid' - not used but could filter
            model_name = match.group(2)
            query = match.group(3)
            return model_name, query
        
        # Pattern: model:something query...
        match = re.match(r'^model:(\S+)\s+(.+)$', user_input, re.DOTALL)
        if match:
            model_name = match.group(1)
            query = match.group(2)
            return model_name, query
        
        return None, user_input
    
    def show_file_attachments(self, files: List[str]):
        """Show notice about attached files"""
        if not files:
            return
        
        if RICH_AVAILABLE:
            self.console.print(f"[dim]📎 Attached: {', '.join(files)}[/dim]")
        else:
            print(f"📎 Attached: {', '.join(files)}")
    
    def show_model_switch_notice(self, model_name: str, one_shot: bool = True):
        """Show notice about model switch"""
        if one_shot:
            msg = f"[dim]Using [cyan]{model_name}[/cyan] for this query[/dim]"
        else:
            msg = f"[green]✓ Switched to [bold]{model_name}[/bold] permanently[/green]"
        
        if RICH_AVAILABLE:
            self.console.print(msg)
        else:
            print(f"→ Using {model_name}" if one_shot else f"✓ Switched to {model_name}")
    
    def show_model_revert_notice(self, model_name: str):
        """Show notice about reverting to original model"""
        if RICH_AVAILABLE:
            self.console.print(f"[dim]Reverted to [cyan]{model_name}[/cyan][/dim]")
        else:
            print(f"← Reverted to {model_name}")
    
    def thinking(self, title: str = "Thinking...") -> ThinkingPanel:
        """Create a thinking panel context manager"""
        return ThinkingPanel(title, self.console)
    
    def status(self, message: str) -> StatusLine:
        """Create a status line context manager"""
        return StatusLine(message, self.console)
    
    def show_user_message(self, message: str, model_override: Optional[str] = None):
        """Display a user message"""
        self.history.append(ChatMessage(role='user', content=message))
        
        if RICH_AVAILABLE:
            self.console.print()
            self.console.print(Rule(style="dim"))
            
            # Show model override if present
            prefix = ""
            if model_override:
                prefix = f"[cyan]@{model_override}[/cyan] "
            
            self.console.print(f"[bold blue]You:[/bold blue] {prefix}{message}")
        else:
            print(f"\nYou: {message}")
    
    def show_response(
        self,
        response: str,
        model_name: Optional[str] = None
    ):
        """Display an AI response with markdown rendering"""
        self.history.append(ChatMessage(
            role='assistant',
            content=response,
            model=model_name
        ))
        
        # Extract code blocks for /copy command
        self._last_code_blocks = self._extract_code_blocks(response)
        
        if not RICH_AVAILABLE:
            print(f"\nStackSense: {response}\n")
            return
        
        self.console.print()
        
        # Model attribution
        model_text = f" [dim]({model_name})[/dim]" if model_name else ""
        self.console.print(f"[bold green]StackSense{model_text}:[/bold green]")
        self.console.print()
        
        # Render markdown
        try:
            md = Markdown(response)
            self.console.print(md, width=min(100, self.console.width - 4))
        except Exception:
            # Fallback to plain text
            self.console.print(response)
        
        # Show copy hint if code blocks found
        if self._last_code_blocks:
            self.console.print()
            self.console.print(f"[dim]💡 Type /copy to copy code ({len(self._last_code_blocks)} block{'s' if len(self._last_code_blocks) > 1 else ''})[/dim]")
        
        self.console.print()
    
    def show_response_streaming(
        self,
        response: str,
        model_name: Optional[str] = None,
        chunk_delay: float = 0.02
    ):
        """
        Display an AI response with LIVE STREAMING - typewriter effect.
        
        Args:
            response: Full response text (can be pre-collected chunks)
            model_name: Model that generated the response
            chunk_delay: Delay between chunks (0.02s = 50 chars/sec feeling)
        """
        import sys
        import time
        
        self.history.append(ChatMessage(
            role='assistant',
            content=response,
            model=model_name
        ))
        
        # Extract code blocks for /copy command
        self._last_code_blocks = self._extract_code_blocks(response)
        
        if not RICH_AVAILABLE:
            print(f"\nStackSense ({model_name}):\n")
            # Simple streaming for non-Rich terminals
            for char in response:
                print(char, end='', flush=True)
                time.sleep(0.01)
            print("\n")
            return
        
        self.console.print()
        
        # Model attribution header
        model_text = f" ({model_name})" if model_name else ""
        self.console.print(f"[bold green]StackSense{model_text}:[/bold green]")
        self.console.print()
        
        # Stream the response with typewriter effect
        # Print raw text live, then render markdown at the end
        for char in response:
            print(char, end='', flush=True)
            if chunk_delay > 0:
                time.sleep(chunk_delay)
        
        print()  # Newline after streaming
        
        # Show copy hint if code blocks found
        if self._last_code_blocks:
            self.console.print()
            self.console.print(f"[dim]💡 Type /copy to copy code ({len(self._last_code_blocks)} block{'s' if len(self._last_code_blocks) > 1 else ''})[/dim]")
        
        self.console.print()
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown text"""
        import re
        # Match ```language ... ``` or just ``` ... ```
        pattern = r'```[\w]*\n?(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [m.strip() for m in matches if m.strip()]
    
    def copy_code(self, block_num: int = 1) -> bool:
        """Copy a code block to clipboard. Returns True on success."""
        if not hasattr(self, '_last_code_blocks') or not self._last_code_blocks:
            self.show_warning("No code blocks in last response")
            return False
        
        if block_num < 1 or block_num > len(self._last_code_blocks):
            self.show_warning(f"Invalid block number. Available: 1-{len(self._last_code_blocks)}")
            return False
        
        code = self._last_code_blocks[block_num - 1]
        
        # Try pyperclip first, then fall back to pbcopy (macOS)
        try:
            import pyperclip
            pyperclip.copy(code)
            self.show_success(f"Copied code block {block_num} to clipboard!")
            return True
        except ImportError:
            pass
        
        # Fallback for macOS
        try:
            import subprocess
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(code.encode('utf-8'))
            if process.returncode == 0:
                self.show_success(f"Copied code block {block_num} to clipboard!")
                return True
        except Exception:
            pass
        
        # Fallback for Linux
        try:
            import subprocess
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(code.encode('utf-8'))
            if process.returncode == 0:
                self.show_success(f"Copied code block {block_num} to clipboard!")
                return True
        except Exception:
            pass
        
        # Show code for manual copy
        self.show_warning("Could not access clipboard. Here's the code:")
        if RICH_AVAILABLE:
            from rich.syntax import Syntax
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
            self.console.print(syntax)
        else:
            print(code)
        return False
    
    def show_error(self, message: str):
        """Display an error message"""
        if RICH_AVAILABLE:
            self.console.print(f"[bold red]❌ {message}[/bold red]")
        else:
            print(f"❌ {message}")
    
    def show_warning(self, message: str):
        """Display a warning message"""
        if RICH_AVAILABLE:
            self.console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")
        else:
            print(f"⚠️  {message}")
    
    def show_success(self, message: str):
        """Display a success message"""
        if RICH_AVAILABLE:
            self.console.print(f"[bold green]✅ {message}[/bold green]")
        else:
            print(f"✅ {message}")
    
    def show_info(self, message: str):
        """Display an info message"""
        if RICH_AVAILABLE:
            self.console.print(f"[cyan]{message}[/cyan]")
        else:
            print(f"ℹ️  {message}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_available_models(self, models: List[str], current_model: str) -> Optional[str]:
        """
        Display available models and let user select one.
        
        Returns selected model name or None if cancelled.
        """
        if not RICH_AVAILABLE:
            print("\n📦 Available Models:")
            for i, model in enumerate(models, 1):
                status = " (current)" if model == current_model else ""
                print(f"  {i}. {model}{status}")
            print("  0. Cancel")
            
            try:
                choice = input(f"\nSelect [0-{len(models)}]: ").strip()
                if choice == '0' or choice.lower() == 'cancel':
                    return None
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    return models[idx]
            except (ValueError, KeyboardInterrupt):
                pass
            return None
        
        # Rich table
        table = Table(title="📦 Available Models", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=3)
        table.add_column("Model", style="bold")
        table.add_column("Status", style="green")
        
        for i, model in enumerate(models, 1):
            status = "✓ current" if model == current_model else ""
            table.add_row(str(i), model, status)
        
        self.console.print()
        self.console.print(table)
        
        try:
            choice = Prompt.ask(f"\nSelect model [1-{len(models)}] or 'cancel'")
            if choice.lower() == 'cancel':
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]
        except (ValueError, KeyboardInterrupt):
            pass
        
        return None


# Convenience functions
def create_ui(debug: bool = False) -> RichChatUI:
    """Create a RichChatUI instance"""
    return RichChatUI(debug=debug)

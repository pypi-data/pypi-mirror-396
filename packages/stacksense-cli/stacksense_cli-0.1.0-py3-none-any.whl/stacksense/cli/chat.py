"""
StackSense Interactive Chat Interface
Provides a conversational AI assistant for developers

Features:
- Collapsible thinking panels (Claude/Antigravity style)
- model:name one-shot switching
- /(free)model and /(paid)model permanent switching
- Rich markdown rendering
"""
import os
import sys
import uuid
import json
import asyncio
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

# Import Rich Chat UI
try:
    from .rich_chat import RichChatUI, ThinkingPanel, StatusLine, create_ui
    RICH_UI_AVAILABLE = True
except ImportError:
    RICH_UI_AVAILABLE = False


class StackSenseChat:
    """
    Interactive chat interface for StackSense AI assistant.
    
    Features:
    - Collapsible thinking panels
    - model:name one-shot switching (use different model for one query)
    - /(free)model and /(paid)model permanent switching
    - Rich markdown rendering
    """
    
    def __init__(self, model_type: Optional[str] = None, debug: bool = False):
        """
        Initialize StackSense chat.
        
        Args:
            model_type: 'openrouter' or 'heuristic'
            debug: Enable debug logging
        """
        self.session_id = str(uuid.uuid4())[:8]
        self.debug = debug
        self.model_type = model_type or self._detect_configured_model()
        self.model = None
        self.actual_model_name = None  # Will be set when model loads
        self.keep_alive_thread = None  # Background thread for model warmth
        
        # Workspace selection
        self.workspace_path = None  # Will be set by _select_workspace
        
        self.workspace_cache_path = f"/tmp/stacksense_workspace_{self.session_id}.json"
        self.search_cache_path = f"/tmp/stacksense_search_{self.session_id}.json"
        
        # Chat state
        self.running = False
        self.workspace_scanned = False
        
        # Diagram-based system
        self.orchestrator = None
        
        # Rich UI (NEW)
        self.ui = create_ui(debug=debug) if RICH_UI_AVAILABLE else None
        
    def _detect_configured_model(self) -> str:
        """Detect which AI model is configured"""
        try:
            from . import config_manager
            # Check the correct preference key
            ai_model = config_manager.get_preference('default_ai_model', None)
            
            # Default to openrouter if not set
            if ai_model is None:
                # OpenRouter is the new default - no setup needed
                return 'openrouter'
            
            # Accept openrouter or heuristic
            if ai_model not in ['openrouter', 'heuristic']:
                # Fallback to openrouter
                return 'openrouter'
            
            return ai_model
        except Exception as e:
            # Default to openrouter
            return 'openrouter'
    
    def _select_workspace(self):
        """Interactive workspace selection - simplified Y/n"""
        cwd = os.getcwd()
        
        # Check if current directory is a repo
        if os.path.exists(os.path.join(cwd, '.git')):
            repo_name = os.path.basename(cwd)
            print(f"\n📂 Detected repository: {repo_name}")
            choice = input("Use this repo for context? [Y/n]: ").strip().lower()
            
            if choice in ['', 'y', 'yes']:
                self.workspace_path = cwd
                print(f"✅ Using: {repo_name}\n")
                return
        
        # Check if in a parent directory with repos (like ~/Documents/GitHub/AI)
        if self._has_child_repos(cwd):
            parent_name = os.path.basename(cwd)
            print(f"\n📂 Detected workspace: {parent_name}")
            choice = input("Use this workspace for context? [Y/n]: ").strip().lower()
            
            if choice in ['', 'y', 'yes']:
                self.workspace_path = cwd
                print(f"✅ Using: {parent_name}\n")
                return
        
        # Not in a repo/workspace
        print("\n✅ Chatting without repo context (general AI chat)\n")
        self.workspace_path = None
    
    def _has_child_repos(self, directory: str) -> bool:
        """Check if directory contains git repos"""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '.git')):
                    return True
            return False
        except:
            return False
    
    def _initialize_diagram_system(self):
        """Initialize diagram-based orchestrator and show codebase overview"""
        if not self.workspace_path:
            return  # No workspace, skip diagram
        
        print("\n🔍 Analyzing workspace structure...")
        
        try:
            from stacksense.cli.terminal_ui import (
                show_codebase_overview, detect_repo_info,
                show_diagram_summary, show_workspace_header
            )
            from pathlib import Path
            
            workspace_path = Path(self.workspace_path)
            workspace_name = workspace_path.name
            
            # Detect tech stack for display in panel
            tech_stack = None
            try:
                from stacksense.core.framework_detector import get_tech_stack_display
                tech_stack = get_tech_stack_display(str(workspace_path))
            except Exception:
                pass  # Silently skip if detection fails
            
            # Detect repos in workspace
            repos_info = []
            
            # Check if this IS a repo (single repo mode)
            if (workspace_path / '.git').exists():
                # Single repo - just show this one
                repo_info = detect_repo_info(str(workspace_path))
                repos_info.append(repo_info)
            else:
                # Multi-repo workspace - scan child directories
                for item in workspace_path.iterdir():
                    if item.is_dir() and (item / '.git').exists():
                        repo_info = detect_repo_info(str(item))
                        repos_info.append(repo_info)
            
            # Show the codebase overview panel (with tech stack inside)
            if repos_info:
                show_codebase_overview(repos_info, workspace_name, tech_stack)
            
            # Now try to initialize the diagram orchestrator
            from stacksense.core.diagram_orchestrator import DiagramBasedOrchestrator
            from stacksense.core.openrouter_client import get_client
            
            # OpenRouter wrapper for diagram generation
            class OpenRouterWrapper:
                def __init__(self, model_name: str = None):
                    self.client = get_client()
                    self.model_name = model_name or "meta-llama/llama-3.3-70b-instruct:free"
                
                def generate(self, prompt, max_tokens=2000):
                    """Generate using OpenRouter API"""
                    try:
                        return self.client.chat(
                            model=self.model_name,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=max_tokens
                        )
                    except Exception as e:
                        return f"Error: {e}"
                
                def warm_up(self):
                    """No warm-up needed for OpenRouter (already warm!)"""
                    pass
                
                def keep_alive_ping(self):
                    """No keep-alive needed for OpenRouter"""
                    pass
            
            wrapped_model = OpenRouterWrapper(self.actual_model_name)
            
            # Determine model size based on context length
            model_size = 'large'  # OpenRouter models are generally well-sized
            
            self.orchestrator = DiagramBasedOrchestrator(
                workspace_path=Path(self.workspace_path),
                model=wrapped_model,
                model_size=model_size,
                debug=False
            )
            
            # ALWAYS call initialize() - it handles caching internally!
            # The orchestrator checks for cached diagrams and loads them if < 24h old
            # This sets workspace_structure, diagrams, grep_searcher, etc.
            self.orchestrator.initialize()
            
            # Warm up the model NOW (during diagram display) so first query is instant
            # This runs while user reads the codebase overview
            wrapped_model.warm_up()
            
            # Start background keep-alive thread (pings every 25 min to maintain 30 min warmth)
            self._start_keep_alive_thread()
            
            self.workspace_scanned = True  # Mark as scanned
            
        except Exception as e:
            print(f"⚠️  Diagram system unavailable: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            # Continue without diagram system
    
    def _start_keep_alive_thread(self):
        """
        Start background thread that pings model every 25 minutes.
        This keeps the model warm for 30 minutes (with 5 min buffer).
        
        The ping sends a tiny request with keep_alive='30m' to refresh the timer.
        """
        import threading
        import requests
        import time
        
        def keep_alive_loop():
            PING_INTERVAL = 25 * 60  # 25 minutes in seconds
            
            while self.running:
                # Sleep first (model was just warmed up at start)
                for _ in range(PING_INTERVAL):
                    if not self.running:
                        return
                    time.sleep(1)
                
                # Send keep-alive ping
                try:
                    model_name = self.actual_model_name or 'phi3:mini'
                    requests.post(
                        'http://localhost:11434/api/generate',
                        json={
                            'model': model_name,
                            'prompt': 'ping',
                            'stream': False,
                            'keep_alive': '30m',
                            'options': {'num_predict': 1}
                        },
                        timeout=30
                    )
                    if self.debug:
                        print(f"[KeepAlive] Pinged {model_name}")
                except Exception as e:
                    if self.debug:
                        print(f"[KeepAlive] Ping failed: {e}")
        
        # Start daemon thread (will auto-stop when main program exits)
        self.keep_alive_thread = threading.Thread(target=keep_alive_loop, daemon=True)
        self.keep_alive_thread.start()
        
        if self.debug:
            print("[KeepAlive] Background thread started (pings every 25 min)")
    
    def _get_model_size(self) -> str:
        """
        Determine model size dynamically using actual GB from Ollama API.
        This works for any model on any device - no hardcoding needed.
        """
        model_name = getattr(self.model, 'model_name', '')
        
        # Query Ollama for actual model size
        try:
            import requests
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                
                for model in models:
                    if model.get('name', '').startswith(model_name.split(':')[0]):
                        size_bytes = model.get('size', 0)
                        size_gb = size_bytes / (1024 ** 3)
                        
                        # Categorize by actual GB
                        if size_gb < 2:
                            return 'tiny'    # phi3:mini, granite:2b (< 2GB)
                        elif size_gb < 4:
                            return 'small'   # 2-4GB models
                        elif size_gb < 8:
                            return 'medium'  # 4-8GB models (most 7B quants)
                        else:
                            return 'large'   # 8GB+ models (13B, 70B)
        except:
            pass
        
        # Fallback: estimate from model name patterns
        model_lower = model_name.lower()
        
        # Parse parameter count from name (e.g., "7b", "13b", "70b")
        import re
        param_match = re.search(r'(\d+)b', model_lower)
        if param_match:
            params = int(param_match.group(1))
            if params <= 3:
                return 'small'
            elif params <= 9:
                return 'medium'
            else:
                return 'large'
        
        # Known small models
        if any(x in model_lower for x in ['mini', 'tiny', 'small', '2b', '3b']):
            return 'small'
        
        # Default to medium (safe assumption)
        return 'medium'
    
    def _browse_repos(self):
        """Browse and select from available repos"""
        try:
            from . import config_manager
            
            repos_dir = config_manager.get_preference('repos_directory', os.path.expanduser('~/Documents/GitHub'))
            
            # Manual repo scanning (standalone)
            print(f"\n🔍 Scanning for repos in {repos_dir}...")
            repos = []
            if os.path.exists(repos_dir):
                for item in os.listdir(repos_dir):
                    item_path = os.path.join(repos_dir, item)
                    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '.git')):
                        repos.append(item_path)
            
            if not repos:
                print("❌ No repos found")
                print("✅ Chatting without repo context\n")
                self.workspace_path = None
                return
            
            print(f"\nFound {len(repos)} repositories:")
            for i, repo in enumerate(repos[:20], 1):  # Show max 20
                repo_name = os.path.basename(repo)
                print(f"  {i}. {repo_name}")
            
            if len(repos) > 20:
                print(f"  ... and {len(repos) - 20} more")
            
            print("  0. Chat without repo context")
            
            choice = input(f"\nSelect repo [0-{min(len(repos), 20)}]: ").strip()
            
            try:
                idx = int(choice)
                if idx == 0:
                    print("✅ Chatting without repo context\n")
                    self.workspace_path = None
                elif 1 <= idx <= min(len(repos), 20):
                    selected = repos[idx - 1]
                    repo_name = os.path.basename(selected)
                    self.workspace_path = selected
                    print(f"✅ Selected: {repo_name}\n")
                else:
                    print("Invalid selection, using no repo context\n")
                    self.workspace_path = None
            except ValueError:
                print("Invalid input, using no repo context\n")
                self.workspace_path = None
                
        except Exception as e:
            if self.debug:
                print(f"[Debug] Browse failed: {e}")
            print("⚠️  Failed to browse repos, using no repo context\n")
            self.workspace_path = None
    
    def _get_input(self, prompt_text: str = "You: ") -> str:
        """
        Get user input with multi-line support and autocomplete.
        
        Autocomplete:
            @              -> File autocomplete (5-6 relevant files)
            model:         -> Model autocomplete (one-shot switch)
            /(free)model   -> Free model autocomplete (permanent switch)
            /(paid)model   -> Paid model autocomplete (permanent switch)
        
        Submit:
            Mac: Cmd+Enter (or Esc+Enter)
            Windows/Linux: Alt+Enter (or Esc+Enter)
            Enter alone: New line
        """
        if PROMPT_TOOLKIT_AVAILABLE:
            try:
                from prompt_toolkit import PromptSession
                from prompt_toolkit.key_binding import KeyBindings  
                from prompt_toolkit.keys import Keys
                from prompt_toolkit.shortcuts import CompleteStyle
                from .completer import StackSenseCompleter
                import platform
                # Key bindings: Enter submits, Shift+Enter for new line
                bindings = KeyBindings()
                
                # Shift+Enter = insert newline (MUST be registered BEFORE Enter)
                @bindings.add('s-enter')  # This is the correct way to bind Shift+Enter
                def newline(event):
                    """Insert newline on Shift+Enter"""
                    event.current_buffer.insert_text('\n')
                
                # Enter = submit
                @bindings.add(Keys.Enter)
                def submit(event):
                    """Submit on Enter"""
                    event.current_buffer.validate_and_handle()
                
                # Esc+Enter = also submit (alternative)
                @bindings.add(Keys.Escape, Keys.Enter)
                def submit_esc(event):
                    """Also submit on Esc+Enter"""
                    event.current_buffer.validate_and_handle()
                
                # Auto-trigger completion menu on @ (files) and : (after model)
                @bindings.add('@')
                def trigger_at_completion(event):
                    """Type @ and immediately show file completions"""
                    event.current_buffer.insert_text('@')
                    # Force start completion
                    event.current_buffer.start_completion(select_first=False)
                
                @bindings.add(':')
                def trigger_colon_completion(event):
                    """Type : and show model completions if preceded by 'model'"""
                    text = event.current_buffer.text
                    event.current_buffer.insert_text(':')
                    # If this completes "model:", trigger completion
                    if text.lower().endswith('model'):
                        event.current_buffer.start_completion(select_first=False)
                
                @bindings.add(' ')
                def trigger_space_completion(event):
                    """Type space and show model completions after /(free)model or /(paid)model"""
                    text = event.current_buffer.text
                    event.current_buffer.insert_text(' ')
                    # If this follows "/(free)model" or "/(paid)model", trigger completion
                    stripped = text.lower().strip()
                    if stripped == '/(free)model' or stripped == '/(paid)model':
                        event.current_buffer.start_completion(select_first=False)
                
                # Create completer with workspace context
                memory_path = None
                if self.workspace_path:
                    memory_path = os.path.join(self.workspace_path, '.stacksense', 'ai_memory.json')
                
                completer = StackSenseCompleter(
                    workspace_path=self.workspace_path,
                    memory_path=memory_path
                )
                
                # Create session with multiline, keybindings, AND autocomplete
                # complete_while_typing=True shows menu as you type
                # complete_in_thread=True keeps UI responsive during completion
                # complete_style=MULTI_COLUMN shows the custom display text properly
                session = PromptSession(
                    multiline=True,
                    key_bindings=bindings,
                    completer=completer,
                    complete_while_typing=True,
                    complete_in_thread=True,
                    complete_style=CompleteStyle.MULTI_COLUMN,
                    prompt_continuation='  >> '
                )
                
                user_input = session.prompt(prompt_text)
                return user_input.strip()
            
            except (EOFError, KeyboardInterrupt):
                raise
            except Exception as e:
                if self.debug:
                    print(f"[Debug] prompt_toolkit failed: {e}")
                # Fall through
        
        # Fallback
        lines = []
        line = input(prompt_text).strip()
        
        if not line:
            return ""
        
        lines.append(line)
        
        while line.endswith('\\'):
            line = line[:-1]
            lines[-1] = line
            line = input("  >> ").strip()
            if line:
                lines.append(line)
            else:
                break
        
        return '\n'.join(lines)
    
    def _print_banner(self):
        """Display StackSense welcome banner using Rich UI"""
        workspace = os.path.basename(self.workspace_path) if self.workspace_path else None
        
        # Detect tech stack for enhanced display
        tech_stack = None
        if self.workspace_path:
            try:
                from ..core.framework_detector import get_tech_stack_display
                tech_stack = get_tech_stack_display(self.workspace_path)
            except Exception:
                pass  # Silently skip if detection fails
        
        if self.ui:
            self.ui.show_banner(
                model_name=self.actual_model_name or self.model_type,
                session_id=self.session_id,
                workspace=workspace,
                tech_stack=tech_stack
            )
        else:
            # Fallback for no Rich UI
            model_display = {
                'openrouter': 'OpenRouter',
                'heuristic': 'Heuristic Coach'
            }
            model_name = model_display.get(self.model_type, 'OpenRouter')
            if self.actual_model_name:
                model_name = f"{model_name} ({self.actual_model_name})"
            
            print("\n" + "=" * 60)
            print("🧠 StackSense - AI Dev Assistant")
            print("=" * 60)
            print(f"Model: {model_name} | Session: {self.session_id}")
            if workspace:
                print(f"📂 Workspace: {workspace}")
            if tech_stack and tech_stack != "Unknown":
                print(f"🔧 Tech Stack: {tech_stack}")
            print("Commands: /help /(free)model /(paid)model /clear /status exit")
            print("Model switch: model:name query (one-shot) | /(free)model or /(paid)model (permanent)")
            print("=" * 60)
            print()
    
    def _print_help(self):
        """Display help information using Rich UI"""
        if self.ui:
            self.ui.show_help()
        else:
            print("""
📖 StackSense Commands:

  exit, quit, q       - Exit StackSense
  /help               - Show this help
  /clear              - Clear terminal
  /status             - Show session status
  /(free)model [name] - Switch to free model
  /(paid)model [name] - Switch to paid model

📍 Model Switching:

  model:name query    - Use model for ONE query, then revert
  /(free)model name   - Switch to free model permanently
  /(paid)model name   - Switch to paid model permanently
            """)
    
    def _cleanup(self):
        """Clean up session resources and unload model to free memory"""
        if self.debug:
            print(f"\n[Debug] Cleaning up session {self.session_id}")
        
        # Stop the keep-alive thread
        self.running = False
        
        # Unload model to free memory (session-based keep-alive)
        if self.actual_model_name:
            try:
                import requests
                # Setting keep_alive to 0 unloads the model immediately
                requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': self.actual_model_name,
                        'prompt': '',
                        'keep_alive': '0'
                    },
                    timeout=5
                )
                if self.debug:
                    print(f"[Debug] Unloaded model {self.actual_model_name}")
            except Exception as e:
                if self.debug:
                    print(f"[Debug] Model unload failed: {e}")
        
        # Delete cache files
        for cache_path in [self.workspace_cache_path, self.search_cache_path]:
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    if self.debug:
                        print(f"[Debug] Deleted {cache_path}")
                except Exception as e:
                    if self.debug:
                        print(f"[Debug] Failed to delete {cache_path}: {e}")
    
    async def _load_model(self):
        """Load the appropriate AI model - OpenRouter by default, with persistence"""
        if self.debug:
            print(f"[Debug] Loading model: {self.model_type}")
        
        # OpenRouter is the default - no model object needed (uses API directly)
        if self.model_type in ['openrouter', 'ollama']:
            # Check for saved model preference first
            saved_model = self._load_model_preference()
            self.actual_model_name = saved_model or "nvidia/nemotron-nano-9b-v2:free"
            self.model_type = 'openrouter'  # Force openrouter
            
            # Simple model wrapper for compatibility
            class OpenRouterModel:
                def __init__(self, model_id):
                    self.model_name = model_id
            
            self.model = OpenRouterModel(self.actual_model_name)
        
        elif self.model_type == 'heuristic':
            from stacksense.models.heuristic_chat import HeuristicChatModel
            self.model = HeuristicChatModel({})
            self.actual_model_name = "heuristic"
        
        if self.debug:
            print(f"[Debug] Model loaded: {self.actual_model_name}")
    
    def _load_model_preference(self) -> str:
        """Load saved model preference from config"""
        try:
            import json
            from pathlib import Path
            config_path = Path.home() / ".stacksense" / "model_preference.json"
            if config_path.exists():
                with open(config_path) as f:
                    data = json.load(f)
                    return data.get("model", "")
        except Exception:
            pass
        return ""
    
    def _save_model_preference(self, model_id: str):
        """Save model preference to config"""
        try:
            import json
            from pathlib import Path
            config_dir = Path.home() / ".stacksense"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "model_preference.json"
            with open(config_path, 'w') as f:
                json.dump({"model": model_id}, f)
        except Exception:
            pass
    
    async def _process_message(self, user_message: str, file_context: dict = None) -> str:
        """
        Process user message and generate response.
        
        Args:
            user_message: The user's input
            file_context: Optional dict of attached file contents
            
        Returns:
            AI response
        """
        # Check usage limits before processing
        try:
            from stacksense.license import check_limit
            allowed, warning = check_limit("chat")
            
            if warning:
                print(f"\n{warning}\n")
            
            if not allowed:
                return "Your usage limit has been reached. Please upgrade your plan at stacksense.dev/upgrade or wait for your limit to reset."
        except ImportError:
            # License module not available, continue without checking
            pass
        except Exception as e:
            if self.debug:
                print(f"[Debug] Usage check error: {e}")
        # NEW: Try diagram-based query first
        if self.orchestrator:
            try:
                import time
                start_time = time.time()
                
                result = self.orchestrator.query(user_message)
                elapsed_ms = int((time.time() - start_time) * 1000)
                
                # Only show stats in debug mode
                if self.debug:
                    from stacksense.cli.terminal_ui import show_query_stats
                    show_query_stats(
                        result.get('keywords_used', []),
                        result.get('files_searched', 0),
                        result.get('slices_extracted', 0),
                        elapsed_ms
                    )
                
                # Return the answer directly (markdown already formatted in result)
                answer = result.get('answer', 'No answer generated')
                return answer  # Return it so chat.py can print it
                
            except Exception as e:
                if self.debug:
                    from stacksense.cli.terminal_ui import show_error
                    show_error(f"Diagram query failed: {e}")
                    print(f"[Debug] Falling back to regular flow")
                # Fall through to regular flow
        
        # Build context (repo scan + web search)
        context = {}
        
        # Determine if we need repo scan or web search
        # Pass empty context initially - these methods may accept (query) or (query, context)
        try:
            should_scan = self.model.should_scan_repo(user_message, context)
        except TypeError:
            should_scan = self.model.should_scan_repo(user_message) if hasattr(self.model, 'should_scan_repo') else True
        
        try:
            should_search = self.model.should_search_web(user_message, context)
        except TypeError:
            should_search = self.model.should_search_web(user_message) if hasattr(self.model, 'should_search_web') else False
        
        # Repo scan
        if should_scan and not self.workspace_scanned:
            if not self.workspace_path:
                # No workspace selected, skip scan
                if self.debug:
                    print("[Debug] No workspace selected, skipping scan")
            else:
                # Use Rich status for proper live updates (not basic Spinner which conflicts with Rich)
                from rich.console import Console
                console = Console()
                
                # Scan repository with lightest model for speed
                with console.status("[bold cyan]📂 Analyzing workspace...[/bold cyan]", spinner="dots"):
                    try:
                        from stacksense.core.repo_scanner import RepoScanner
                        
                        # Use lightweight model for scanning
                        scan_model = self.model.get_scan_model() if hasattr(self.model, 'get_scan_model') else None
                        
                        scanner = RepoScanner(
                            workspace_path=self.workspace_path,
                            debug=False, # RepoScanner has its own debug, keep it quiet by default
                            scan_model=scan_model  # Pass lightest model for fast scanning
                        )
                        context_map = await scanner.scan()
                        context['repo'] = {
                            'context_map': context_map,
                            'scanner': scanner  # Keep scanner for finding relevant slices
                        }
                        self.workspace_scanned = True
                        
                        if context_map:
                            files_scanned = context_map.get('total_files', 0)
                            languages = ', '.join(list(context_map.get('languages', {}).keys())[:3])
                            console.print(f"✅ Scanned {files_scanned} files ({languages})")
                            
                            # Show code structure sample
                            if scanner and hasattr(scanner, 'slices') and scanner.slices:
                                console.print(f"   Found {len(scanner.slices)} code slices")
                    except Exception as e:
                        if self.debug:
                            print(f"[Debug] Repo scan failed: {e}")
        
        # Web search with fallback
        if should_search:
            print("🔍 Searching the web...")
            print("   Querying: StackOverflow, GitHub, Reddit, MDN")
            try:
                from stacksense.core.web_searcher import WebSearcher
                searcher = WebSearcher(
                    cache_path=self.search_cache_path,
                    debug=True,  # Enable debug to show results as they arrive
                    timeout=15.0
                )
                search_results = await searcher.search(user_message)
                context['web'] = {
                    'results': search_results,
                    'count': len(search_results)
                }
                
                if search_results:
                    sources = ', '.join(sorted(set(r.source for r in search_results)))
                    print(f"✅ Found {len(search_results)} results from: {sources}")
                else:
                    print("⚠️  No web results found (continuing without web context)")
            except Exception as e:
                if self.debug:
                    print(f"[Debug] Web search failed: {e}")
                print("⚠️  Web search unavailable (continuing with local knowledge)")
                # Continue without web context
                context['web'] = {'results': [], 'count': 0, 'error': str(e)}
        
        
        # Generate response with Rich status (not basic Spinner which prints new lines)
        from rich.console import Console
        console = Console()
        
        with console.status("[bold cyan]🤖 Thinking...[/bold cyan]", spinner="dots"):
            if self.debug:
                print(f"\n   Context size: {len(str(context))} chars")
                if 'repo' in context:
                    print(f"   Repo context: YES")
                if 'web' in context and context['web'].get('results'):
                    print(f"   Web results: {len(context['web']['results'])} sources")
            
            # Generate response
            response = await self.model.generate_response(user_message, context)
        
        return response
    
    def _handle_model_switch(self, filter_type: str = 'all'):
        """
        Handle model switching mid-chat.
        
        Args:
            filter_type: 'all' (default), 'free', or 'paid'
        """
        try:
            from stacksense.core.openrouter_client import get_client
            from stacksense.cli.terminal_ui import console
            from rich.table import Table
            
            client = get_client()
            
            filter_label = {'all': 'All', 'free': 'Free', 'paid': 'Paid'}.get(filter_type, 'All')
            print(f"\n🔄 Fetching {filter_label.lower()} models...")
            models = client.get_models(filter_type=filter_type)
            
            if not models:
                print(f"❌ No {filter_label.lower()} models found. Check your API key.")
                return
            
            # Show available models with FREE/PAID marker
            table = Table(title=f"🌐 {filter_label} Models", show_header=True)
            table.add_column("#", style="cyan")
            table.add_column("Model", style="bold")
            table.add_column("Type", style="dim")
            table.add_column("Context", style="dim")
            table.add_column("Status", style="green")
            
            for i, model in enumerate(models[:15], 1):  # Show top 15
                display_name = model.display_name
                model_type = "[green]FREE[/green]" if model.is_free else "[yellow]PAID[/yellow]"
                ctx_len = f"{model.context_length // 1000}K"
                status = "✓ Current" if model.id == self.actual_model_name else ""
                table.add_row(str(i), display_name, model_type, ctx_len, status)
            
            console.print()
            console.print(table)
            console.print()
            
            if len(models) > 15:
                console.print(f"[dim](Showing 15 of {len(models)} models)[/dim]\n")
            
            # Get user choice
            choice = input(f"Select model [1-{min(len(models), 15)}] or 'cancel': ").strip()
            
            if choice.lower() == 'cancel':
                print("✅ Keeping current model\n")
                return
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < min(len(models), 15):
                    selected = models[idx]
                    
                    if selected.id == self.actual_model_name:
                        print(f"\n✅ Already using {selected.display_name}\n")
                        return
                    
                    # Switch model
                    self.actual_model_name = selected.id
                    self._save_model_preference(selected.id)
                    
                    type_marker = "FREE" if selected.is_free else "PAID"
                    print(f"✅ Switched to {selected.display_name} ({type_marker})")
                    print(f"💡 Context: {selected.context_length // 1000}K tokens\n")
                else:
                    print("❌ Invalid choice\n")
            except ValueError:
                print("❌ Please enter a number\n")
                
        except Exception as e:
            print(f"❌ Error: {e}\n")
            if self.debug:
                import traceback
                traceback.print_exc()
    
    def run(self):
        """Start the interactive chat loop with Rich UI"""
        self.running = True
        
        # Show ASCII logo FIRST (centered, full width)
        from rich.console import Console
        from rich.align import Align
        from rich.text import Text
        console = Console()
        
        # Large centered ASCII logo
        logo_text = """
╔═╗╔╦╗╔═╗╔═╗╦╔═╔═╗╔═╗╔╗╔╔═╗╔═╗
╚═╗ ║ ╠═╣║  ╠╩╗╚═╗║╣ ║║║╚═╗║╣ 
╚═╝ ╩ ╩ ╩╚═╝╩ ╩╚═╝╚═╝╝╚╝╚═╝╚═╝"""
        
        logo = Text(logo_text, style="bold magenta")
        console.print(Align.center(logo))
        console.print()  # Spacing
        
        # Select workspace first
        self._select_workspace()
        
        # Load model (to get actual model name)
        asyncio.run(self._load_model())
        
        # Initialize diagram system
        self._initialize_diagram_system()
        
        # Show banner with model name
        self._print_banner()
        
        # Show initial context bar (0% used)
        if self.ui:
            self.ui.show_context_bar()
        
        while self.running:
            try:
                # Get user input
                if self.ui:
                    user_input = self.ui.get_input("You", workspace_path=str(self.workspace_path) if self.workspace_path else None)
                else:
                    user_input = self._get_input("You: ")
                
                # Skip empty inputs
                if not user_input or not user_input.strip():
                    continue
                
                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    if self.ui:
                        self.ui.show_success("Goodbye! Session cleaned up.")
                    else:
                        print("\n👋 Goodbye! Session cleaned up.")
                    break
                
                # Handle /help
                if user_input.lower() in ['help', '/help']:
                    self._print_help()
                    continue
                
                # Handle /clear
                if user_input.lower() in ['clear', '/clear']:
                    if self.ui:
                        self.ui.clear_screen()
                    else:
                        os.system('clear' if os.name == 'posix' else 'cls')
                    self._print_banner()
                    continue
                
                # Handle /copy - copy code from last response
                if user_input.lower().startswith('/copy'):
                    if self.ui:
                        # Parse optional block number: /copy or /copy 2
                        parts = user_input.split()
                        block_num = 1
                        if len(parts) > 1:
                            try:
                                block_num = int(parts[1])
                            except ValueError:
                                pass
                        self.ui.copy_code(block_num)
                    else:
                        print("Copy feature requires Rich UI")
                    continue
                
                # Handle /status
                if user_input.lower() in ['status', '/status']:
                    if self.ui:
                        self.ui.show_status(
                            session_id=self.session_id,
                            model_type=self.model_type,
                            model_name=self.actual_model_name or "unknown",
                            workspace_scanned=self.workspace_scanned,
                            orchestrator_active=self.orchestrator is not None
                        )
                    else:
                        print(f"\nSession: {self.session_id}")
                        print(f"Model: {self.model_type} ({self.actual_model_name})")
                        print(f"Workspace scanned: {self.workspace_scanned}")
                        print(f"Diagram system: {'Active' if self.orchestrator else 'Inactive'}\n")
                    continue
                
                # Handle /(free)model - permanent switch (free models only)
                if user_input.startswith('/(free)model'):
                    # Extract model name (after the command, with or without space)
                    model_name = user_input[12:].strip()  # len('/(free)model') = 12
                    if model_name:
                        # Direct switch to named model
                        parts = model_name.split(maxsplit=1)
                        self._switch_model_to(parts[0], permanent=True)
                    else:
                        # Show free models picker
                        self._handle_model_switch(filter_type='free')
                    continue
                
                # Handle /(paid)model - permanent switch (paid models only)
                if user_input.startswith('/(paid)model'):
                    # Extract model name (after the command, with or without space)
                    model_name = user_input[12:].strip()  # len('/(paid)model') = 12
                    if model_name:
                        # Direct switch to named model
                        parts = model_name.split(maxsplit=1)
                        self._switch_model_to(parts[0], permanent=True)
                    else:
                        # Show paid models picker
                        self._handle_model_switch(filter_type='paid')
                    continue
                
                # Check for search:query - web search command
                if user_input.startswith("search:"):
                    search_query = user_input[7:].strip()  # Remove "search:"
                    if search_query:
                        try:
                            from ddgs import DDGS
                            from stacksense.core.rate_limiter import check_rate_limit
                            
                            # Rate limit: 10 searches per minute
                            check_rate_limit('web_search')
                            
                            if self.ui:
                                self.ui.console.print(f"[cyan]🔍 Searching: {search_query}[/cyan]")
                                self.ui.console.print("[dim]   Querying: DuckDuckGo (general web search)[/dim]")
                            else:
                                print(f"🔍 Searching: {search_query}")
                                print("   Querying: DuckDuckGo (general web search)")
                            
                            # Use DuckDuckGo for general web search
                            with DDGS() as ddgs:
                                results = list(ddgs.text(search_query, max_results=5))
                            
                            if results:
                                # Format results as rich panels
                                if self.ui:
                                    from rich.panel import Panel
                                    from rich.markdown import Markdown
                                    from urllib.parse import urlparse
                                    
                                    console = self.ui.console
                                    console.print()
                                    console.print(f"[bold cyan]🌐 Search Results for:[/bold cyan] [yellow]{search_query}[/yellow]")
                                    console.print()
                                    
                                    for i, r in enumerate(results, 1):
                                        # DuckDuckGo returns dict with 'title', 'body', 'href'
                                        title = r.get('title', 'No title')
                                        body = r.get('body', '')
                                        url = r.get('href', '')
                                        
                                        # Determine color based on domain
                                        domain = urlparse(url).netloc if url else ''
                                        if 'stackoverflow' in domain:
                                            color, source = 'orange1', '📚 StackOverflow'
                                        elif 'github' in domain:
                                            color, source = 'bright_white', '🐙 GitHub'
                                        elif 'reddit' in domain:
                                            color, source = 'red', '💬 Reddit'
                                        elif 'wikipedia' in domain:
                                            color, source = 'blue', '📖 Wikipedia'
                                        else:
                                            color, source = 'green', f'🌐 {domain[:30]}'
                                        
                                        # Print each result as a panel
                                        console.print(Panel(
                                            f"[bold]{title}[/bold]\n\n"
                                            f"[dim]{body[:300]}{'...' if len(body) > 300 else ''}[/dim]\n\n"
                                            f"[link={url}]{url}[/link]",
                                            title=f"[{color}]{source}[/{color}]",
                                            border_style=color,
                                            padding=(0, 1)
                                        ))
                                else:
                                    output_lines = [f"\n🌐 Search Results for: {search_query}\n"]
                                    for i, r in enumerate(results, 1):
                                        output_lines.append(f"{i}. {r.get('title', 'No title')}")
                                        output_lines.append(f"   {r.get('href', '')}")
                                        output_lines.append(f"   {r.get('body', '')[:200]}...")
                                        output_lines.append("")
                                    print("\n".join(output_lines))
                            else:
                                if self.ui:
                                    self.ui.show_warning(f"No results found for: {search_query}")
                                else:
                                    print(f"No results found for: {search_query}")
                                    
                        except ImportError as e:
                            if self.ui:
                                self.ui.show_error(f"Web search module not found: {e}")
                            else:
                                print(f"❌ Web search module not found: {e}")
                        except Exception as e:
                            if self.ui:
                                self.ui.show_error(f"Search failed: {e}")
                            else:
                                print(f"❌ Search failed: {e}")
                    else:
                        if self.ui:
                            self.ui.show_warning("Usage: search:your query here")
                        else:
                            print("Usage: search:your query here")
                    continue
                
                # Check for model:name one-shot switching
                one_shot_model = None
                original_model = None
                original_model_obj = None
                query = user_input
                
                if self.ui:
                    one_shot_model, query = self.ui.parse_model_switch(user_input)
                else:
                    # Manual parse: model:name query
                    import re
                    match = re.match(r'^model:(\S+)\s+(.+)$', user_input, re.DOTALL)
                    if match:
                        one_shot_model = match.group(1)
                        query = match.group(2)
                
                # If one-shot model specified, temporarily switch
                if one_shot_model:
                    original_model = self.actual_model_name
                    original_model_obj = self.model
                    
                    if self.ui:
                        self.ui.show_model_switch_notice(one_shot_model, one_shot=True)
                    else:
                        print(f"→ Using {one_shot_model} for this query")
                    
                    # Switch to the one-shot model
                    self._switch_model_to(one_shot_model, permanent=False)
                
                
                # Don't call show_user_message - user already sees their input from prompt
                # Just add a visual separator
                if self.ui:
                    from rich.rule import Rule
                    self.ui.console.print()
                    self.ui.console.print(Rule(style="dim"))
                
                # Parse @file attachments
                attached_files = []
                file_context = {}
                if self.ui:
                    attached_files, query = self.ui.parse_file_attachments(query)
                    if attached_files:
                        self.ui.show_file_attachments(attached_files)
                        # Extract file content for context
                        file_context = self._extract_file_context(attached_files)
                
                # Process message with AGENT-BASED streaming
                try:
                    # Use the new agentic architecture for ALL queries
                    # Agent handles: tool selection, streaming, general vs workspace
                    response = asyncio.run(self._process_with_agent(query, file_context=file_context))
                    
                    # Response is already printed with live streaming
                    # Update context bar with estimated token usage
                    if self.ui and response:
                        # Rough estimate: 4 chars = 1 token
                        query_tokens = len(query) // 4
                        response_tokens = len(response) // 4
                        self.ui.update_context(tokens_used=query_tokens + response_tokens)
                        self.ui.show_context_bar()

                        
                except Exception as e:
                    if self.ui:
                        self.ui.show_error(f"Failed to process message: {e}")
                    else:
                        print(f"\n❌ Error: {e}")
                    if self.debug:
                        import traceback
                        traceback.print_exc()
                
                # Revert model if one-shot
                if one_shot_model and original_model and original_model_obj:
                    self.model = original_model_obj
                    self.actual_model_name = original_model
                    
                    if self.ui:
                        self.ui.show_model_revert_notice(original_model)
                    else:
                        print(f"← Reverted to {original_model}")
                
            except KeyboardInterrupt:
                if self.ui:
                    self.ui.show_success("Goodbye! Session cleaned up.")
                else:
                    print("\n\n👋 Goodbye! Session cleaned up.")
                break
            except EOFError:
                break
            except Exception as e:
                if self.ui:
                    self.ui.show_error(str(e))
                else:
                    print(f"\n❌ Error: {e}")
                if self.debug:
                    import traceback
                    traceback.print_exc()
        
        # Cleanup
        self._cleanup()
    
    async def _process_message_with_panel(self, user_message: str, panel, file_context: dict = None) -> str:
        """
        Process message using FAST query with LIVE panel updates.
        
        Uses threading so the panel spinner keeps animating during AI calls.
        """
        import time
        import threading
        
        # Add file context to the message if provided
        if file_context:
            panel.step(f"Attaching {len(file_context)} files", completed=True, elapsed=0.0)
        
        # Check if diagram-based query
        if self.orchestrator:
            try:
                # Rate limit: check before making AI call
                from stacksense.core.rate_limiter import check_rate_limit
                rate_limit_name = 'openrouter_free' if ':free' in (self.actual_model_name or '') else 'openrouter'
                check_rate_limit(rate_limit_name)
                
                # Result container for thread
                result_container = {'result': None, 'error': None, 'stream_chunks': []}
                done_event = threading.Event()
                
                # Lock for thread-safe panel updates
                panel_lock = threading.Lock()
                
                def on_step_start(step_name):
                    with panel_lock:
                        panel.step(step_name)
                
                def on_step_complete(step_name, elapsed):
                    with panel_lock:
                        panel.update_last_step(step_name, elapsed)
                
                def on_stream_chunk(chunk):
                    # Collect chunks for streaming display after panel
                    result_container['stream_chunks'].append(chunk)
                
                def run_query():
                    """Run AI query in background thread"""
                    try:
                        result = self.orchestrator.query_fast(
                            user_query=user_message,
                            stream=True,
                            on_step_start=on_step_start,
                            on_step_complete=on_step_complete,
                            on_stream_chunk=on_stream_chunk
                        )
                        result_container['result'] = result
                    except Exception as e:
                        result_container['error'] = e
                    finally:
                        done_event.set()
                
                # Start query in background thread
                # NOTE: fast_query_processor handles all step callbacks
                query_thread = threading.Thread(target=run_query, daemon=True)
                query_thread.start()
                
                # Keep panel updating while query runs
                # This is what makes the spinner animate!
                while not done_event.is_set():
                    # Force panel refresh
                    if hasattr(panel, 'live') and panel.live:
                        panel.live.update(panel._render())
                    time.sleep(0.1)  # 10 updates/second
                
                # Check for errors
                if result_container['error']:
                    raise result_container['error']
                
                result = result_container['result']
                
                # Show completion stats
                files_used = result.get('files_used', [])
                total_time = result.get('total_time', 0)
                context_size = result.get('context_size', 0)
                panel.step(f"Complete: {len(files_used)} files, {context_size//1000}KB", 
                          completed=True, elapsed=total_time)
                
                # Get answer (use chunks if available for streaming display)
                stream_chunks = result_container['stream_chunks']
                if stream_chunks:
                    # We have streaming chunks - will be displayed by caller with streaming
                    answer = ''.join(stream_chunks)
                else:
                    answer = result.get('answer', 'No answer generated')
                
                return answer
                
            except Exception as e:
                if self.debug:
                    panel.step(f"Error: {e}", completed=True, elapsed=0)
                # Fall back to old method
                try:
                    panel.step("Falling back to standard query")
                    result = self.orchestrator.query(user_message, extra_context=file_context)
                    return result.get('answer', 'Error generating answer')
                except:
                    pass
        
        # Fall back to regular processing
        panel.step("Building context")
        return await self._process_message(user_message, file_context)
    
    def _extract_file_context(self, file_paths: list) -> dict:
        """
        Extract content from attached files using slicers.
        
        Args:
            file_paths: List of file paths (relative to workspace)
            
        Returns:
            Dict mapping file paths to their content/slices
        """
        context = {}
        
        if not self.workspace_path:
            return context
        
        for file_path in file_paths:
            # Try to find the file
            full_path = os.path.join(self.workspace_path, file_path)
            
            if not os.path.exists(full_path):
                # Try searching for the file
                for root, dirs, files in os.walk(self.workspace_path):
                    if file_path in files:
                        full_path = os.path.join(root, file_path)
                        break
                    # Check basename match
                    basename = os.path.basename(file_path)
                    if basename in files:
                        full_path = os.path.join(root, basename)
                        break
            
            if os.path.exists(full_path):
                try:
                    # Read file content
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Limit content size
                    max_chars = 8000
                    if len(content) > max_chars:
                        # Try to use code slicer if available
                        try:
                            from stacksense.core.code_extractor import CodeExtractor
                            extractor = CodeExtractor()
                            slices = extractor.extract(full_path, content)
                            if slices:
                                # Join slices with separators
                                content = "\n\n---\n\n".join([
                                    f"# {s.get('name', 'code')}\n{s.get('content', '')}"
                                    for s in slices[:10]  # Max 10 slices
                                ])
                        except ImportError:
                            # Fallback: truncate with message
                            content = content[:max_chars] + f"\n\n... (truncated, {len(content) - max_chars} more chars)"
                    
                    context[file_path] = {
                        'path': full_path,
                        'content': content,
                        'size': len(content)
                    }
                except Exception as e:
                    if self.debug:
                        print(f"[Debug] Failed to read {file_path}: {e}")
        
        return context
    
    def _switch_model_to(self, model_name: str, permanent: bool = True):
        """Switch to a specific OpenRouter model"""
        try:
            # Validate model exists
            from stacksense.core.openrouter_client import get_client
            client = get_client()
            models = client.search_models(model_name)
            
            if not models:
                if self.ui:
                    self.ui.show_warning(f"No models matching '{model_name}' found")
                else:
                    print(f"⚠️ No models matching '{model_name}' found")
                return
            
            # Use the first matching model
            selected = models[0]
            self.actual_model_name = selected.id
            
            # Update orchestrator if present
            if self.orchestrator and permanent:
                from stacksense.core.openrouter_client import get_client
                
                class OpenRouterWrapper:
                    def __init__(self, model_id: str):
                        self.client = get_client()
                        self.model_name = model_id
                    
                    def generate(self, prompt, max_tokens=2000):
                        try:
                            return self.client.chat(
                                model=self.model_name,
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=max_tokens
                            )
                        except Exception as e:
                            return f"Error: {e}"
                    
                    def warm_up(self):
                        pass  # No warm-up needed for OpenRouter
                
                self.orchestrator.model = OpenRouterWrapper(selected.id)
            
            if permanent:
                # Save preference for persistence across sessions
                self._save_model_preference(selected.id)
                
                if self.ui:
                    self.ui.show_model_switch_notice(selected.display_name, one_shot=False)
                else:
                    print(f"✅ Switched to {selected.display_name}")
                    
        except Exception as e:
            if self.ui:
                self.ui.show_error(f"Failed to switch model: {e}")
            else:
                print(f"❌ Failed to switch model: {e}")
    
    # ═══════════════════════════════════════════════════════════
    # AGENTIC CHAT - Hybrid Streaming (Option C)
    # ═══════════════════════════════════════════════════════════
    
    async def _process_with_agent(self, user_message: str, file_context: dict = None) -> str:
        """
        Process message using hybrid approach:
        - Phase 1: Simple spinner during wait (always animates)
        - Phase 2: Real streaming when tokens arrive
        
        This fixes the "hanging panel" issue across all providers since
        most providers don't support streaming when tool calling is enabled.
        
        Args:
            user_message: User's query
            file_context: Dict of {filepath: content} for attached files
            
        Returns:
            AI's response
        """
        # Dynamic agent selection based on provider
        from stacksense.core.config import Config
        
        try:
            config = Config()
            provider = getattr(config, 'provider', 'openrouter') or 'openrouter'
        except:
            provider = 'openrouter'
        
        # Import the appropriate agent based on provider
        agent = None
        try:
            if provider == 'openai':
                from stacksense.core.openai_agent import OpenAIAgent
                agent = OpenAIAgent(
                    workspace_path=str(self.workspace_path) if self.workspace_path else None,
                    model_name=self.actual_model_name or "gpt-4o-mini",
                    debug=self.debug
                )
            elif provider == 'grok':
                from stacksense.core.grok_agent import GrokAgent
                agent = GrokAgent(
                    workspace_path=str(self.workspace_path) if self.workspace_path else None,
                    model_name=self.actual_model_name or "grok-beta",
                    debug=self.debug
                )
            elif provider == 'together':
                from stacksense.core.together_agent import TogetherAgent
                agent = TogetherAgent(
                    workspace_path=str(self.workspace_path) if self.workspace_path else None,
                    model_name=self.actual_model_name or "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                    debug=self.debug
                )
            else:  # Default to OpenRouter
                from stacksense.core.openrouter_agent import OpenRouterAgent
                agent = OpenRouterAgent(
                    workspace_path=str(self.workspace_path) if self.workspace_path else None,
                    model_name=self.actual_model_name or "nvidia/nemotron-nano-9b-v2:free",
                    debug=self.debug
                )
        except ImportError as e:
            # Fallback to OpenRouter if provider agent not available
            from stacksense.core.openrouter_agent import OpenRouterAgent
            agent = OpenRouterAgent(
                workspace_path=str(self.workspace_path) if self.workspace_path else None,
                model_name=self.actual_model_name or "nvidia/nemotron-nano-9b-v2:free",
                debug=self.debug
            )
        except ValueError as e:
            # Missing API key - return helpful message
            return f"❌ {str(e)}\n\n💡 Run `stacksense --setup-ai` to configure your provider."
        
        # Rate limit: check before making AI call
        from stacksense.core.rate_limiter import check_rate_limit
        rate_limit_name = f'{provider}_free' if ':free' in (self.actual_model_name or '') else provider
        try:
            check_rate_limit(rate_limit_name)
        except:
            check_rate_limit('openrouter')  # Fallback
        
        # Build enhanced query with file context
        query_with_context = user_message
        if file_context:
            file_sections = []
            for filepath, content in file_context.items():
                # Truncate very large files
                if len(content) > 10000:
                    content = content[:10000] + "\n\n... [truncated - file too large] ..."
                file_sections.append(f"### File: {filepath}\n```\n{content}\n```")
            
            if file_sections:
                query_with_context = f"{user_message}\n\n## Attached Files:\n\n" + "\n\n".join(file_sections)
        
        full_response = []
        
        if self.ui:
            from rich.console import Console
            import time as time_module
            import threading
            
            console = Console()
            streaming_started = [False]
            current_tool = [None]
            start_time = time_module.time()
            status_handle = [None]
            stop_timer = threading.Event()
            current_status_text = ["🤖 Thinking..."]
            
            # Track tool executions for panel display
            tool_executions = []
            tool_start_times = {}
            
            def timer_updater():
                """Background thread to update elapsed time every 0.5s"""
                while not stop_timer.is_set():
                    if status_handle[0] and not streaming_started[0]:
                        elapsed = time_module.time() - start_time
                        status_handle[0].update(f"[cyan]{current_status_text[0]}[/cyan] [dim]({elapsed:.1f}s)[/dim]")
                    stop_timer.wait(0.5)
            
            def on_tool_start(tool_call: str):
                """Track tool start for panel display"""
                tool_name = tool_call.split('(')[0]  # Just the tool name
                current_tool[0] = tool_name
                current_status_text[0] = f"🔧 {tool_name}..."
                tool_start_times[tool_name] = time_module.time()
            
            def on_tool_complete(tool_name: str, status: str):
                """Track tool completion with elapsed time"""
                # Extract elapsed from status string (e.g., "✓ 0.5s" or "✗ 0.3s")
                # The agent already calculated the accurate elapsed time
                elapsed = 0.0
                import re
                match = re.search(r'(\d+\.?\d*)s', status)
                if match:
                    elapsed = float(match.group(1))
                
                success = "✓" in status
                tool_executions.append({
                    'name': tool_name,
                    'elapsed': elapsed,
                    'success': success,
                    'status': status
                })
                current_status_text[0] = "🤖 Thinking..."
            
            def on_token(token: str):
                """Collect tokens during streaming (only used when no tools)"""
                nonlocal streaming_started
                if not streaming_started[0]:
                    streaming_started[0] = True
                    stop_timer.set()  # Stop the timer thread
                    # Stop the spinner when streaming starts
                    if status_handle[0]:
                        status_handle[0].stop()
                
                # Just collect tokens - display handled by response panel
                full_response.append(token)
            
            console.print()
            
            # Start background timer thread
            timer_thread = threading.Thread(target=timer_updater, daemon=True)
            timer_thread.start()
            
            # Phase 1: Simple spinner that ALWAYS animates
            # Rich's console.status() uses internal animation, never freezes
            try:
                with console.status(
                    "[cyan]🤖 Thinking...[/cyan]",
                    spinner="dots"
                ) as status:
                    status_handle[0] = status
                    
                    # Run agent - spinner keeps animating during blocking API calls
                    response = await agent.chat(
                        user_query=query_with_context,
                        on_token=on_token,
                        on_tool_start=on_tool_start,
                        on_tool_complete=on_tool_complete
                    )
            finally:
                stop_timer.set()  # Ensure timer thread stops

            # Phase 2: Process response - extract thinking from answer
            final_response = ''.join(full_response) if full_response else response
            
            # Extract thinking content (XML-style tags) from response
            thinking_content = ""
            clean_response = final_response
            if final_response:
                import re
                
                # Extract thinking tags like <search_quality_reflection>...</search_quality_reflection>
                thinking_patterns = [
                    r'<search_quality_reflection>.*?</search_quality_reflection>',
                    r'<search_quality_score>\d+</search_quality_score>',
                    r'<thinking>.*?</thinking>',
                    r'<reflection>.*?</reflection>',
                    r'<analysis>.*?</analysis>',
                    r'<inner_thoughts>.*?</inner_thoughts>',
                ]
                
                thinking_parts = []
                for pattern in thinking_patterns:
                    matches = re.findall(pattern, final_response, re.DOTALL | re.IGNORECASE)
                    thinking_parts.extend(matches)
                    # Remove from clean response
                    clean_response = re.sub(pattern, '', clean_response, flags=re.DOTALL | re.IGNORECASE)
                
                # Clean up the response (remove extra whitespace)
                clean_response = re.sub(r'\n{3,}', '\n\n', clean_response).strip()
                
                # Format thinking content
                if thinking_parts:
                    # Clean up XML tags for display
                    thinking_text = "\n".join(thinking_parts)
                    thinking_text = re.sub(r'</?[a-z_]+>', '', thinking_text, flags=re.IGNORECASE)
                    thinking_content = thinking_text.strip()
            
            # Show tool + thinking panels side-by-side if either exists
            if tool_executions or thinking_content:
                from rich.panel import Panel
                from rich.columns import Columns
                
                panels = []
                
                # Build tool panel if tools were used
                if tool_executions:
                    # Deduplicate tools (same tool at same start time = same call)
                    seen_tools = set()
                    unique_tools = []
                    for tool in tool_executions:
                        key = (tool['name'], round(tool['elapsed'], 1))
                        if key not in seen_tools:
                            seen_tools.add(key)
                            unique_tools.append(tool)
                    
                    # Build tool execution summary
                    total_time = sum(t['elapsed'] for t in unique_tools)
                    tool_count = len(unique_tools)
                    
                    # Create tool lines
                    tool_lines = []
                    for i, tool in enumerate(unique_tools, 1):
                        icon = "✓" if tool['success'] else "✗"
                        color = "green" if tool['success'] else "red"
                        tool_lines.append(f"[{color}]{icon}[/{color}] {i}. [cyan]{tool['name']}[/cyan] [dim]({tool['elapsed']:.1f}s)[/dim]")
                    
                    tool_content = "\n".join(tool_lines)
                    panel_title = f"🔧 {tool_count} tool{'s' if tool_count != 1 else ''} in {total_time:.1f}s"
                    
                    panels.append(Panel(
                        tool_content,
                        title=f"[bold]{panel_title}[/bold]",
                        border_style="dim",
                        expand=True
                    ))
                
                # Build thinking panel if thinking was extracted
                if thinking_content:
                    # Truncate thinking content for display
                    display_thinking = thinking_content[:300] + ("..." if len(thinking_content) > 300 else "")
                    
                    panels.append(Panel(
                        display_thinking,
                        title="[bold dim]💭 Thinking[/bold dim]",
                        border_style="dim blue",
                        expand=True
                    ))
                
                # Display side by side
                if len(panels) == 2:
                    console.print(Columns(panels, equal=True, expand=True))
                else:
                    console.print(panels[0])
                console.print()
            
            if final_response:
                # Check if AI is asking for permission
                if '__PERMISSION_REQUIRED__' in final_response:
                    # Show the permission prompt (without the marker)
                    permission_text = final_response.replace('__PERMISSION_REQUIRED__', '').strip()
                    from rich.panel import Panel
                    console.print(Panel(permission_text, title="[yellow]⚠️ Permission Required[/yellow]", border_style="yellow"))
                    
                    # Get user response
                    try:
                        user_response = input("Your response (yes/no/custom): ").strip().lower()
                    except (KeyboardInterrupt, EOFError):
                        user_response = "no"
                    
                    # Handle the response
                    if user_response in ['yes', 'y', '']:
                        # Grant permission
                        agent._permission_granted = True
                        
                        # Check if there's a pending action from write_file/run_command
                        pending = getattr(agent, '_pending_permission', {})
                        if pending.get('pending_action'):
                            action = pending['pending_action']
                            agent._pending_permission = {}
                            
                            if action[0] == 'write_file':
                                # Execute the cached write_file
                                _, filepath, content, description = action
                                result = agent._tool_write_file(filepath, content, description)
                                console.print(f"[green]{result}[/green]")
                                
                                # Show summary of what was created
                                console.print()
                                from rich.panel import Panel
                                from rich.markdown import Markdown
                                
                                # Count lines and show brief preview
                                lines = content.split('\n')
                                line_count = len(lines)
                                preview_lines = lines[:5]
                                preview = '\n'.join(preview_lines)
                                if line_count > 5:
                                    preview += f"\n... ({line_count - 5} more lines)"
                                
                                summary_md = f"""### 📝 Created `{filepath}`

**Description:** {description}

**File stats:** {line_count} lines

**Preview:**
```python
{preview}
```

---
*Type your next request or ask questions about the created file.*"""
                                
                                console.print(Panel(Markdown(summary_md), title="[bold green]✓ Task Complete[/bold green]", border_style="green"))
                                return result
                                
                            elif action[0] == 'run_command':
                                # Execute the cached run_command
                                _, command, working_dir = action
                                result = agent._tool_run_command(command, working_dir)
                                console.print(f"[dim]{result}[/dim]")
                                
                                # Show summary of command execution
                                console.print()
                                from rich.panel import Panel
                                from rich.markdown import Markdown
                                
                                # Truncate output if too long
                                output_lines = result.split('\n')
                                if len(output_lines) > 10:
                                    truncated = '\n'.join(output_lines[:10]) + f"\n... ({len(output_lines) - 10} more lines)"
                                else:
                                    truncated = result
                                
                                summary_md = f"""### ⚡ Executed Command

**Command:** `{command}`

**Output:**
```
{truncated}
```

---
*Type your next request or ask about the results.*"""
                                
                                console.print(Panel(Markdown(summary_md), title="[bold green]✓ Command Complete[/bold green]", border_style="green"))
                                return result
                        else:
                            # No cached action - ask AI to proceed (for ask_user prompts)
                            agent._pending_permission = {}
                            console.print("[green]✓ Permission granted. Executing...[/green]")
                            return await self._process_with_agent("User approved. Proceed with the action.", file_context)
                        
                    elif user_response in ['no', 'n']:
                        console.print("[yellow]Action cancelled.[/yellow]")
                        agent._pending_permission = {}
                        agent._permission_granted = False
                        return "Action cancelled by user."
                    else:
                        # Custom response - send back to AI for negotiation
                        console.print(f"[cyan]Sending your feedback to AI...[/cyan]")
                        # Recursively call with user's custom response
                        return await self._process_with_agent(user_response, file_context)
                else:
                    # Clear the progress dots if any
                    if streaming_started[0] and full_response:
                        print()  # Newline after dots
                    
                    # Render AI response in a styled panel (use clean response without thinking)
                    from rich.markdown import Markdown
                    from rich.panel import Panel
                    
                    model_name = self.actual_model_name.split('/')[-1].replace(':free', '') if self.actual_model_name else "AI"
                    display_response = clean_response if clean_response else final_response
                    md = Markdown(display_response)
                    
                    console.print(Panel(
                        md,
                        title=f"[bold green]{model_name}[/bold green]",
                        border_style="green",
                        expand=True,
                        padding=(1, 2)
                    ))
            
            # Show copy hint if code blocks found
            if final_response and '```' in final_response and '__PERMISSION_REQUIRED__' not in final_response:
                import re
                code_blocks = re.findall(r'```[\s\S]*?```', final_response)
                if code_blocks:
                    console.print()
                    console.print(f"[dim]💡 Type /copy to copy code ({len(code_blocks)} block{'s' if len(code_blocks) > 1 else ''})[/dim]")
                    # Store for /copy command
                    if self.ui:
                        self.ui._last_code_blocks = code_blocks
            
            print()
            
            if self.debug:
                stats = agent.get_stats()
                console.print(f"[dim]Stats: {stats['tools_used']} tools, {stats['total_time']:.1f}s[/dim]")
            
            return final_response
        
        else:
            # Non-Rich fallback
            def on_token(token: str):
                print(token, end="", flush=True)
                full_response.append(token)
            
            def on_tool_start(tool_call: str):
                print(f"\n🔧 {tool_call}", flush=True)
            
            def on_tool_complete(tool_name: str, status: str):
                pass
            
            print(f"\n🤖 Thinking...")
            
            response = await agent.chat(
                user_query=query_with_context,
                on_token=on_token,
                on_tool_start=on_tool_start,
                on_tool_complete=on_tool_complete
            )
            
            if not full_response and response:
                print(f"\n{response}")
            
            print("\n")
            
            return ''.join(full_response) if full_response else response



def start_chat(model_type: Optional[str] = None, debug: bool = False):
    """
    Start StackSense interactive chat.
    
    Args:
        model_type: AI model to use
        debug: Enable debug mode
    """
    chat = StackSenseChat(model_type=model_type, debug=debug)
    chat.run()


if __name__ == "__main__":
    # For testing
    start_chat(debug=True)

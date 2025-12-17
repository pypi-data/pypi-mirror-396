"""
StackSense Input Completer
==========================
Autocomplete for chat input:
- @ → File suggestions (5-6 relevant files)
- model: → All models (one-shot)
- model(free): → Free models only (one-shot)
- model(paid): → Paid models only (one-shot)
- /(free)model → Free models only (permanent)
- /(paid)model → Paid models only (permanent)
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Iterable

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


class StackSenseCompleter(Completer):
    """
    Smart completer for StackSense chat.
    
    Triggers:
        @              → File autocomplete
        model:         → All models (one-shot)
        model(free):   → Free models only (one-shot)
        model(paid):   → Paid models only (one-shot)
        /(free)model   → Free models only (permanent)
        /(paid)model   → Paid models only (permanent)
    """
    
    def __init__(self, workspace_path: str = None, memory_path: str = None):
        """
        Args:
            workspace_path: Path to current workspace/repo
            memory_path: Path to ai_memory.json for relevant files
        """
        self.workspace_path = workspace_path
        self.memory_path = memory_path
        self._cached_models: List[str] = []
        self._cached_files: List[str] = []
        self._relevant_files: List[str] = []
    
    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        """Get completions based on current input."""
        text = document.text_before_cursor
        
        # Check for @ file completion
        if '@' in text:
            at_pos = text.rfind('@')
            query = text[at_pos + 1:]
            for completion in self._get_file_completions(query):
                yield completion
            return
        
        # model(free): - one-shot, free only
        if text.startswith('model(free):'):
            query = text[12:]
            for completion in self._get_model_completions(query, filter_type='free'):
                yield completion
            return
        
        # model(paid): - one-shot, paid only
        if text.startswith('model(paid):'):
            query = text[12:]
            for completion in self._get_model_completions(query, filter_type='paid'):
                yield completion
            return
        
        # model: - one-shot, all models
        if text.startswith('model:'):
            query = text[6:]
            for completion in self._get_model_completions(query, filter_type='all'):
                yield completion
            return
        
        # /(free)model - permanent, free only
        if text.startswith('/(free)model'):
            parts = text.split(maxsplit=1)
            query = parts[1] if len(parts) > 1 else ''
            for completion in self._get_model_completions(query, filter_type='free'):
                yield completion
            return
        
        # /(paid)model - permanent, paid only
        if text.startswith('/(paid)model'):
            parts = text.split(maxsplit=1)
            query = parts[1] if len(parts) > 1 else ''
            for completion in self._get_model_completions(query, filter_type='paid'):
                yield completion
            return
    
    def _get_file_completions(self, query: str) -> Iterable[Completion]:
        """
        Get file completions for @ trigger.
        
        Features:
        - Fuzzy matching: @pay → payment.py, PaymentPage.tsx
        - Shows 15 files per page
        - Respects gitignore (handled by _get_relevant_files)
        """
        # Get files (cached or fresh)
        files = self._get_relevant_files()
        
        if not query:
            # No query - show first 15 files
            matches = files[:15]
        else:
            # Fuzzy match: split query into characters for substring matching
            query_lower = query.lower()
            
            # Score files based on match quality
            scored = []
            for f in files:
                f_lower = f.lower()
                filename_lower = os.path.basename(f).lower()
                
                # Exact filename match is best
                if filename_lower == query_lower:
                    scored.append((0, f))
                # Filename starts with query
                elif filename_lower.startswith(query_lower):
                    scored.append((1, f))
                # Filename contains query
                elif query_lower in filename_lower:
                    scored.append((2, f))
                # Path contains query
                elif query_lower in f_lower:
                    scored.append((3, f))
                # Fuzzy: all chars appear in order
                elif self._fuzzy_match(query_lower, f_lower):
                    scored.append((4, f))
            
            # Sort by score and take top 15
            scored.sort(key=lambda x: (x[0], len(x[1])))
            matches = [f for _, f in scored[:15]]
        
        for filepath in matches:
            filename = os.path.basename(filepath)
            display = f"📄 {filename}"
            
            yield Completion(
                text=filepath,
                start_position=-len(query),
                display=display,
                display_meta=filepath if len(filepath) <= 45 else f"...{filepath[-42:]}"
            )
    
    def _fuzzy_match(self, query: str, text: str) -> bool:
        """Check if all query chars appear in text in order (fuzzy match)."""
        query_idx = 0
        for char in text:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
        return query_idx == len(query)
    
    def _get_model_completions(self, query: str, filter_type: str = 'all') -> Iterable[Completion]:
        """
        Get model completions with optional free/paid filter.
        Shows ALL matching models (no limit).
        """
        models = self._get_provider_models()  # Returns (id, display_name, is_free) tuples
        query_lower = query.lower()
        
        count = 0
        for model_id, display_name, is_free in models:
            # Apply filter
            if filter_type == 'free' and not is_free:
                continue
            if filter_type == 'paid' and is_free:
                continue
            
            # Match query (if empty query, show all)
            if not query_lower or query_lower in model_id.lower() or query_lower in display_name.lower():
                count += 1
                
                # Add FREE/PAID marker to display
                marker = "[FREE]" if is_free else "[PAID]"
                
                yield Completion(
                    text=model_id,
                    start_position=-len(query),
                    display=f"{display_name} {marker}",
                    display_meta=model_id[:35] if len(model_id) > 35 else model_id
                )
    
    def _get_relevant_files(self) -> List[str]:
        """
        Get all project files for autocomplete.
        
        Features:
        1. Respects .gitignore patterns
        2. Excludes venv, node_modules, __pycache__, .git by default
        3. Caches all files for fast filtering
        """
        if self._relevant_files:
            return self._relevant_files
        
        if not self.workspace_path:
            return []
        
        workspace = Path(self.workspace_path)
        
        # Load gitignore patterns
        gitignore_patterns = set()
        default_ignores = {
            'venv', '.venv', 'env', '.env', 'node_modules', '__pycache__',
            '.git', '.idea', '.vscode', 'dist', 'build', '.next', '.cache',
            '*.pyc', '*.pyo', '.DS_Store', '.stacksense', '.mypy_cache',
            'coverage', 'htmlcov', '.pytest_cache', 'eggs', '*.egg-info'
        }
        gitignore_patterns.update(default_ignores)
        
        # Read .gitignore if exists
        gitignore_path = workspace / '.gitignore'
        if gitignore_path.exists():
            try:
                with open(gitignore_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Remove trailing slashes and add
                            gitignore_patterns.add(line.rstrip('/'))
            except:
                pass
        
        # Also read .dockerignore
        dockerignore_path = workspace / '.dockerignore'
        if dockerignore_path.exists():
            try:
                with open(dockerignore_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            gitignore_patterns.add(line.rstrip('/'))
            except:
                pass
        
        files = []
        
        def should_ignore(path: str) -> bool:
            """Check if path should be ignored based on patterns."""
            parts = Path(path).parts
            for pattern in gitignore_patterns:
                # Direct name match
                if pattern in parts:
                    return True
                # Pattern in path string
                if pattern in path:
                    return True
                # Glob-style matching for simple patterns
                if pattern.startswith('*.'):
                    if path.endswith(pattern[1:]):
                        return True
            return False
        
        # Collect all files
        try:
            for item in workspace.rglob('*'):
                if not item.is_file():
                    continue
                
                rel_path = str(item.relative_to(workspace))
                
                # Skip ignored files
                if should_ignore(rel_path):
                    continue
                
                # Only include common source files
                ext = item.suffix.lower()
                if ext in {'.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
                          '.java', '.go', '.rs', '.rb', '.php', '.c', '.cpp', '.h',
                          '.md', '.json', '.yaml', '.yml', '.toml', '.txt', '.css',
                          '.scss', '.html', '.sql', '.sh', '.env.example'}:
                    files.append(rel_path)
        except Exception:
            pass
        
        # Sort: prioritize important files, then alphabetically
        important_names = {'main', 'app', 'index', '__init__', 'setup', 'config', 
                          'settings', 'models', 'views', 'api', 'routes', 'auth'}
        
        def sort_key(f: str) -> tuple:
            name = Path(f).stem.lower()
            is_important = any(imp in name for imp in important_names)
            return (not is_important, f.count('/'), f.lower())
        
        files.sort(key=sort_key)
        
        self._relevant_files = files
        return self._relevant_files
    
    def _get_provider_models(self) -> List[tuple]:
        """
        Get models for current provider from dynamic registry.
        Returns list of (model_id, display_name, is_free) tuples.
        Uses pricing data to determine free/paid status.
        """
        if self._cached_models:
            return self._cached_models
        
        try:
            import httpx
            
            url = "https://openrouter.ai/api/v1/models"
            response = httpx.get(url, timeout=10.0)
            data = response.json()
            
            # Filter for tool calling models and extract pricing info
            models = []
            for model in data.get("data", []):
                supported_params = model.get("supported_parameters", [])
                if "tools" in supported_params:
                    model_id = model.get("id", "")
                    model_name = model.get("name", model_id)
                    
                    # Determine if free from pricing data
                    pricing = model.get("pricing", {})
                    prompt_cost = float(pricing.get("prompt", "1"))
                    completion_cost = float(pricing.get("completion", "1"))
                    is_free = (prompt_cost == 0 and completion_cost == 0)
                    
                    # Clean display name
                    display_name = model_name.replace(" (free)", "").strip()
                    if len(display_name) > 35:
                        display_name = display_name[:35] + '...'
                    
                    models.append((model_id, display_name, is_free))
            
            # Sort: free models first (for /(free)model), then by name
            # For /(paid)model, the filtering will handle showing paid first
            models.sort(key=lambda x: (not x[2], x[1]))
            
            # Cache ALL models - no limit!
            self._cached_models = models
            
        except Exception as e:
            # Print error for debugging (will show in terminal)
            import sys
            print(f"[Debug] Model fetch failed: {e}", file=sys.stderr)
            
            # Fallback - ONLY verified native tool-calling models
            self._cached_models = [
                # Free native tool-calling models
                ("google/gemini-2.0-flash-exp:free", "Gemini 2.0 Flash", True),
                ("mistralai/devstral-2512:free", "Mistral Devstral", True),
                # Paid native tool-calling models  
                ("openai/gpt-4o", "GPT-4o", False),
                ("openai/gpt-4o-mini", "GPT-4o Mini", False),
                ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet", False),
            ]
        
        return self._cached_models
    
    def refresh_files(self):
        """Clear file cache to force refresh."""
        self._relevant_files = []
    
    def refresh_models(self):
        """Clear model cache to force refresh."""
        self._cached_models = []


"""
StackSense Configuration
Local storage for API keys and provider settings
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict


# Config directory (user's home)
CONFIG_DIR = Path.home() / ".stacksense"
CONFIG_FILE = CONFIG_DIR / "config.json"
WORKSPACES_DIR = CONFIG_DIR / "workspaces"


def get_workspace_path(workspace_path: Optional[str] = None) -> Path:
    """
    Get the storage path for a workspace.
    
    Stores data in ~/.stacksense/workspaces/{parent}/{repo}/ to:
    1. Prevent accidental git pushes of .stacksense folders
    2. Support multi-repo workspaces (e.g., telios/Frontend + telios/Backend)
    
    Args:
        workspace_path: Path to the workspace (cwd if None)
        
    Returns:
        Path to workspace-specific storage directory
        
    Examples:
        ~/GitHub/telios/Telios_Backend -> ~/.stacksense/workspaces/telios/Telios_Backend/
        ~/GitHub/wisdom-drop -> ~/.stacksense/workspaces/wisdom-drop/wisdom-drop/
    """
    if workspace_path:
        ws_path = Path(workspace_path).resolve()
    else:
        ws_path = Path.cwd().resolve()
    
    # Get parent folder name (workspace) and current folder name (repo)
    repo_name = ws_path.name
    parent_name = ws_path.parent.name
    
    # If parent is a common folder like "GitHub", "Documents", "home", etc.
    # use repo name as workspace name too
    common_parents = {"GitHub", "Documents", "Projects", "repos", "code", "src", "dev", "home"}
    if parent_name in common_parents or parent_name == repo_name:
        workspace_name = repo_name
    else:
        workspace_name = parent_name
    
    # Create and return the workspace path
    path = WORKSPACES_DIR / workspace_name / repo_name
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    name: str
    base_url: str
    api_key: str = ""
    default_model: str = ""
    supports_tools: bool = True


# Built-in provider templates
PROVIDERS = {
    "openrouter": ProviderConfig(
        name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        default_model="nvidia/nemotron-nano-9b-v2:free",
        supports_tools=True
    ),
    "together": ProviderConfig(
        name="TogetherAI",
        base_url="https://api.together.xyz/v1",
        default_model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        supports_tools=True
    ),
    "groq": ProviderConfig(
        name="Groq",
        base_url="https://api.groq.com/openai/v1",
        default_model="llama-3.3-70b-versatile",
        supports_tools=True
    ),
    "openai": ProviderConfig(
        name="OpenAI",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
        supports_tools=True
    ),
    "anthropic": ProviderConfig(
        name="Anthropic (via OpenRouter)",
        base_url="https://openrouter.ai/api/v1",
        default_model="anthropic/claude-3.5-sonnet",
        supports_tools=True
    ),
}


class Config:
    """StackSense configuration manager"""
    
    def __init__(self):
        self._config: Dict = {}
        self._load()
    
    def _ensure_dir(self):
        """Ensure config directory exists"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """Load config from disk"""
        self._ensure_dir()
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}
        else:
            self._config = self._default_config()
            self._save()
    
    def _save(self):
        """Save config to disk"""
        self._ensure_dir()
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "provider": "openrouter",
            "providers": {},
            "custom_model": "",
            "show_free_only": True
        }
    
    # ═══════════════════════════════════════════════════════════
    # PROVIDER SETTINGS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def provider(self) -> str:
        """Current provider name"""
        return self._config.get("provider", "openrouter")
    
    @provider.setter
    def provider(self, value: str):
        self._config["provider"] = value
        self._save()
    
    @property
    def provider_config(self) -> ProviderConfig:
        """Get current provider configuration"""
        name = self.provider
        
        # Check for stored config
        if name in self._config.get("providers", {}):
            stored = self._config["providers"][name]
            base = PROVIDERS.get(name, PROVIDERS["openrouter"])
            return ProviderConfig(
                name=base.name,
                base_url=stored.get("base_url", base.base_url),
                api_key=stored.get("api_key", ""),
                default_model=stored.get("default_model", base.default_model),
                supports_tools=base.supports_tools
            )
        
        # Return built-in provider
        return PROVIDERS.get(name, PROVIDERS["openrouter"])
    
    # ═══════════════════════════════════════════════════════════
    # API KEY MANAGEMENT
    # ═══════════════════════════════════════════════════════════
    
    def get_api_key(self, provider: Optional[str] = None) -> str:
        """Get API key for provider (checks config, then env)"""
        provider = provider or self.provider
        
        # Check stored config first
        if provider in self._config.get("providers", {}):
            key = self._config["providers"][provider].get("api_key", "")
            if key:
                return key
        
        # Then check environment variables
        env_vars = {
            "openrouter": "OPENROUTER_API_KEY",
            "together": "TOGETHER_API_KEY",
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "OPENROUTER_API_KEY",  # Via OpenRouter
        }
        
        env_var = env_vars.get(provider, f"{provider.upper()}_API_KEY")
        return os.environ.get(env_var, "")
    
    def set_api_key(self, key: str, provider: Optional[str] = None):
        """Store API key for provider (locally only, never sent anywhere)"""
        provider = provider or self.provider
        
        if "providers" not in self._config:
            self._config["providers"] = {}
        
        if provider not in self._config["providers"]:
            self._config["providers"][provider] = {}
        
        self._config["providers"][provider]["api_key"] = key
        self._save()
    
    # ═══════════════════════════════════════════════════════════
    # MODEL SETTINGS
    # ═══════════════════════════════════════════════════════════
    
    @property
    def model(self) -> str:
        """Current model"""
        # Check for custom model first
        custom = self._config.get("custom_model", "")
        if custom:
            return custom
        
        # Then check provider's stored model
        provider = self.provider
        if provider in self._config.get("providers", {}):
            stored = self._config["providers"][provider].get("default_model", "")
            if stored:
                return stored
        
        # Fall back to provider default
        return self.provider_config.default_model
    
    @model.setter
    def model(self, value: str):
        self._config["custom_model"] = value
        self._save()
    
    @property
    def show_free_only(self) -> bool:
        """Whether to show only free models"""
        return self._config.get("show_free_only", True)
    
    @show_free_only.setter
    def show_free_only(self, value: bool):
        self._config["show_free_only"] = value
        self._save()
    
    # ═══════════════════════════════════════════════════════════
    # SETUP WIZARD
    # ═══════════════════════════════════════════════════════════
    
    def needs_setup(self) -> bool:
        """Check if initial setup is needed"""
        return not self.get_api_key()
    
    def interactive_setup(self):
        """Run interactive setup wizard"""
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        from rich.panel import Panel
        
        console = Console()
        
        console.print()
        console.print(Panel.fit(
            "[bold cyan]StackSense Setup[/bold cyan]\n"
            "Configure your AI provider",
            border_style="cyan"
        ))
        
        # Provider selection
        console.print("\n[bold]Available Providers:[/bold]")
        for i, (key, p) in enumerate(PROVIDERS.items(), 1):
            console.print(f"  {i}. {p.name}")
        
        choice = Prompt.ask(
            "\nSelect provider",
            choices=["1", "2", "3", "4", "5"],
            default="1"
        )
        
        provider_keys = list(PROVIDERS.keys())
        self.provider = provider_keys[int(choice) - 1]
        
        # API key
        console.print(f"\n[bold]Enter API key for {PROVIDERS[self.provider].name}:[/bold]")
        console.print("[dim]Your key is stored locally only, never sent to our servers[/dim]")
        
        key = Prompt.ask("API Key", password=True)
        if key:
            self.set_api_key(key)
        
        # Model selection (optional)
        if Confirm.ask("\nCustomize default model?", default=False):
            model = Prompt.ask(
                "Model name",
                default=self.provider_config.default_model
            )
            self.model = model
        
        console.print("\n[bold green]✅ Setup complete![/bold green]")
        console.print(f"Provider: {PROVIDERS[self.provider].name}")
        console.print(f"Model: {self.model}")
    
    def __repr__(self):
        return f"Config(provider={self.provider}, model={self.model})"


# Global config instance  
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config

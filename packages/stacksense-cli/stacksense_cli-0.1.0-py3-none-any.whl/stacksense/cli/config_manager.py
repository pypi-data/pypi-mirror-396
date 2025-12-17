"""
StackSense Configuration Manager
================================
Standalone configuration for StackSense AI settings.
"""

import os
import json
from pathlib import Path
from typing import Optional, Any, Dict


# Config file location
CONFIG_DIR = Path.home() / ".stacksense"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _ensure_config_dir():
    """Ensure config directory exists"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _load_config() -> Dict[str, Any]:
    """Load config from file"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_config(config: Dict[str, Any]):
    """Save config to file"""
    _ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_preference(key: str, default: Any = None) -> Any:
    """
    Get a configuration preference.
    
    Args:
        key: Preference key
        default: Default value if not found
        
    Returns:
        Preference value
    """
    # Check environment variables first
    env_key = f"STACKSENSE_{key.upper()}"
    env_val = os.environ.get(env_key)
    if env_val is not None:
        return env_val
    
    # Check config file
    config = _load_config()
    return config.get(key, default)


def set_preference(key: str, value: Any):
    """
    Set a configuration preference.
    
    Args:
        key: Preference key
        value: Value to set
    """
    config = _load_config()
    config[key] = value
    _save_config(config)


def get_all_preferences() -> Dict[str, Any]:
    """Get all preferences"""
    return _load_config()


def setup_ai_interactive():
    """
    Interactive AI setup wizard.
    
    Prompts user to configure their preferred AI model.
    API keys are stored LOCALLY in ~/.stacksense/config.json - never sent to any server.
    """
    print("\n🤖 StackSense AI Setup")
    print("=" * 40)
    print("\nSelect your AI provider:\n")
    print("  1. OpenRouter (cloud, 100+ models, recommended)")
    print("  2. Ollama (local, free, requires install)")
    print("  3. Heuristic (no AI, pattern-based)")
    print("  0. Cancel\n")
    
    try:
        choice = input("Select [0-3]: ").strip()
        
        if choice == "0":
            print("✅ Setup cancelled\n")
            return
        
        if choice == "1":
            # OpenRouter setup
            print("\n☁️  OpenRouter Setup")
            print("-" * 30)
            print("\n🔐 Your API key is stored LOCALLY in ~/.stacksense/config.json")
            print("   It is NEVER sent to our servers.\n")
            
            # Check for existing key
            existing_key = get_preference("openrouter_api_key")
            if existing_key:
                masked = existing_key[:12] + "..." + existing_key[-4:] if len(existing_key) > 16 else "***"
                print(f"   Current key: {masked}")
                update = input("   Update key? [y/N]: ").strip().lower()
                if update != 'y':
                    print("✅ Keeping existing OpenRouter configuration\n")
                    return
            
            print("Get your API key from: https://openrouter.ai/settings/keys\n")
            api_key = input("Enter OpenRouter API key (sk-or-v1-...): ").strip()
            
            if not api_key:
                print("❌ No key provided. Setup cancelled.\n")
                return
            
            if not api_key.startswith("sk-or-"):
                print("⚠️  Warning: Key doesn't look like OpenRouter format (sk-or-...)")
                confirm = input("Continue anyway? [y/N]: ").strip().lower()
                if confirm != 'y':
                    print("❌ Setup cancelled.\n")
                    return
            
            # Get default model preference
            print("\nDefault model (can change anytime with /model):")
            print("  1. claude-3-5-sonnet (smart, balanced)")
            print("  2. gpt-4o (very capable)")
            print("  3. gemini-2.0-flash-exp:free (free)")
            print("  4. Enter custom model ID")
            
            model_choice = input("\nSelect [1-4]: ").strip()
            model_map = {
                "1": "anthropic/claude-3-5-sonnet",
                "2": "openai/gpt-4o",
                "3": "google/gemini-2.0-flash-exp:free",
            }
            
            if model_choice == "4":
                default_model = input("Enter model ID: ").strip() or "anthropic/claude-3-5-sonnet"
            else:
                default_model = model_map.get(model_choice, "anthropic/claude-3-5-sonnet")
            
            # Store locally - NEVER sent to server
            set_preference("default_ai_model", "openrouter")
            set_preference("openrouter_api_key", api_key)
            set_preference("openrouter_model", default_model)
            
            print(f"\n✅ Configured OpenRouter with model: {default_model}")
            print("🔐 Key stored locally in ~/.stacksense/config.json\n")
        
        elif choice == "2":
            # Ollama setup
            print("\n📦 Ollama Setup")
            print("-" * 30)
            
            # Get available models
            try:
                import subprocess
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    models = [line.split()[0] for line in lines if line.strip()]
                    
                    if models:
                        print("\nAvailable models:")
                        for i, model in enumerate(models, 1):
                            print(f"  {i}. {model}")
                        
                        model_choice = input(f"\nSelect model [1-{len(models)}] or type name: ").strip()
                        
                        try:
                            idx = int(model_choice) - 1
                            if 0 <= idx < len(models):
                                model_name = models[idx]
                            else:
                                model_name = model_choice
                        except ValueError:
                            model_name = model_choice
                    else:
                        print("\n⚠️  No models found. Run: ollama pull llama3")
                        model_name = input("Enter model name: ").strip() or "llama3"
                else:
                    print("\n⚠️  Could not list models")
                    model_name = input("Enter model name: ").strip() or "llama3"
            except FileNotFoundError:
                print("\n⚠️  Ollama not found. Install from https://ollama.com")
                model_name = input("Enter model name: ").strip() or "llama3"
            
            set_preference("default_ai_model", "ollama")
            set_preference("ollama_model", model_name)
            print(f"\n✅ Configured Ollama with model: {model_name}")
            
        elif choice == "3":
            set_preference("default_ai_model", "heuristic")
            print("\n✅ Configured Heuristic (pattern-based) mode")
        
        else:
            print("❌ Invalid choice")
            return
        
        print("\n💡 You can reconfigure anytime with: stacksense --setup-ai\n")
        
    except KeyboardInterrupt:
        print("\n\n✅ Setup cancelled\n")


def is_configured() -> bool:
    """Check if AI is configured"""
    model = get_preference("default_ai_model")
    return model is not None


def get_configured_model() -> Optional[str]:
    """Get the configured AI model type"""
    return get_preference("default_ai_model")


def get_ollama_model() -> str:
    """Get configured Ollama model name"""
    return get_preference("ollama_model", "llama3")

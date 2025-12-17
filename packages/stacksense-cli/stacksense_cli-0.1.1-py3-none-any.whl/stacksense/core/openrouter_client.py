"""
OpenRouter API Client
=====================
Replaces Ollama with OpenRouter for cloud-based inference.
Uses FREE models only with live filtering.
"""
import os
import json
import time
import requests
from typing import List, Dict, Optional, Callable, Generator
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OpenRouterModel:
    """Model info from OpenRouter"""
    id: str
    name: str
    context_length: int
    is_free: bool
    
    @property
    def display_name(self) -> str:
        """Display name with (free) suffix for disambiguation"""
        # Remove existing (free) suffix if present, then add based on is_free
        name = self.name.replace(" (free)", "").strip()
        if self.is_free:
            return f"{name} (free)"
        return name


class OpenRouterClient:
    """
    OpenRouter API client with free model filtering.
    
    Usage:
        client = OpenRouterClient()  # Reads from .env
        
        # Get free models
        models = client.get_free_models()
        
        # Generate with streaming
        for chunk in client.chat_stream(model_id, messages):
            print(chunk, end="")
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str = None):
        """
        Initialize client.
        
        Args:
            api_key: OpenRouter API key (reads from .env if not provided)
        """
        # Load from .env if not provided
        if not api_key:
            api_key = self._load_api_key()
        
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found!\n"
                "Set it in your .env file or environment:\n"
                "  OPENROUTER_API_KEY=sk-or-v1-...\n\n"
                "Get your key at: https://openrouter.ai/keys"
            )
        
        self.api_key = api_key
        self._models_cache: List[OpenRouterModel] = []
        self._cache_time: float = 0
        self._cache_ttl = 3600  # 1 hour cache
        
        # Rate limiting (free tier: ~20-30 req/min)
        self._request_times: List[float] = []
        self._max_requests_per_min = 25
    
    def _load_api_key(self) -> Optional[str]:
        """Load API key from config, .env, or environment"""
        # Try python-dotenv first (most reliable)
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Try environment 
        key = os.getenv("OPENROUTER_API_KEY")
        if key:
            return key.strip().strip('"\'')
        
        # Try local config file (~/.stacksense/config.json) - from --setup-ai
        try:
            config_path = Path.home() / ".stacksense" / "config.json"
            if config_path.exists():
                import json
                config = json.loads(config_path.read_text())
                # Config class stores keys under: providers.openrouter.api_key
                providers = config.get("providers", {})
                if "openrouter" in providers:
                    key = providers["openrouter"].get("api_key", "")
                    if key:
                        return key.strip().strip('"\'')
                # Also check old location for backward compat
                if config.get("openrouter_api_key"):
                    return config["openrouter_api_key"].strip().strip('"\'')
        except Exception:
            pass
        
        # Manual .env parsing as fallback
        env_paths = [
            Path.cwd() / ".env",
            Path.home() / ".env",
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                try:
                    with open(env_path) as f:
                        for line in f:
                            line = line.strip()
                            # Handle: OPENROUTER_API_KEY = "value" (with spaces)
                            if 'OPENROUTER_API_KEY' in line and '=' in line:
                                # Split on first = and strip spaces
                                parts = line.split('=', 1)
                                if len(parts) == 2:
                                    return parts[1].strip().strip('"\'')
                except Exception:
                    continue
        
        return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/stacksense/stacksense",
            "X-Title": "StackSense",
            "Content-Type": "application/json"
        }
    
    def _check_rate_limit(self):
        """Check and wait if rate limited"""
        now = time.time()
        
        # Clean old requests (>1 min ago)
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        # Check if at limit
        if len(self._request_times) >= self._max_requests_per_min:
            wait_time = 60 - (now - self._request_times[0])
            if wait_time > 0:
                print(f"⏳ Rate limit reached. Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                self._request_times = []
        
        # Track this request
        self._request_times.append(now)
    
    # Fallback list if API fails - these are verified to support NATIVE tool calling
    FALLBACK_MODELS = [
        # Free native tool-calling models
        ("google/gemini-2.0-flash-exp:free", "Gemini 2.0 Flash", 1048576),
        ("mistralai/devstral-2512:free", "Mistral Devstral", 64000),
        # Paid native tool-calling models
        ("openai/gpt-4o", "GPT-4o", 128000),
        ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet", 200000),
    ]
    
    def get_free_models(self, force_refresh: bool = False) -> List[OpenRouterModel]:
        """Alias for get_models(filter='free') for backward compatibility."""
        return self.get_models(filter_type='free', force_refresh=force_refresh)
    
    def get_models(self, filter_type: str = 'all', force_refresh: bool = False) -> List[OpenRouterModel]:
        """
        Get tool-calling capable models from OpenRouter API.
        
        Args:
            filter_type: 'all' (default), 'free', or 'paid'
            force_refresh: Force refresh the cache
        
        Returns:
            List of models supporting tool calling
        """
        # Check cache first
        now = time.time()
        if not force_refresh and self._models_cache and (now - self._cache_time) < self._cache_ttl:
            models = self._models_cache
        else:
            try:
                import httpx
                
                url = "https://openrouter.ai/api/v1/models"
                response = httpx.get(url, timeout=10.0)
                data = response.json()
                
                models = []
                for model_data in data.get("data", []):
                    # Only include models that support tool calling
                    supported_params = model_data.get("supported_parameters", [])
                    if "tools" not in supported_params:
                        continue
                    
                    pricing = model_data.get("pricing", {})
                    is_free = (
                        float(pricing.get("prompt", 1)) == 0 and
                        float(pricing.get("completion", 1)) == 0
                    )
                    
                    models.append(OpenRouterModel(
                        id=model_data.get("id", ""),
                        name=model_data.get("name", ""),
                        context_length=model_data.get("context_length", 4096),
                        is_free=is_free
                    ))
                
                # Sort by context length (largest first)
                models.sort(key=lambda m: -m.context_length)
                
                # Cache ALL tool-calling models (no limit)
                self._models_cache = models
                self._cache_time = now
                models = self._models_cache
                
            except Exception as e:
                if self.debug:
                    print(f"[OpenRouter] API fetch failed: {e}, using fallback")
                
                # Return fallback list
                models = [
                    OpenRouterModel(
                        id=model_id,
                        name=name,
                        context_length=ctx,
                        is_free=is_free
                    )
                    for model_id, name, ctx, is_free in [
                        ("google/gemini-2.0-flash-exp:free", "Gemini 2.0 Flash", 1048576, True),
                        ("openai/gpt-4o", "GPT-4o", 128000, False),
                        ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet", 200000, False),
                    ]
                ]
        
        # Apply filter (no limit - return all matching)
        if filter_type == 'free':
            return [m for m in models if m.is_free]
        elif filter_type == 'paid':
            return [m for m in models if not m.is_free]
        else:  # 'all'
            return models
    
    def get_all_free_models(self, force_refresh: bool = False) -> List[OpenRouterModel]:
        """
        Get ALL free models from OpenRouter (for advanced users).
        
        Returns:
            List of all free models
        """
        # Check cache
        now = time.time()
        if not force_refresh and self._models_cache and (now - self._cache_time) < self._cache_ttl:
            return self._models_cache
        
        self._check_rate_limit()
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/models",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            if self._models_cache:
                return self._models_cache
            raise RuntimeError(f"Failed to fetch models: {e}")
        
        models = []
        for m in data.get('data', []):
            model_id = m.get('id', '')
            model_name = m.get('name', '').lower()
            
            pricing = m.get('pricing', {})
            prompt_price = pricing.get('prompt', '1')
            completion_price = pricing.get('completion', '1')
            
            is_free = (
                ':free' in model_id.lower() or
                (str(prompt_price) == '0' and str(completion_price) == '0')
            )
            
            if not is_free:
                continue
            
            architecture = m.get('architecture', {})
            modality = architecture.get('modality', 'text->text')
            
            if any(x in modality.lower() for x in ['image', 'vision', 'audio', 'video']):
                continue
            if any(x in model_name for x in ['vision', 'image', 'audio', 'video', 'vl', 'img']):
                continue
            
            models.append(OpenRouterModel(
                id=model_id,
                name=m.get('name', model_id),
                context_length=m.get('context_length', 4096),
                is_free=True
            ))
        
        self._models_cache = models
        self._cache_time = now
        
        return models
    
    def search_models(self, query: str, filter_type: str = 'all') -> List[OpenRouterModel]:
        """
        Search models by name.
        
        Args:
            query: Search string (case-insensitive)
            filter_type: 'all' (default), 'free', or 'paid'
            
        Returns:
            Matching models
        """
        models = self.get_models(filter_type=filter_type)
        
        if not query:
            return models
        
        query_lower = query.lower()
        
        # Exact match first
        exact = [m for m in models if m.id.lower() == query_lower]
        if exact:
            return exact
        
        # Partial match
        return [
            m for m in models
            if query_lower in m.id.lower() or query_lower in m.name.lower()
        ]
    
    def chat(
        self,
        model: str,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Non-streaming chat completion.
        
        Args:
            model: Model ID (e.g., "meta-llama/llama-3.2-3b-instruct:free")
            messages: List of {"role": "...", "content": "..."} dicts
            temperature: Randomness (0-1)
            max_tokens: Max response length
            
        Returns:
            Response text
        """
        self._check_rate_limit()
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._get_headers(),
            json=payload,
            timeout=120
        )
        
        if not response.ok:
            raise RuntimeError(f"OpenRouter error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        return data['choices'][0]['message']['content']
    
    def chat_stream(
        self,
        model: str,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        on_token: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Generator[str, None, str]:
        """
        Streaming chat completion.
        
        Args:
            model: Model ID
            messages: Chat messages
            temperature: Randomness
            max_tokens: Max length
            on_token: Callback for each token
            
        Yields:
            Response tokens as they arrive
            
        Returns:
            Full response text
        """
        self._check_rate_limit()
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._get_headers(),
            json=payload,
            stream=True,
            timeout=120
        )
        
        if not response.ok:
            raise RuntimeError(f"OpenRouter error: {response.status_code} - {response.text}")
        
        full_response = []
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8')
            
            # Skip non-data lines
            if not line_str.startswith('data: '):
                continue
            
            # Handle [DONE] marker
            data_str = line_str[6:]  # Remove "data: " prefix
            if data_str.strip() == '[DONE]':
                break
            
            try:
                data = json.loads(data_str)
                
                # Extract content from delta
                choices = data.get('choices', [])
                if choices:
                    delta = choices[0].get('delta', {})
                    content = delta.get('content', '')
                    
                    if content:
                        full_response.append(content)
                        
                        if on_token:
                            on_token(content)
                        
                        yield content
                        
            except json.JSONDecodeError:
                continue
        
        return ''.join(full_response)
    
    def chat_with_tools(
        self,
        model: str,
        messages: List[Dict],
        tools: List[Dict],
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_call: Optional[Callable[[str, Dict], None]] = None,
        **kwargs
    ) -> Dict:
        """
        Chat with function/tool calling support.
        
        Args:
            model: Model ID
            messages: Chat messages
            tools: Tool definitions (OpenAI format)
            on_token: Token callback
            on_tool_call: Tool call callback
            
        Returns:
            {
                "content": str,  # Text response
                "tool_calls": [{"name": str, "arguments": dict}, ...]
            }
        """
        self._check_rate_limit()
        
        payload = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "stream": False,  # OpenRouter doesn't support streaming with tools
            **kwargs
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._get_headers(),
            json=payload,
            timeout=120
        )
        
        if not response.ok:
            raise RuntimeError(f"OpenRouter error: {response.status_code} - {response.text}")
        
        # Parse non-streaming JSON response
        data = response.json()
        choices = data.get('choices', [])
        
        if not choices:
            return {'content': '', 'tool_calls': []}
        
        message = choices[0].get('message', {})
        content = message.get('content', '') or ''
        
        # Parse tool calls from response
        tool_calls = []
        raw_tool_calls = message.get('tool_calls', [])
        
        for tc in raw_tool_calls:
            func = tc.get('function', {})
            name = func.get('name', '')
            args_str = func.get('arguments', '{}')
            
            try:
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
            except json.JSONDecodeError:
                args = {}
            
            tool_call = {
                'id': tc.get('id', f'call_{name}'),
                'name': name,
                'arguments': args
            }
            tool_calls.append(tool_call)
            
            if on_tool_call:
                on_tool_call(name, args)
        
        # IMPORTANT: Only stream content when it's the FINAL answer (no tool calls)
        # When tool_calls are present, content is just "thinking" text - don't show to user
        if content and on_token and not tool_calls:
            for char in content:
                on_token(char)
        
        return {
            'content': content,
            'tool_calls': tool_calls
        }


# Default client instance (lazy loaded)
_default_client: Optional[OpenRouterClient] = None


def get_client() -> OpenRouterClient:
    """Get default OpenRouter client (singleton)"""
    global _default_client
    
    if _default_client is None:
        _default_client = OpenRouterClient()
    
    return _default_client

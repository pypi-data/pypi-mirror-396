"""
StackSense Module summarizer using Ollama for LLM-based code understanding.
Generates module descriptions, features, and live README.
"""
import json
import re
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path


try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

import requests


class ModuleSummarizer:
    """
    Summarizes code modules using Ollama LLM with dynamic model selection.
    
    Features:
    - Dynamic model selection (lightest for scanning, user's choice for chat)
    - LLM-guided cluster refinement
    - README integration
    - Live README generation
    """
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434/api/generate",
        model_name: Optional[str] = None,
        debug: bool = False
    ):
        """
        Initialize summarizer.
        
        Args:
            ollama_url: Ollama API endpoint
            model_name: Model to use (None = auto-select lightest)
            debug: Enable debug logging
        """
        self.ollama_url = ollama_url
        self.debug = debug
        self.readme_content = None
        
        # ⚡ DYNAMIC MODEL SELECTION
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = self._select_optimal_model()
    
    def _select_optimal_model(self) -> str:
        """
        Dynamically select the lightest Ollama model for fast scanning.
        
        Priority:
        1. Lightest model (by size) for speed
        2. 'qwen2.5:7b-instruct-q4_K_M' as fallback
        
        Returns:
            Model name to use
        """
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                
                if not models:
                    if self.debug:
                        print("[Summarizer] No Ollama models found, using default")
                    return 'qwen2.5:7b-instruct-q4_K_M'
                
                # Parse sizes and sort by smallest
                model_sizes = []
                for model in models:
                    name = model.get('name', '')
                    size = model.get('size', 0)
                    
                    # Convert size to GB for comparison
                    size_gb = size / (1024**3) if size else 999
                    model_sizes.append((name, size_gb, size))
                
                # Sort by size (smallest first)
                model_sizes.sort(key=lambda x: x[1])
                
                lightest = model_sizes[0]
                
                if self.debug:
                    print(f"[Summarizer] Available models:")
                    for name, size_gb, _ in model_sizes[:5]:
                        print(f"   • {name}: {size_gb:.1f}GB")
                    print(f"[Summarizer] Selected lightest: {lightest[0]} ({lightest[1]:.1f}GB)")
                
                # Tip if using a large model
                if lightest[1] > 3.0:  # > 3GB
                    print(f"\n💡 TIP: For faster scanning, consider installing a lighter model:")
                    print(f"   ollama pull phi3:mini  (2.2GB, ~10x faster)")
                    print(f"   Currently using: {lightest[0]} ({lightest[1]:.1f}GB)\n")
                
                return lightest[0]
            
        except Exception as e:
            if self.debug:
                print(f"[Summarizer] Model selection failed: {e}, using default")
        
        return 'qwen2.5:7b-instruct-q4_K_M'
    
    async def load_readme(self, workspace_path: str) -> Optional[str]:
        """
        Load and parse README.md from workspace.
        
        Args:
            workspace_path: Root workspace path
            
        Returns:
            README content or None
        """
        readme_paths = [
            Path(workspace_path) / 'README.md',
            Path(workspace_path) / 'readme.md',
            Path(workspace_path) / 'Readme.md',
        ]
        
        for readme_path in readme_paths:
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if self.debug:
                        print(f"[Summarizer] Loaded README: {readme_path}")
                    
                    self.readme_content = content
                    return content
                except Exception as e:
                    if self.debug:
                        print(f"[Summarizer] Failed to read README: {e}")
        
        return None
    
    async def _call_ollama(self, prompt: str, max_tokens: int = 150, retries: int = 3) -> str:
        """
        Call Ollama API for text generation with retries.
        
        Args:
            prompt: Prompt for the model
            max_tokens: Maximum response tokens (reduced from 500 to 150)
            retries: Number of retry attempts
            
        Returns:
            Generated text
        """
        import time
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.3,
                "top_p": 0.9
            }
        }
        
        if self.debug:
            print(f"[Summarizer] Calling Ollama (prompt len: {len(prompt)}, max_tokens: {max_tokens})...")
        
        for attempt in range(retries):
            try:
                if AIOHTTP_AVAILABLE:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            self.ollama_url,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=120)  # Increased from 30s
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                return data.get('response', '').strip()
                            else:
                                error = await response.text()
                                if self.debug:
                                    print(f"[Summarizer] Ollama HTTP {response.status}: {error[:100]}")
                                raise Exception(f"HTTP {response.status}")
                else:
                    # Fallback to sync requests
                    response = requests.post(
                        self.ollama_url,
                        json=payload,
                        timeout=120  # Increased from 30s
                    )
                    response.raise_for_status()
                    return response.json().get('response', '').strip()
            
            except (requests.exceptions.Timeout, 
                    requests.exceptions.ConnectionError,
                    aiohttp.ClientError if AIOHTTP_AVAILABLE else Exception) as e:
                
                if attempt == retries - 1:
                    # Final attempt failed
                    if self.debug:
                        print(f"[Summarizer] Ollama failed after {retries} attempts: {e}")
                    raise
                
                # Retry with backoff
                backoff = 5 * (attempt + 1)  # 5s, 10s, 15s
                if self.debug:
                    print(f"[Summarizer] Retry {attempt + 1}/{retries} after error: {type(e).__name__}")
                time.sleep(backoff)
            
            except Exception as e:
                if self.debug:
                    print(f"[Summarizer] Unexpected error: {e}")
                raise
        
        raise Exception("Ollama max retries exceeded")
    
    def _generate_heuristic_name(self, files: List[str]) -> str:
        """
        Generate module name from file patterns.
        
        Args:
            files: List of file paths
            
        Returns:
            Module name
        """
        # Extract common tokens from filenames
        stems = [Path(f).stem for f in files]
        
        # Find most common tokens
        token_counts = {}
        for stem in stems:
            tokens = stem.lower().replace('-', '_').split('_')
            for token in tokens:
                if len(token) > 2 and token not in ['test', 'spec', 'index']:
                    token_counts[token] = token_counts.get(token, 0) + 1
        
        if token_counts:
            # Get top 2 tokens
            sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
            top_tokens = [t[0] for t in sorted_tokens[:2]]
            
            # Capitalize and join
            name = ' '.join([t.capitalize() for t in top_tokens])
            
            # Add "System" or "Module" suffix
            if 'system' not in name.lower() and 'module' not in name.lower():
                name += ' System'
            
            return name
        
        # Fallback to folder name
        if files:
            folder = Path(files[0]).parent.name
            return f"{folder.replace('_', ' ').title()} Module"
        
        return "Unknown Module"
    
    async def summarize_module(
        self,
        cluster_name: str,
        files: List[str],
        slices: List[Any],
        dependencies: List[str],
        readme_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate module summary using Ollama with simplified, concise prompts.
        
        Returns:
            {
                'name': 'User Management',
                'description': 'Complete auth system with JWT...',
                'key_features': ['2FA', 'Role-based access'],
                'dependencies': [...],
                'confidence': 0.92,
                'files': [...]
            }
        """
        # ⚡ OPTIMIZATION: Limit to top 5 files, 1 sample, concise prompt
        file_list = '\n'.join([f"- {Path(f).name}" for f in files[:5]])
        if len(files) > 5:
            file_list += f"\n- ... and {len(files) - 5} more"
        
        # Get ONE code sample (first file, first 200 chars)
        code_sample = ""
        for s in slices[:1]:
            if hasattr(s, 'file_path') and s.file_path in files:
                sample = s.content[:200] if hasattr(s, 'content') else ""
                if sample:
                    code_sample = f"```\n{sample}\n```"
                    break
        
        # Limit dependencies
        deps_str = ', '.join([Path(d).name for d in dependencies[:3]]) if dependencies else 'None'
        
        # Concise prompt (< 1000 chars)
        prompt = f"""Summarize this code module concisely:

Files ({len(files)} total, top 5):
{file_list}

Sample code:
{code_sample if code_sample else 'No sample available'}

Dependencies: {deps_str}

Output JSON:
{{"name": "2-4 words", "description": "1 sentence max", "key_features": ["3 items max"]}}

JSON:"""
        
        # Call Ollama with reduced tokens
        try:
            if self.debug:
                print(f"[Summarizer] Generating summary for {len(files)} files (prompt: {len(prompt)} chars)...")
            
            response = await self._call_ollama(prompt, max_tokens=150)  # Reduced from 300
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                return {
                    'name': data.get('name', self._generate_heuristic_name(files)),
                    'description': data.get('description', 'No description available'),
                    'key_features': data.get('key_features', [])[:3],  # Max 3
                    'dependencies': dependencies,
                    'confidence': 0.85,
                    'files': files
                }
            else:
                raise ValueError("No JSON found in response")
        
        except Exception as e:
            if self.debug:
                print(f"[Summarizer] LLM summarization failed: {e}, using heuristic")
            
            # Fallback to heuristic
            return self._generate_heuristic_summary(files, dependencies)
    
    def _generate_heuristic_summary(self, files: List[str], dependencies: List[str] = None) -> Dict[str, Any]:
        """Generate summary using heuristics (fallback)"""
        return {
            'name': self._generate_heuristic_name(files),
            'description': f"Module containing {len(files)} related files",
            'key_features': [],
            'dependencies': dependencies or [],
            'confidence': 0.5,
            'files': files
        }
    
    async def refine_clusters(
        self,
        clusters: Dict[str, List[str]],
        slices: List[Any]
    ) -> Dict[str, List[str]]:
        """
        Use LLM to refine cluster assignments.
        
        Asks Ollama to review clusters and suggest merges/splits.
        
        Args:
            clusters: Current cluster assignments
            slices: All code slices
            
        Returns:
            Refined cluster assignments
        """
        if len(clusters) <= 1:
            return clusters  # No refinement needed
        
        # Build prompt
        cluster_summary = []
        for name, files in list(clusters.items())[:10]:  # Limit to 10 clusters
            file_list = ', '.join([Path(f).name for f in files[:5]])
            if len(files) > 5:
                file_list += f" + {len(files) - 5} more"
            cluster_summary.append(f"- {name}: {file_list}")
        
        prompt = f"""Review these code module clusters and suggest improvements:

{chr(10).join(cluster_summary)}

Should any clusters be:
1. Merged (too similar)?
2. Split (too diverse)?
3. Left as-is?

Respond with JSON:
{{
  "merges": [["cluster1", "cluster2"], ...],
  "splits": ["cluster_to_split", ...],
  "keep": ["cluster_name", ...]
}}

JSON:"""
        
        try:
            response = await self._call_ollama(prompt, max_tokens=200)
            
            # Extract JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                suggestions = json.loads(json_str)
                
                if self.debug:
                    print(f"[Summarizer] LLM refinement suggestions:")
                    print(f"   Merges: {suggestions.get('merges', [])}")
                    print(f"   Splits: {suggestions.get('splits', [])}")
                
                # Apply merges
                refined = dict(clusters)
                for merge_pair in suggestions.get('merges', []):
                    if len(merge_pair) == 2 and all(c in refined for c in merge_pair):
                        c1, c2 = merge_pair
                        refined[c1].extend(refined[c2])
                        del refined[c2]
                        if self.debug:
                            print(f"   Merged {c2} into {c1}")
                
                return refined
        
        except Exception as e:
            if self.debug:
                print(f"[Summarizer] Cluster refinement failed: {e}")
        
        return clusters  # Return original if refinement fails
    
    async def generate_live_readme(
        self,
        modules: Dict[str, Dict[str, Any]],
        workspace_path: str
    ) -> str:
        """
        Generate a "live README" summarizing all modules.
        
        Args:
            modules: Module summaries
            workspace_path: Workspace root path
            
        Returns:
            Markdown formatted live README
        """
        lines = [
            f"# {Path(workspace_path).name} - Live Analysis",
            "",
            f"**Auto-generated workspace analysis**",
            "",
            "## Modules Detected",
            ""
        ]
        
        # Sort modules by confidence
        sorted_modules = sorted(
            modules.items(),
            key=lambda x: x[1].get('confidence', 0),
            reverse=True
        )
        
        for idx, (name, info) in enumerate(sorted_modules, 1):
            confidence = info.get('confidence', 0)
            confidence_emoji = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "⚪"
            
            lines.append(f"### {idx}. {info['name']} {confidence_emoji}")
            lines.append(f"**Confidence:** {confidence:.0%}")
            lines.append(f"**Description:** {info['description']}")
            
            if info.get('key_features'):
                lines.append("**Key Features:**")
                for feature in info['key_features']:
                    lines.append(f"- {feature}")
            
            files = info.get('files', [])
            lines.append(f"**Files:** {len(files)}")
            for f in files[:5]:
                lines.append(f"  - `{Path(f).name}`")
            if len(files) > 5:
                lines.append(f"  - ... and {len(files) - 5} more")
            
            if info.get('dependencies'):
                deps = info['dependencies']
                lines.append(f"**Dependencies:** {', '.join([Path(d).name for d in deps[:3]])}")
            
            lines.append("")
        
        return '\n'.join(lines)

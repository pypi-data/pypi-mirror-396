"""
StackSense Repo Scanner
Lightning-fast workspace analyzer with semantic code understanding
"""
import os
import asyncio
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass


@dataclass
class CodeSlice:
    """Represents a semantic chunk of code"""
    file_path: str
    slice_type: str  # 'function', 'class', 'component', 'block'
    name: str
    start_line: int
    end_line: int
    content: str
    hash: str
    language: str


class RepoScanner:
    """Fast, intelligent workspace scanner"""
    
    # Whitelisted file extensions (code + DevOps)
    WHITELIST = {
        # Code
        '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', 
        '.kt', '.rs', '.cpp', '.h', '.cs', '.rb', '.php',
        # Config & Docs
        '.md', '.yaml', '.yml', '.json', '.toml', '.ini', '.conf',
        # DevOps & Infrastructure
        '.dockerfile', '.dockerignore', '.nginx', '.sh', '.bash',
        # Special files (no extension)
        'Dockerfile', 'docker-compose', 'Makefile', 'Jenkinsfile',
        'Vagrantfile', 'Procfile', '.env.example', 'requirements.txt',
        'package.json', 'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle'
    }
    
    # Blacklisted directories (skip these completely)
    BLACKLIST = {
        'node_modules', 'venv', 'env', '.env', 'target', 'dist', 
        'build', '.idea', '.git', '.next', '.cache', '__pycache__',
        '.pytest_cache', 'coverage', '.vscode', '.DS_Store'
    }
    
    def __init__(
        self,
        workspace_path: Path,
        cache_path: Optional[Path] = None,
        debug: bool = False,
        scan_model: Optional[str] = None  # Lightest model for scanning
    ):
        """
        Initialize repository scanner.
        
        Args:
            workspace_path: Root path of workspace to scan
            cache_path: Optional cache file path
            debug: Enable debug logging
            scan_model: Model to use for scanning (None = auto-select lightest)
        """
        self.workspace_path = Path(workspace_path)
        self.cache_path = cache_path or (Path.home() / '.stacksense' / 'scan_cache.json')
        self.debug = debug
        self.scan_model = scan_model  # Store for passing to ModuleSummarizer
        self.slices: List[CodeSlice] = []
        self.context_map: Dict[str, Any] = {}
        self.cached_hashes: Dict[str, str] = {}  # file_path -> hash
        
        # Load previous cache if exists
        self._load_previous_cache()
        
        # Load gitignore patterns
        self._load_gitignore()
    
    def _load_previous_cache(self):
        """Load previous scan cache for incremental scanning"""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r') as f:
                    data = json.load(f)
                    # Extract file hashes
                    for slice_data in data.get('slices', []):
                        file_path = slice_data.get('file_path')
                        file_hash = slice_data.get('hash')
                        if file_path and file_hash:
                            self.cached_hashes[file_path] = file_hash
                
                if self.debug:
                    print(f"[Scanner] Loaded {len(self.cached_hashes)} cached file hashes")
        except Exception as e:
            if self.debug:
                print(f"[Scanner] Failed to load cache: {e}")
    
    def _load_gitignore(self):
        """Parse .gitignore to auto-detect additional blacklist patterns"""
        gitignore_path = self.workspace_path / '.gitignore'
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith('#'):
                            # Handle common patterns
                            pattern = line.rstrip('/')
                            if pattern and not pattern.startswith('!'):
                                self.BLACKLIST.add(pattern)
                
                if self.debug:
                    print(f"[Scanner] Loaded .gitignore patterns: {len(self.BLACKLIST)} total")
            except Exception as e:
                if self.debug:
                    print(f"[Scanner] Failed to load .gitignore: {e}")
    
    def _should_skip_dir(self, dir_name: str) -> bool:
        """Check if directory should be skipped"""
        # Check blacklist
        if dir_name in self.BLACKLIST:
            return True
        # Skip hidden dirs (except intentional ones)
        if dir_name.startswith('.') and dir_name not in {'.github', '.vscode'}:
            return True
        return False
    
    def _should_include_file(self, file_path: Path) -> bool:
        """
        Check if file should be included in scan.
        Supports code files and DevOps configs.
        """
        # Check blacklist
        if any(part in self.BLACKLIST for part in file_path.parts):
            return False
        
        # Check extension
        ext = file_path.suffix.lower()
        if ext in self.WHITELIST:
            return True
        
        # Check special DevOps files (no extension or special names)
        filename = file_path.name.lower()
        devops_files = {
            'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'docker-compose.dev.yml', 'docker-compose.prod.yml',
            'makefile', 'jenkinsfile', 'vagrantfile', 'procfile',
            '.dockerignore', '.gitignore', '.env.example',
            'requirements.txt', 'package.json', 'cargo.toml',
            'go.mod', 'pom.xml', 'build.gradle', 'nginx.conf',
            'celery.py', 'wsgi.py', 'asgi.py', 'manage.py'
        }
        
        if filename in devops_files:
            return True
        
        # Check for docker-compose variants
        if filename.startswith('docker-compose') and ext in {'.yml', '.yaml'}:
            return True
        
        # Check for Kubernetes files
        if ext in {'.yml', '.yaml'} and any(k in filename for k in ['deployment', 'service', 'ingress', 'configmap', 'k8s']):
            return True
        
        # File size check (skip files > 1MB)
        try:
            if file_path.stat().st_size > 1_000_000:
                return False
        except:
            pass
        
        return False
    
    async def _discover_files(self) -> List[Path]:
        """
        Async file discovery with smart filtering.
        
        Returns:
            List of paths to relevant files
        """
        if self.debug:
            print(f"[Scanner] Discovering files in {self.workspace_path}")
        
        files = []
        
        # Use os.scandir for speed (faster than os.walk)
        def scan_dir(directory: Path) -> List[Path]:
            found = []
            try:
                with os.scandir(directory) as it:
                    for entry in it:
                        # Skip blacklisted directories immediately
                        if entry.is_dir():
                            if not self._should_skip_dir(entry.name):
                                found.extend(scan_dir(Path(entry.path)))
                        elif entry.is_file():
                            file_path = Path(entry.path)
                            if self._should_include_file(file_path):
                                found.append(file_path)
            except PermissionError:
                if self.debug:
                    print(f"[Scanner] Permission denied: {directory}")
            return found
        
        # Run in executor to avoid blocking
        loop = asyncio.get_running_loop()
        files = await loop.run_in_executor(None, scan_dir, self.workspace_path)
        
        if self.debug:
            print(f"[Scanner] Found {len(files)} relevant files")
        
        return files
    
    def _hash_content(self, content: str) -> str:
        """Generate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension and name"""
        ext = file_path.suffix.lower()
        filename = file_path.name.lower()
        
        # Extension-based detection
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.go': 'go',
            '.java': 'java',
            '.kt': 'kotlin',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c-header',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.md': 'markdown',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.toml': 'toml',
            '.ini': 'ini',
            '.conf': 'config',
            '.sh': 'shell',
            '.bash': 'bash',
        }
        
        if ext in lang_map:
            return lang_map[ext]
        
        # Filename-based detection (for files without extensions)
        if 'dockerfile' in filename:
            return 'dockerfile'
        elif 'docker-compose' in filename:
            return 'docker-compose'
        elif filename == 'makefile':
            return 'makefile'
        elif filename == 'jenkinsfile':
            return 'jenkinsfile'
        elif filename in {'procfile', 'vagrantfile'}:
            return filename
        elif 'requirements.txt' in filename:
            return 'requirements'
        elif 'package.json' in filename:
            return 'package-json'
        elif '.env' in filename:
            return 'env-file'
        
        return 'unknown'
    
    def _slice_python(self, content: str, file_path: str) -> List[CodeSlice]:
        """Slice Python code by functions and classes"""
        slices = []
        lines = content.split('\n')
        
        current_slice = None
        current_indent = -1
        
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            
            # Detect function or class definition
            if stripped.startswith('def ') or stripped.startswith('class '):
                # Save previous slice
                if current_slice:
                    current_slice['end_line'] = i - 1
                    current_slice['content'] = '\n'.join(lines[current_slice['start_line']-1:i-1])
                    slices.append(CodeSlice(
                        file_path=file_path,
                        slice_type=current_slice['type'],
                        name=current_slice['name'],
                        start_line=current_slice['start_line'],
                        end_line=current_slice['end_line'],
                        content=current_slice['content'],
                        hash=self._hash_content(current_slice['content']),
                        language='python'
                    ))
                
                # Start new slice
                indent = len(line) - len(stripped)
                is_class = stripped.startswith('class ')
                name = stripped.split('(')[0].replace('def ', '').replace('class ', '').strip(':')
                
                current_slice = {
                    'type': 'class' if is_class else 'function',
                    'name': name,
                    'start_line': i,
                    'end_line': i
                }
                current_indent = indent
        
        # Save final slice
        if current_slice:
            current_slice['end_line'] = len(lines)
            current_slice['content'] = '\n'.join(lines[current_slice['start_line']-1:])
            slices.append(CodeSlice(
                file_path=file_path,
                slice_type=current_slice['type'],
                name=current_slice['name'],
                start_line=current_slice['start_line'],
                end_line=current_slice['end_line'],
                content=current_slice['content'],
                hash=self._hash_content(current_slice['content']),
                language='python'
            ))
        
        return slices
    
    def _slice_javascript(self, content: str, file_path: str) -> List[CodeSlice]:
        """Slice JavaScript/TypeScript code by functions and exports"""
        slices = []
        lines = content.split('\n')
        
        # Simple heuristic: look for function/class/export definitions
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['function ', 'class ', 'export ', '=>']):
                # Create slice around this definition
                start = max(0, i - 5)
                end = min(len(lines), i + 20)
                slice_content = '\n'.join(lines[start:end])
                
                slices.append(CodeSlice(
                    file_path=file_path,
                    slice_type='function',
                    name=stripped[:50],  # First 50 chars as name
                    start_line=start + 1,
                    end_line=end,
                    content=slice_content,
                    hash=self._hash_content(slice_content),
                    language='javascript'
                ))
        
        return slices
    
    def _slice_by_language(self, content: str, file_path: str, language: str) -> List[CodeSlice]:
        """
        Slice code semantically based on language.
        
        Args:
            content: File content
            file_path: Path to file
            language: Programming language
            
        Returns:
            List of code slices
        """
        if language == 'python':
            return self._slice_python(content, file_path)
        elif language in ['javascript', 'typescript', 'react', 'react-typescript']:
            return self._slice_javascript(content, file_path)
        else:
            # Fallback: chunk by lines
            lines = content.split('\n')
            chunk_size = 50
            slices = []
            
            for i in range(0, len(lines), chunk_size):
                chunk = '\n'.join(lines[i:i+chunk_size])
                slices.append(CodeSlice(
                    file_path=file_path,
                    slice_type='block',
                    name=f"lines_{i+1}-{i+chunk_size}",
                    start_line=i + 1,
                    end_line=min(i + chunk_size, len(lines)),
                    content=chunk,
                    hash=self._hash_content(chunk),
                    language=language
                ))
            
            return slices
    
    async def _read_and_slice_file(self, file_path: Path) -> List[CodeSlice]:
        """
        Read file and slice into semantic chunks.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of code slices
        """
        try:
            # Read file
            loop = asyncio.get_running_loop()
            content = await loop.run_in_executor(
                None, 
                lambda: file_path.read_text(encoding='utf-8', errors='ignore')
            )
            
            # Detect language
            language = self._detect_language(file_path)
            
            # Slice content
            slices = self._slice_by_language(content, str(file_path), language)
            
            return slices
            
        except Exception as e:
            if self.debug:
                print(f"[Scanner] Error reading {file_path}: {e}")
            return []
    
    def _generate_context_map(self) -> Dict[str, Any]:
        """Generate high-level context map of the workspace"""
        context_map = {
            'workspace': str(self.workspace_path),  # Convert PosixPath to string
            'total_files': len(self.slices), # Changed from len(self.files_scanned) to len(self.slices) for consistency with original logic
            'languages': {},
            'frameworks': [],
            'patterns': {},  # New: detected code patterns
            'scan_timestamp': asyncio.get_event_loop().time() # Retained original timestamp logic
        }
        
        # Count languages
        for slice_obj in self.slices:
            lang = slice_obj.language
            context_map['languages'][lang] = context_map['languages'].get(lang, 0) + 1
        
        
        # Detect frameworks deterministically (no hallucinations!)
        from .framework_detector import detect_frameworks
        
        try:
            framework_categories = detect_frameworks(self.workspace_path, debug=self.debug)
            
            # Flatten categories into single list for backwards compatibility
            all_frameworks = []
            for category_frameworks in framework_categories.values():
                all_frameworks.extend(category_frameworks)
            
            context_map['frameworks'] = sorted(set(all_frameworks))
            
            if self.debug:
                print(f"[Scanner] Frameworks detected: {context_map['frameworks']}")
        
        except Exception as e:
            if self.debug:
                print(f"[Scanner] Framework detection failed: {e}")
            context_map['frameworks'] = []
        
        # Pattern detection (keep this - it's useful metadata)
        pattern_indicators = {
            'api_endpoints': ['@app.route', '@router.', 'app.get(', 'app.post(', 'api/', '/api/', '@api_view'],
            'database_models': ['class.*Model', 'models.', 'Schema', 'Table(', 'db.Model'],
            'authentication': ['auth', 'login', 'token', 'jwt', 'session', 'password', 'authenticate'],
            'error_handling': ['try:', 'except', 'catch', 'throw', 'raise'],
            'testing': ['test_', 'def test', 'it(', 'describe(', 'pytest', 'unittest', 'jest'],
            'async_code': ['async def', 'await ', 'asyncio', 'Promise'],
            'config': ['config', 'settings', 'env', 'dotenv', 'SECRET_KEY'],
            'logging': ['logger', 'logging', 'log.', 'console.log'],
            'caching': ['cache', 'redis', 'memcached', '@cache'],
            'websockets': ['websocket', 'socket.io', 'ws://'],
            'graphql': ['graphql', 'gql', 'GraphQLSchema'],
            'rest_api': ['rest', 'restful', 'api', 'endpoint'],
        }
        
        patterns_found = {key: 0 for key in pattern_indicators.keys()}
        
        for slice_obj in self.slices:
            content_lower = slice_obj.content.lower()
            
            # Check patterns
            for pattern, indicators in pattern_indicators.items():
                if any(ind.lower() in content_lower for ind in indicators):
                    patterns_found[pattern] += 1
        
        context_map['patterns'] = {k: v for k, v in patterns_found.items() if v > 0}
        
        return context_map
    
    async def scan(
        self,
        progressive: bool = False,
        max_files: Optional[int] = None,
        use_cache: bool = True  # NEW: Enable caching
    ) -> Dict[str, Any]:
        """
        Perform full 3-stage workspace scan.
        
        Args:
            progressive: Use progressive scanning (priority files first)
            max_files: Limit files to scan (for huge repos)
            use_cache: Use cached results if available (default: True)
            
        Returns:
            Context map with modules, clusters, and analysis
        """
        
        # ==== CACHE CHECK ====
        if use_cache:
            from .cache_manager import WorkspaceCache
            cache = WorkspaceCache(self.workspace_path, debug=self.debug)
            cached_data = cache.load()
            
            if cached_data:
                if self.debug:
                    print("✅ Using cached workspace analysis (skipping scan)")
                return cached_data
        
        # ==== FULL SCAN (cache miss or disabled) ====
        if self.debug:
            print(f"🔍 Scanning workspace: {self.workspace_path}")
            print(f"   Progressive: {progressive}")
            if max_files:
                print(f"   Max files: {max_files}")
        
        # ============================================
        # Stage 1: Heuristic Scan (0.5s)
        # ============================================
        start_time = asyncio.get_event_loop().time()
        
        # Discover files
        files = await self._discover_files()
        
        # Progressive mode: prioritize important files
        if progressive and len(files) > (max_files or 100):
            files = await self._prioritize_files(files, max_files or 100)
            if self.debug:
                print(f"[Scanner] Progressive mode: Selected {len(files)} priority files")
        elif max_files and len(files) > max_files:
            files = files[:max_files]
        
        # Read and slice files in parallel
        batch_size = 20
        for i in range(0, len(files), batch_size):
            batch = files[i:i+batch_size]
            tasks = [self._read_and_slice_file(f) for f in batch]
            results = await asyncio.gather(*tasks)
            
            for slices_list in results:
                self.slices.extend(slices_list)
        
        if self.debug:
            stage1_time = asyncio.get_event_loop().time() - start_time
            print(f"[Scanner] Stage 1 complete: {len(self.slices)} slices in {stage1_time:.2f}s")
        
        # ============================================
        # Stage 2: TF-IDF Semantic Analysis (0.5-1s)
        # ============================================
        semantic_result = None
        stage2_start = asyncio.get_event_loop().time()
        
        try:
            from .semantic_analyzer import SemanticAnalyzer
            
            analyzer = SemanticAnalyzer(
                use_lsa=True,
                lsa_components=200,
                similarity_weights=(0.6, 0.2, 0.2),
                debug=self.debug
            )
            
            semantic_result = await analyzer.analyze_files(
                self.slices,
                use_topology=True
            )
            
            if self.debug:
                stage2_time = asyncio.get_event_loop().time() - stage2_start
                n_clusters = len(semantic_result.get('clusters', {}))
                print(f"[Scanner] Stage 2 complete: {n_clusters} clusters in {stage2_time:.2f}s")
        
        except Exception as e:
            if self.debug:
                print(f"[Scanner] Stage 2 failed: {e}")
                import traceback
                traceback.print_exc()
        
        # ============================================
        # Stage 3: LLM Refinement (OPTIMIZED)
        # ============================================
        modules = {}
        live_readme = ""
        stage3_start = asyncio.get_event_loop().time()
        
        if semantic_result and semantic_result.get('clusters'):
            try:
                # ⚡ PRE-CHECK: Verify Ollama is available
                ollama_available = False
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        model_names = [m['name'] for m in models]
                        if self.debug:
                            print(f"[Scanner] Ollama ready - Models: {', '.join(model_names[:3])}")
                        ollama_available = True
                    else:
                        if self.debug:
                            print(f"[Scanner] Ollama HTTP {response.status_code} - Using heuristics")
                except Exception as e:
                    if self.debug:
                        print(f"[Scanner] Ollama check failed: {e} - Using heuristics")
                
                from .module_summarizer import ModuleSummarizer
                summarizer = ModuleSummarizer(
                    debug=self.debug,
                    model_name=self.scan_model  # Use lightest model for scanning
                )
                
                # Load README
                await summarizer.load_readme(str(self.workspace_path))
                
                clusters = semantic_result['clusters']
                dependencies = semantic_result.get('dependencies', {})
                
                # ⚡ OPTIMIZATION: Filter clusters - only LLM for ≥3 files
                large_clusters = {name: files for name, files in clusters.items() if len(files) >= 3}
                small_clusters = {name: files for name, files in clusters.items() if len(files) < 3}
                
                if self.debug:
                    print(f"[Scanner] {len(large_clusters)} large clusters (LLM), {len(small_clusters)} small (heuristic)")
                
                if ollama_available and large_clusters:
                    # ⚡ BATCHING: Process 5 clusters per LLM call
                    batch_size = 5
                    cluster_items = list(large_clusters.items())
                    
                    async def process_batch(batch_clusters):
                        """Process a batch of clusters in one LLM call"""
                        batch_modules = {}
                        
                        # Build multi-cluster prompt
                        cluster_prompts = []
                        for cluster_name, files in batch_clusters:
                            cluster_slices = [s for s in self.slices if s.file_path in files]
                            
                            # Get dependencies
                            cluster_deps = set()
                            for file in files:
                                if file in dependencies:
                                    cluster_deps.update(dependencies[file])
                            cluster_deps = [d for d in cluster_deps if d not in files]
                            
                            # Minimal file list (top 3)
                            file_list = ', '.join([Path(f).name for f in files[:3]])
                            if len(files) > 3:
                                file_list += f" +{len(files)-3}"
                            
                            # One code sample (first 100 chars)
                            sample = ""
                            for s in cluster_slices[:1]:
                                if hasattr(s, 'content'):
                                    sample = s.content[:100].replace('\n', ' ')
                                    break
                            
                            cluster_prompts.append(
                                f"Cluster {cluster_name}:\n"
                                f"Files: {file_list}\n"
                                f"Sample: {sample}\n"
                                f"Deps: {', '.join([Path(d).name for d in cluster_deps[:2]]) if cluster_deps else 'None'}"
                            )
                        
                        # Combined prompt with stricter JSON instructions
                        full_prompt = f"""Analyze these {len(batch_clusters)} code modules. For each, provide:
- name: 2-3 words (e.g., "User Management")
- description: 1 sentence
- key_features: 2-3 items

{chr(10).join(cluster_prompts)}

IMPORTANT: Output ONLY valid JSON array, no extra text.
Format:
[
  {{"cluster": "cluster_name", "name": "Module Name", "description": "Brief description", "key_features": ["feature1", "feature2"]}},
  ...
]

JSON:"""
                        
                        try:
                            response = await summarizer._call_ollama(full_prompt, max_tokens=400)  # Increased from 300
                            
                            # Clean response - remove markdown, extra text
                            response = response.strip()
                            if '```json' in response.lower():
                                # Extract from markdown code block
                                start = response.lower().find('```json') + 7
                                end = response.find('```', start)
                                if end > start:
                                    response = response[start:end].strip()
                            elif '```' in response:
                                # Generic code block
                                start = response.find('```') + 3
                                end = response.find('```', start)
                                if end > start:
                                    response = response[start:end].strip()
                            
                            # Parse JSON array
                            json_start = response.find('[')
                            json_end = response.rfind(']') + 1
                            
                            if json_start >= 0 and json_end > json_start:
                                import json
                                import re
                                
                                json_str = response[json_start:json_end]
                                
                                # Try to fix common JSON issues
                                # Replace single quotes with double quotes
                                json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
                                json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
                                
                                # Handle truncated arrays (e.g., [...) by attempting to close them
                                if json_str.count('[') > json_str.count(']'):
                                    # Count unclosed brackets and add closing ones
                                    unclosed = json_str.count('[') - json_str.count(']')
                                    json_str = json_str.rstrip(',') + ']' * unclosed
                                
                                # Handle truncated objects
                                if json_str.count('{') > json_str.count('}'):
                                    unclosed = json_str.count('{') - json_str.count('}')
                                    json_str = json_str.rstrip(',') + '}' * unclosed
                                
                                try:
                                    data = json.loads(json_str)
                                except json.JSONDecodeError as je:
                                    if self.debug:
                                        print(f"[Scanner] JSON parse error: {je}")
                                        print(f"[Scanner] Problematic JSON: {json_str[:200]}...")
                                    raise
                                
                                # Process valid JSON
                                for item in data:
                                    orig_name = item.get('cluster', '')
                                    if orig_name in dict(batch_clusters):
                                        files = dict(batch_clusters)[orig_name]
                                        cluster_deps = set()
                                        for file in files:
                                            if file in dependencies:
                                                cluster_deps.update(dependencies[file])
                                        cluster_deps = [d for d in cluster_deps if d not in files]
                                        
                                        batch_modules[item['name']] = {
                                            'name': item['name'],
                                            'description': item.get('description', ''),
                                            'key_features': item.get('key_features', [])[:3],
                                            'dependencies': cluster_deps,
                                            'confidence': 0.85,
                                            'files': files
                                        }
                            else:
                                raise ValueError("No JSON array found in response")
                            
                            return batch_modules
                        
                        except Exception as e:
                            if self.debug:
                                print(f"[Scanner] Batch LLM failed: {e}")
                                print(f"[Scanner] Using heuristics for {len(batch_clusters)} clusters")
                            # Fallback to heuristics for this batch
                            for cluster_name, files in batch_clusters:
                                cluster_deps = set()
                                for file in files:
                                    if file in dependencies:
                                        cluster_deps.update(dependencies[file])
                                cluster_deps = [d for d in cluster_deps if d not in files]
                                
                                summary = summarizer._generate_heuristic_summary(files, cluster_deps)
                                batch_modules[summary['name']] = summary
                            
                            return batch_modules
                    
                    # ⚡ PARALLEL: Run batches concurrently
                    batches = [cluster_items[i:i+batch_size] for i in range(0, len(cluster_items), batch_size)]
                    
                    if self.debug:
                        print(f"[Scanner] Processing {len(batches)} batches in parallel...")
                    
                    tasks = [process_batch(batch) for batch in batches]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Merge results
                    for result in batch_results:
                        if isinstance(result, Exception):
                            if self.debug:
                                print(f"[Scanner] Batch error: {result}")
                        else:
                            modules.update(result)
                
                else:
                    # Ollama not available - use heuristics for large clusters
                    if self.debug and large_clusters:
                        print(f"[Scanner] Generating {len(large_clusters)} heuristic summaries...")
                    
                    for cluster_name, files in large_clusters.items():
                        cluster_deps = set()
                        for file in files:
                            if file in dependencies:
                                cluster_deps.update(dependencies[file])
                        cluster_deps = [d for d in cluster_deps if d not in files]
                        
                        summary = summarizer._generate_heuristic_summary(files, cluster_deps)
                        modules[summary['name']] = summary
                
                # Always use heuristics for small clusters
                for cluster_name, files in small_clusters.items():
                    cluster_deps = set()
                    for file in files:
                        if file in dependencies:
                            cluster_deps.update(dependencies[file])
                    cluster_deps = [d for d in cluster_deps if d not in files]
                    
                    summary = summarizer._generate_heuristic_summary(files, cluster_deps)
                    modules[summary['name']] = summary
                
                # Generate live README
                if modules:
                    live_readme = await summarizer.generate_live_readme(
                        modules,
                        str(self.workspace_path)
                    )
                
                if self.debug:
                    stage3_time = asyncio.get_event_loop().time() - stage3_start
                    print(f"[Scanner] Stage 3 complete: {len(modules)} modules in {stage3_time:.2f}s")
            
            except Exception as e:
                if self.debug:
                    print(f"[Scanner] Stage 3 failed: {e}")
                    import traceback
                    traceback.print_exc()
        
        # ============================================
        # Stage 2.5: Code Extraction (NEW - Phase 2!)
        # ============================================
        if self.debug:
            print("[Scanner] Extracting code structures...")
        
        try:
            from .code_extractor import extract_code_structures
            
            # Extract code details from modules
            modules_with_code = extract_code_structures(
                self.workspace_path,
                modules,
                debug=self.debug
            )
            
            if self.debug:
                extract_count = sum(1 for m in modules_with_code.values() 
                                  if isinstance(m, dict) and 'code_extracts' in m)
                print(f"[Scanner] Extracted code from {extract_count}/{len(modules)} modules")
            
            # Use enhanced modules
            modules = modules_with_code
        
        except Exception as e:
            if self.debug:
                print(f"[Scanner] Code extraction failed: {e}")
                import traceback
                traceback.print_exc()
        
        # ============================================
        # Generate Context Map
        # ============================================
        self.context_map = self._generate_context_map()
        
        # Add stage 2 & 3 results
        self.context_map['modules'] = modules
        self.context_map['live_readme'] = live_readme
        self.context_map['semantic_analysis'] = {
            'clusters': semantic_result.get('clusters', {}) if semantic_result else {},
            'dependencies': semantic_result.get('dependencies', {}) if semantic_result else {},
            'topology_groups': semantic_result.get('topology_groups', {}) if semantic_result else {},
            'confidence_scores': semantic_result.get('confidence_scores', {}) if semantic_result else {}
        }
        
        # Save to cache
        self._save_cache()
        
        # ==== SAVE TO WORKSPACE CACHE ====
        if use_cache:
            from .cache_manager import WorkspaceCache
            cache = WorkspaceCache(self.workspace_path, debug=self.debug)
            cache.save(self.context_map)
        
        total_time = asyncio.get_event_loop().time() - start_time
        if self.debug:
            print(f"[Scanner] Total scan time: {total_time:.2f}s")
        
        return self.context_map
    
    async def _prioritize_files(self, files: List[Path], limit: int) -> List[Path]:
        """
        Prioritize files for progressive scanning.
        
        Priority:
        1. README and docs
        2. Entry points (main.py, index.js, app.py)
        3. Recently modified (via git or mtime)
        4. Models, views, controllers
        5. Everything else
        
        Args:
            files: All discovered files
            limit: Max files to return
            
        Returns:
            Prioritized file list
        """
        import subprocess
        from datetime import datetime
        
        scored_files = []
        
        for file_path in files:
            score = 0
            name_lower = file_path.name.lower()
            path_str = str(file_path).lower()
            
            # Priority 1: Documentation
            if name_lower in ['readme.md', 'readme.rst', 'index.md']:
                score += 100
            elif name_lower.endswith(('.md', '.rst', '.txt')) and 'doc' in path_str:
                score += 50
            
            # Priority 2: Entry points
            if name_lower in ['main.py', 'app.py', '__main__.py', 'index.js', 
                             'index.ts', 'app.js', 'server.py', 'manage.py']:
                score += 80
            
            # Priority 3: Core patterns
            if any(p in path_str for p in ['/models/', '/views/', '/controllers/', 
                                            '/routes/', '/api/', '/services/']):
                score += 40
            
            # Priority 4: Configuration
            if name_lower in ['settings.py', 'config.py', 'package.json', 
                             'tsconfig.json', 'setup.py']:
                score += 30
            
            # Priority 5: Recent modifications (git or mtime)
            try:
                # Try git first
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%ct', '--', str(file_path)],
                    cwd=str(self.workspace_path),
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0 and result.stdout.strip():
                    timestamp = int(result.stdout.strip())
                    days_old = (datetime.now().timestamp() - timestamp) / 86400
                    if days_old < 7:
                        score += 20
                    elif days_old < 30:
                        score += 10
            except:
                # Fallback to mtime
                try:
                    mtime = file_path.stat().st_mtime
                    days_old = (datetime.now().timestamp() - mtime) / 86400
                    if days_old < 7:
                        score += 15
                    elif days_old < 30:
                        score += 5
                except:
                    pass
            
            scored_files.append((score, file_path))
        
        # Sort by score and return top N
        scored_files.sort(reverse=True, key=lambda x: x[0])
        return [f for _, f in scored_files[:limit]]
    
    def _save_cache(self):
        """Save scan results to JSON cache"""
        cache_data = {
            'context_map': self.context_map,
            'slices': [
                {
                    'file_path': s.file_path,
                    'type': s.slice_type,
                    'name': s.name,
                    'start_line': s.start_line,
                    'end_line': s.end_line,
                    'hash': s.hash,
                    'language': s.language,
                    'content_preview': s.content[:200]  # First 200 chars only
                }
                for s in self.slices[:100]  # Only save top 100 slices
            ]
        }
        
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            if self.debug:
                print(f"[Scanner] Cache saved to {self.cache_path}")
        except Exception as e:
            if self.debug:
                print(f"[Scanner] Failed to save cache: {e}")
    
    def find_relevant_slices(self, query: str, max_results: int = 5) -> List[CodeSlice]:
        """
        Find code slices relevant to query.
        
        Args:
            query: Search query
            max_results: Max number of results
            
        Returns:
            List of relevant code slices
        """
        query_lower = query.lower()
        results = []
        
        for slice in self.slices:
            # Simple relevance scoring
            score = 0
            if query_lower in slice.name.lower():
                score += 10
            if query_lower in slice.content.lower():
                score += 5
            if query_lower in slice.file_path.lower():
                score += 3
            
            if score > 0:
                results.append((score, slice))
        
        # Sort by score and return top results
        results.sort(reverse=True, key=lambda x: x[0])
        return [slice for _, slice in results[:max_results]]

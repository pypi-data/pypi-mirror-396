"""
AI-Guided Reader - On-Demand File Reading
==========================================
Claude Code-style approach: AI decides which files to read per query.
No pre-parsing, reads only what's needed.
"""
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio


class AIGuidedReader:
    """
    AI-guided on-demand file reading with intelligent slicing.
    AI decides which files to read, SliceFilterPipeline extracts relevant parts.
    """
    
    def __init__(self, repo_path: Path, file_index: Dict, model, debug: bool = False):
        self.repo_path = Path(repo_path)
        self.file_index = file_index
        self.model = model  # OllamaIntegration instance
        self.debug = debug
    
    async def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Answer query using AI-guided file selection.
        
        Args:
            query: User's question about the codebase
        
        Returns:
            {
                'answer': str,
                'sources': List[str],  # Files that were read
                'confidence': float
            }
        """
        
        if self.debug:
            print(f"[AIGuidedReader] Processing query: {query}")
        
        # Step 1: AI plans the search strategy
        search_strategy = await self._ai_plan_search(query)
        
        if self.debug:
            print(f"[AIGuidedReader] AI search strategy: {search_strategy.get('focus', 'general')}")
        
        # NEW Step 2: Grep search for keywords (VSCode-like)
        keyword_matches = await self._grep_search_keywords(search_strategy)
        
        if self.debug:
            print(f"[AIGuidedReader] Grep found {len(keyword_matches)} files with keyword matches")
        
        # Step 3: AI selects files (from grep results - proven relevant!)
        file_paths = await self._ai_select_files(query, search_strategy, keyword_matches)
        
        if self.debug:
            print(f"[AIGuidedReader] AI selected {len(file_paths)} files to read")
        
        # Step 4: Read files with intelligent slicing (using strategy keywords)
        file_contents = await self._read_files(file_paths, query, search_strategy)
        
        if self.debug:
            print(f"[AIGuidedReader] Successfully processed {len(file_contents)} files")
        
        # Step 4: AI Answer with file context
        answer_data = await self._ai_answer(query, file_contents)
        
        return answer_data
    
    async def _ai_plan_search(self, query: str) -> Dict[str, Any]:
        """
        AI plans search strategy with DIVERSE keywords.
        Generates primary keywords + synonyms + context-aware alternatives.
        """
        
        # Get framework context for smarter keywords
        frameworks_str = ', '.join(self.file_index.get('frameworks', {}).get('backend', [])) + ', ' + \
                        ', '.join(self.file_index.get('frameworks', {}).get('frontend', []))
        
        planning_prompt = f"""You are planning a code search strategy.

USER QUERY: "{query}"

REPOSITORY CONTEXT:
- Languages: {', '.join(self.file_index['languages'].keys())}
- Frameworks: {frameworks_str}

TASK: Generate a DIVERSE search strategy with multiple keyword variations.

IMPORTANT: Generate MANY keywords including:
1. Primary keywords from the query
2. Synonyms (e.g., "user" → "admin", "account", "profile")
3. Technical terms (e.g., "database" → "postgres", "mysql", "db", "connection")
4. Framework-specific (e.g., if Django: "User.objects", "models.py")

OUTPUT (JSON format):
{{
  "focus": "Brief description",
  "keywords": ["main1", "main2", "synonym1", "synonym2", "technical1", "technical2"],
  "file_patterns": ["pattern1", "pattern2"],
  "what_to_find": "Specific things to look for"
}}

EXAMPLE for "user roles":
{{
  "focus": "user authorization system",
  "keywords": ["user", "role", "roles", "admin", "superuser", "permissions", "groups", "access", "is_staff", "account"],
  "file_patterns": ["models", "auth", "permissions", "user"],
  "what_to_find": "User model definitions, role/permission systems"
}}

EXAMPLE for "database connection":
{{
  "focus": "database configuration",
  "keywords": ["database", "db", "postgres", "postgresql", "mysql", "connection", "connect", "engine", "host", "port"],
  "file_patterns": ["settings", "config", ".env", "database"],
  "what_to_find": "Database config, connection strings"
}}

YOUR STRATEGY (JSON only, include 8-15 diverse keywords):"""

        try:
            response = await self.model.generate(
                prompt=planning_prompt,
                max_tokens=400,
                temperature=0.3  # Slightly higher for diversity
            )
            
            # Parse JSON
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                strategy = json.loads(json_match.group())
                
                # Ensure we have enough keywords
                if len(strategy.get('keywords', [])) < 5:
                    # Fallback: add basic synonyms
                    strategy['keywords'] = self._expand_keywords(query, strategy.get('keywords', []))
                
                return strategy
            
        except Exception as e:
            if self.debug:
                print(f"[AIGuidedReader] Strategy planning failed: {e}")
        
        # Fallback with keyword expansion
        words = query.lower().split()
        base_keywords = [w for w in words if len(w) > 3]
        expanded_keywords = self._expand_keywords(query, base_keywords)
        
        return {
            'focus': 'general',
            'keywords': expanded_keywords,
            'file_patterns': [],
            'what_to_find': query
        }
    
    def _expand_keywords(self, query: str, base_keywords: List[str]) -> List[str]:
        """Expand keywords with common synonyms and related terms"""
        expanded = set(base_keywords)
        query_lower = query.lower()
        
        # Common synonyms mapping
        synonyms = {
            'user': ['admin', 'account', 'profile', 'superuser', 'member'],
            'role': ['permission', 'access', 'group', 'privilege'],
            'payment': ['billing', 'transaction', 'charge', 'invoice'],
            'database': ['db', 'postgres', 'postgresql', 'mysql', 'sqlite'],
            'connection': ['connect', 'link', 'socket', 'endpoint'],
            'api': ['endpoint', 'route', 'view', 'controller'],
            'auth': ['authentication', 'authorization', 'login', 'signin'],
        }
        
        # Add synonyms for base keywords
        for keyword in base_keywords:
            if keyword in synonyms:
                expanded.update(synonyms[keyword])
        
        # Add query-specific terms
        for term, alternatives in synonyms.items():
            if term in query_lower:
                expanded.update(alternatives)
        
        return list(expanded)[:15]  # Limit to top 15 keywords
    
    async def _grep_search_keywords(self, strategy: Dict[str, Any]) -> Dict[str, int]:
        """
        Multi-tool grep search: pss → pygrep → pure Python fallback.
        Returns files with match counts - proof they're relevant!
        """
        import subprocess
        from concurrent.futures import ThreadPoolExecutor
        
        keywords = strategy.get('keywords', [])
        if not keywords:
            return {}
        
        if self.debug:
            print(f"[AIGuidedReader] Searching for keywords: {keywords}")
        
        file_matches = {}  # file → total match count
        
        for keyword in keywords[:5]:  # Top 5 keywords
            try:
                # Try 1: pss (Python-based, installed via pip)
                try:
                    result = subprocess.run(
                        ['pss', '--nocolor', '--count', keyword],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        self._parse_grep_results(result.stdout, file_matches)
                        if self.debug:
                            print(f"[AIGuidedReader] pss found matches for '{keyword}'")
                        continue
                
                except FileNotFoundError:
                    pass  # pss not available
                
                # Try 2: pygrep (Python-based, installed via pip)
                try:
                    result = subprocess.run(
                        ['pygrep', '-c', keyword],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        self._parse_grep_results(result.stdout, file_matches)
                        if self.debug:
                            print(f"[AIGuidedReader] pygrep found matches for '{keyword}'")
                        continue
                
                except FileNotFoundError:
                    pass  # pygrep not available
                
                # Try 3: Pure Python fallback (always works!)
                if self.debug:
                    print(f"[AIGuidedReader] Using pure Python search for '{keyword}'")
                
                python_results = self._pure_python_grep(keyword)
                for file_path, count in python_results.items():
                    file_matches[file_path] = file_matches.get(file_path, 0) + count
            
            except Exception as e:
                if self.debug:
                    print(f"[AIGuidedReader] Search failed for '{keyword}': {e}")
        
        # Sort by match count (most relevant first)
        sorted_matches = dict(sorted(file_matches.items(), key=lambda x: x[1], reverse=True))
        
        # Limit to top 20 files
        top_matches = dict(list(sorted_matches.items())[:20])
        
        if self.debug:
            print(f"[AIGuidedReader] Found {len(top_matches)} files with matches")
            if top_matches:
                print(f"[AIGuidedReader] Top match: {list(top_matches.items())[0]}")
        
        return top_matches
    
    def _parse_grep_results(self, output: str, file_matches: dict):
        """Parse grep-style output: file:count format"""
        for line in output.strip().split('\n'):
            if ':' in line:
                parts = line.rsplit(':', 1)
                if len(parts) == 2:
                    file_path = parts[0].lstrip('./')
                    try:
                        count = int(parts[1])
                        if count > 0:
                            file_matches[file_path] = file_matches.get(file_path, 0) + count
                    except ValueError:
                        pass
    
    def _pure_python_grep(self, keyword: str) -> dict:
        """Fast pure Python grep using threading - uses project's tracked files only!"""
        from concurrent.futures import ThreadPoolExecutor
        
        results = {}
        keyword_lower = keyword.lower()
        
        def search_file(file_path_str):
            try:
                file_path = self.repo_path / file_path_str
                
                # Skip large/binary files
                if not file_path.exists() or file_path.stat().st_size > 1_000_000:  # Skip files >1MB
                    return None
                
                content = file_path.read_text(errors='ignore').lower()
                count = content.count(keyword_lower)
                
                if count > 0:
                    return (file_path_str, count)
            except:
                pass
            return None
        
        # Use ONLY git-tracked files from index (respects .gitignore automatically!)
        tracked_files = self.file_index.get('files', [])
        
        # Search in parallel (fast!)
        with ThreadPoolExecutor(max_workers=8) as executor:
            for result in executor.map(search_file, tracked_files):
                if result:
                    results[result[0]] = result[1]
        
        return results
    
    def _get_framework_skip_patterns(self) -> list:
        """Get skip patterns based on DETECTED frameworks - fully dynamic!"""
        skip = []
        frameworks = self.file_index.get('frameworks', {})
        backend = frameworks.get('backend', [])
        frontend = frameworks.get('frontend', [])
        
        # Backend framework noise
        if 'Django' in backend or 'Django REST Framework' in backend:
            skip.extend(['staticfiles/', 'static/admin/', 'migrations/'])
        
        if 'Flask' in backend:
            skip.extend(['static/', '__pycache__/'])
        
        # Frontend framework noise  
        if 'Next.js' in frontend or 'React' in frontend:
            skip.extend(['.next/', 'node_modules/', 'dist/', 'build/'])
        
        if 'Vue' in frontend:
            skip.extend(['dist/', 'node_modules/'])
        
        # Build artifacts (language-agnostic)
        skip.extend(['.git/', '__pycache__/', '.DS_Store'])
        
        if self.debug and skip:
            print(f"[AIGuidedReader] Skipping framework noise: {skip[:5]}...")
        
        return skip
    
    async def _ai_select_files(self, query: str, strategy: Dict[str, Any], keyword_matches: Dict[str, int]) -> List[str]:
        """AI decides which files are relevant using grep results - proven relevant!"""
        
        # Build context for AI
        context = self._build_planning_context()
        
        # Use strategy keywords and patterns
        keywords_str = ', '.join(strategy.get('keywords', []))
        patterns_str = ', '.join(strategy.get('file_patterns', []))
        
        # Format grep results for AI
        if keyword_matches:
            grep_results = "\n".join([
                f"  {file}: {count} matches" 
                for file, count in list(keyword_matches.items())[:15]
            ])
        else:
            grep_results = "  (no keyword matches found - will search manually)"
        
        planning_prompt = f"""You are helping analyze a codebase.

REPOSITORY CONTEXT:
- Total files: {self.file_index['total_files']}
- Languages: {', '.join(self.file_index['languages'].keys())}
- Frameworks: {self._format_frameworks()}

USER QUERY: "{query}"

SEARCH STRATEGY:
- Focus: {strategy.get('focus', 'general')}
- Keywords: {keywords_str}
- File patterns: {patterns_str}

GREP SEARCH RESULTS (files containing keywords):
{grep_results}

TASK: Select 5-10 most relevant files from the grep results above.
These files are PROVEN to contain the keywords, so choose confidently!

OUTPUT FORMAT: Just file paths, one per line.
EXAMPLE:
Telios_Backend/settings.py
Telios_Backend/.env
"""
        
        try:
            # Get AI response
            response = await self.model.generate(
                prompt=planning_prompt,
                max_tokens=500,
                temperature=0.1  # Low temperature for focused selection
            )
            
            # Parse file paths
            lines = [line.strip() for line in response.strip().split('\n')]
            file_paths = [line for line in lines if line and not line.startswith('#')]
            
            # Validate paths exist in index
            valid_paths = []
            for path in file_paths[:10]:  # Limit to 10
                # Try exact match
                if path in self.file_index['files']:
                    valid_paths.append(path)
                else:
                    # Try fuzzy match
                    matches = [f for f in self.file_index['files'] if path in f or Path(f).name in path]
                    if matches:
                        valid_paths.append(matches[0])
            
            if not valid_paths:
                # Fallback: use keyword-based selection
                valid_paths = self._fallback_file_selection(query)
            
            return valid_paths[:10]
        
        except Exception as e:
            if self.debug:
                print(f"[AIGuidedReader] AI selection failed: {e}, using fallback")
            return self._fallback_file_selection(query)
    
    def _fallback_file_selection(self, query: str) -> List[str]:
        """Fallback file selection using keywords"""
        query_lower = query.lower()
        keywords = query_lower.split()
        
        scored_files = []
        
        for file_path in self.file_index['files']:
            # Skip non-source files
            if any(skip in file_path.lower() for skip in ['test', 'spec', '__pycache__', 'node_modules']):
                continue
            
            # Score based on keyword matches
            score = 0
            file_lower = file_path.lower()
            
            for keyword in keywords:
                if keyword in file_lower:
                    score += 10
                if keyword in Path(file_path).stem:  # In filename
                    score += 20
            
            if score > 0:
                scored_files.append((score, file_path))
        
        # Return top 10
        scored_files.sort(reverse=True)
        return [path for _, path in scored_files[:10]]
    
    async def _read_files(self, file_paths: List[str], query: str, strategy: Dict[str, Any]) -> Dict[str, str]:
        """Read files with keyword-based slice extraction using AI strategy"""
        contents = {}
        
        # Use strategy keywords (more focused than query words)
        keywords = strategy.get('keywords', [])
        if not keywords:
            # Fallback to query words
            keywords = [w.lower() for w in query.split() if len(w) > 3]
        
        if self.debug:
            print(f"[AIGuidedReader] Using keywords: {keywords}")
        
        for file_path in file_paths:
            try:
                full_path = self.repo_path / file_path
                
                if full_path.exists() and full_path.is_file():
                    # Read full content
                    full_content = full_path.read_text(errors='ignore')
                    lines = full_content.split('\n')
                    
                    # Extract relevant slices based on strategy keywords
                    relevant_slices = []
                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        
                        # Check if line contains keywords
                        if any(kw in line_lower for kw in keywords):
                            # Extract context: 3 lines before and after
                            start = max(0, i - 3)
                            end = min(len(lines), i + 4)
                            context = '\n'.join(lines[start:end])
                            relevant_slices.append(f"# Near line {i+1}:\n{context}")
                    
                    if relevant_slices:
                        # Use extracted slices
                        contents[file_path] = '\n\n'.join(relevant_slices[:5])
                        
                        if self.debug:
                            print(f"[AIGuidedReader] Extracted {len(relevant_slices)} slices from {file_path}")
                    else:
                        # Fallback: first 5KB
                        contents[file_path] = full_content[:5000]
                        
                        if self.debug:
                            print(f"[AIGuidedReader] No keyword matches, using first 5KB from {file_path}")
                    
            except Exception as e:
                if self.debug:
                    print(f"[AIGuidedReader] Failed to read {file_path}: {e}")
        
        return contents
    
    async def _ai_answer(self, query: str, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Generate answer using file contents"""
        
        # Format file contents for prompt
        files_text = ""
        for path, content in file_contents.items():
            files_text += f"\n{'='*60}\nFILE: {path}\n{'='*60}\n{content}\n"
        
        answer_prompt = f"""You are analyzing code to answer a developer's question.

USER QUERY: "{query}"

RELEVANT FILES:
{files_text}

INSTRUCTIONS:
1. Answer the question based ONLY on the file contents shown above
2. Be specific - cite file names and line numbers when possible
3. If the answer isn't in these files, say so
4. Keep answer concise (2-3 sentences)

ANSWER:"""
        
        try:
            answer = await self.model.generate(
                prompt=answer_prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            return {
                'answer': answer.strip(),
                'sources': list(file_contents.keys()),
                'confidence': 0.8 if len(file_contents) > 0 else 0.3
            }
        
        except Exception as e:
            if self.debug:
                print(f"[AIGuidedReader] AI answer failed: {e}")
            
            return {
                'answer': f"Error generating answer: {e}",
                'sources': [],
                'confidence': 0.0
            }
    
    def _build_planning_context(self) -> str:
        """Build context string for AI planning"""
        context_parts = []
        
        # Languages
        langs = ', '.join(f"{lang} ({count} files)" for lang, count in list(self.file_index['languages'].items())[:5])
        context_parts.append(f"Languages: {langs}")
        
        # Frameworks
        frameworks = self._format_frameworks()
        if frameworks:
            context_parts.append(f"Frameworks: {frameworks}")
        
        return ' | '.join(context_parts)
    
    def _format_frameworks(self) -> str:
        """Format frameworks for display"""
        parts = []
        for category, frameworks in self.file_index['frameworks'].items():
            if frameworks:
                parts.append(f"{category}: {', '.join(frameworks)}")
        return ' | '.join(parts) if parts else "None detected"
    
    def _format_directory_tree(self) -> str:
        """Format directory tree for display"""
        lines = []
        for dir_name, count in sorted(self.file_index['directory_tree'].items(), key=lambda x: x[1], reverse=True)[:10]:
            lines.append(f"  {dir_name}/: {count} files")
        return '\n'.join(lines) if lines else "  (flat structure)"
    
    def _format_repo_map(self) -> str:
        """Format repository map for AI guidance"""
        repo_map = self.file_index.get('repo_map', {})
        
        if not repo_map:
            return "  (no map available)"
        
        lines = []
        
        # Separate hints from folder mappings
        hints = []
        folders = []
        
        for key, purpose in sorted(repo_map.items()):
            if key.startswith('_hint_'):
                hints.append(f"  💡 {purpose}")
            else:
                folders.append(f"  📁 {key}/ → {purpose}")
        
        # Show framework hints first
        if hints:
            lines.extend(hints)
            lines.append("")
        
        # Then folder purposes
        lines.extend(folders[:15])  # Limit to top 15
        
        return '\n'.join(lines) if lines else "  (analyzing...)"
    
    def _format_file_sample(self) -> str:
        """Format sample of available files"""
        # Show first 20 non-config files
        sample_files = []
        for file_path in self.file_index['files']:
            # Skip config/build files
            if any(skip in file_path.lower() for skip in ['.json', '.lock', '.config', 'package', 'tsconfig']):
                continue
            sample_files.append(f"  - {file_path}")
            if len(sample_files) >= 20:
                break
        
        return '\n'.join(sample_files) if sample_files else "  (no files)"

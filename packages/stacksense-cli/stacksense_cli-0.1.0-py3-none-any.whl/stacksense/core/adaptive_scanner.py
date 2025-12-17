"""
Adaptive Scanner - Two-Phase Intelligent Scanning
==================================================
Phase 1: Shallow scan (20-30s) → Fast overview
Phase 2: Query-driven refinement (3-8s) → Targeted deep dive

This enables the "exam skim then tackle questions" pattern.
"""
from pathlib import Path
from typing import Dict, Any, List, Set
import time
from datetime import datetime


class AdaptiveScanner:
    """
    Two-phase scanner that adapts to user queries dynamically.
    No hardcoding - works for any language/framework.
    """
    
    def __init__(self, repo_path: Path, debug: bool = False):
        self.repo_path = Path(repo_path)
        self.debug = debug
        
        # Cache shallow scan for reuse
        self.shallow_cache = None
        self.last_shallow_scan = None
    
    async def scan_shallow(self) -> Dict[str, Any]:
        """
        Phase 1: Fast shallow scan (20-30s).
        Indexes files without deep extraction.
        """
        if self.debug:
            print("\n" + "=" * 80)
            print("🔍 PHASE 1: Shallow Scan (Fast Overview)")
            print("=" * 80)
        
        start_time = time.time()
        
        result = {
            'scan_type': 'shallow',
            'timestamp': datetime.now().isoformat(),
            'repo_path': str(self.repo_path),
            
            # Quick metadata
            'languages': self._detect_languages(),
            'frameworks': self._detect_frameworks(),
            
            # File index (ALL files with metadata, NO extraction)
            'file_index': self._build_file_index(),
            
            # Structure hints
            'directory_structure': self._analyze_structure(),
            'entry_points': self._find_entry_points(),
            
            # README for context
            'readme_hints': self._extract_readme_hints(),
        }
        
        elapsed = time.time() - start_time
        
        if self.debug:
            print(f"\n✅ Shallow scan complete in {elapsed:.2f}s")
            print(f"   Languages: {result['languages']}")
            print(f"   Frameworks: {len(result['frameworks'])} detected")
            print(f"   Files indexed: {len(result['file_index'])}")
        
        # Cache for reuse
        self.shallow_cache = result
        self.last_shallow_scan = time.time()
        
        return result
    
    async def refine_for_query(self, query: str, shallow_scan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: Query-driven refinement (3-8s).
        Find and extract ONLY relevant files for this query.
        """
        if self.debug:
            print("\n" + "=" * 80)
            print(f"🎯 PHASE 2: Query-Driven Refinement")
            print(f"Query: '{query[:60]}...'")
            print("=" * 80)
        
        start_time = time.time()
        
        # 1. Extract keywords from query
        keywords = await self._extract_keywords(query)
        if self.debug:
            print(f"\n📝 Keywords: {keywords}")
        
        # 2. Find relevant files using TWO-PASS semantic approach
        #    Pass 1: Fast path-based scoring (top 20)
        #    Pass 2: Content-based re-scoring (final top 10)
        relevant_files = self._find_relevant_files(keywords, shallow_scan)
        
        if self.debug:
            print(f"\n📂 Found {len(relevant_files)} relevant files:")
            for file_path, score in relevant_files[:5]:
                print(f"   {score:.2f} - {file_path.relative_to(self.repo_path)}")
        
        # 3. Deep extract ONLY those files (FULLY DYNAMIC!)
        from .code_extractor import CodeExtractor
        
        extractor = CodeExtractor(self.repo_path, debug=self.debug)
        deep_extractions = {}
        
        for file_path, score in relevant_files[:10]:  # Limit to top 10
            try:
                # Universal extraction - works for ANY file type!
                extract = extractor.extract(file_path)
                
                # Add to extractions if we got meaningful content
                if extract and not extract.get('error'):
                    deep_extractions[str(file_path)] = {
                        'extraction': extract,
                        'relevance_score': score
                    }
            except Exception as e:
                if self.debug:
                    print(f"   ⚠️  Failed to extract {file_path.name}: {str(e)[:50]}")
                continue
        
        # 4. Build refined context
        refined = {
            **shallow_scan,
            'query': query,
            'keywords': keywords,
            'query_specific_extractions': deep_extractions,
            'relevant_files': [str(f) for f, _ in relevant_files[:10]]
        }
        
        elapsed = time.time() - start_time
        
        if self.debug:
            print(f"\n✅ Refinement complete in {elapsed:.2f}s")
            print(f"   Deep extractions: {len(deep_extractions)}")
        
        return refined
    
    def _build_file_index(self) -> Dict[str, Dict[str, Any]]:
        """
        Index ALL files with metadata (no extraction).
        Fast metadata-only pass.
        """
        file_index = {}
        
        
        # Search all source files (including docs and configs!)
        patterns = [
            # Code files
            '*.py', '*.js', '*.ts', '*.tsx', '*.jsx', '*.go', '*.java', '*.rb', '*.rs', '*.cpp', '*.c', '*.h',
            # Documentation
            '*.md', '*.markdown', '*.rst', '*.txt',
            # Web files
            '*.html', '*.htm', '*.css',
            # Config files
            '*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.cfg'
        ]
        
        for pattern in patterns:
            for file_path in self.repo_path.rglob(pattern):
                # Skip common ignores
                if any(skip in file_path.parts for skip in ['venv', 'node_modules', '.venv', 'dist', 'build', 'target', '.git', '__pycache__']):
                    continue
                
                # Basic metadata only (fast!)
                file_index[str(file_path)] = {
                    'size': file_path.stat().st_size,
                    'type': file_path.suffix[1:],  # .py → py
                    'name': file_path.name,
                    'parent': str(file_path.parent.relative_to(self.repo_path))
                }
        
        return file_index
    
    async def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords using dynamic domain learning.
        NO HARDCODING - learns from repository patterns!
        """
        # Remove stopwords
        stopwords = {
            'what', 'how', 'where', 'when', 'why', 'who', 
            'the', 'is', 'are', 'was', 'were', 'does', 'do', 'did',
            'in', 'to', 'from', 'with', 'by', 'for', 'at', 'of',
            'a', 'an', 'and', 'or', 'but', 'this', 'that', 'these', 'those',
            'exist', 'have', 'has', 'had', 'can', 'could', 'should', 'would'
        }
        
        words = query.lower().split()
        base_keywords = [w.strip('?.,!') for w in words if w not in stopwords and len(w) > 2]
        
        # Use DomainLearner for dynamic expansion
        from .domain_learner import DomainLearner
        
        learner = DomainLearner(debug=self.debug)
        
        # Learn domains from file index if we have it
        if hasattr(self, 'shallow_cache') and self.shallow_cache:
            file_paths = list(self.shallow_cache.get('file_index', {}).keys())
            learned_domains = await learner.learn_domains_from_files(
                file_paths, 
                self.shallow_cache
            )
            
            # Generate expansions based on learned domains
            expanded = await learner.generate_keyword_expansions(query, learned_domains)
            
            # Combine base keywords with learned expansions
            all_keywords = list(set(base_keywords + expanded))
        else:
            # Fallback to base keywords only
            all_keywords = base_keywords
        
        if self.debug:
            print(f"[AdaptiveScanner] Keywords: {base_keywords}")
            if len(all_keywords) > len(base_keywords):
                print(f"[AdaptiveScanner] Expanded to: {all_keywords[:10]}...")
        
        return all_keywords

    
    
    def _find_relevant_files(self, keywords: List[str], shallow_scan: Dict[str, Any]) -> List[tuple]:
        """
        TWO-PASS SEMANTIC SCORING (no hardcoding):
        Pass 1: Fast path-only scoring → Top 20 candidates
        Pass 2: Read content and re-score → Final top 10
        """
        from .semantic_similarity import SemanticSimilarity
        
        file_index = shallow_scan['file_index']
        semantic = SemanticSimilarity()
        query = ' '.join(keywords)
        
        # ===== PASS 1: Fast Path-Based Scoring =====
        if self.debug:
            print(f"\n[Pass 1] Fast path-based scoring...")
        
        path_scored = []
        for file_path_str, metadata in file_index.items():
            score = semantic.score_file_for_query(
                query=query,
                file_path=file_path_str,
                file_content=None  # Fast: paths only
            )
            if score > 0:
                path_scored.append((Path(file_path_str), score))
        
        # Sort and take top 20
        path_scored.sort(key=lambda x: x[1], reverse=True)
        top_candidates = path_scored[:20]
        
        # CRITICAL: Always include documentation files, even if they didn't score well!
        # This ensures README, CHANGELOG, docs are never missed
        doc_patterns = ['readme', 'changelog', 'docs', 'documentation', 'guide']
        doc_files = []
        for file_path_str, metadata in file_index.items():
            filename_lower = metadata['name'].lower()
            parent_lower = metadata['parent'].lower()
            
            # Check if it's a documentation file
            is_doc = any(pattern in filename_lower or pattern in parent_lower for pattern in doc_patterns)
            
            if is_doc:
                file_path = Path(file_path_str)
                # Only add if not already in top candidates
                if file_path not in [f for f, _ in top_candidates]:
                    doc_files.append((file_path, 0.0))  # Score 0.0, will be re-scored in Pass 2
        
        # Combine: top candidates + documentation files
        top_candidates.extend(doc_files)
        
        if self.debug:
            print(f"   Found {len(path_scored[:20])} path-based + {len(doc_files)} documentation files")
        
        # ===== PASS 2: Content-Based Re-Scoring =====
        if self.debug:
            print(f"\n[Pass 2] Content-based re-scoring...")
        
        content_scored = []
        for file_path, path_score in top_candidates:
            try:
                # LEVEL 1 FIX: Read more content for scoring (10000 chars instead of 2000)
                # This ensures long README files include deep sections in scoring
                # For markdown files, read even more to capture all sections
                char_limit = 20000 if file_path.suffix.lower() in ['.md', '.markdown', '.rst', '.txt'] else 10000
                content = file_path.read_text(encoding='utf-8', errors='ignore')[:char_limit]
                
                # Re-score with content
                content_score = semantic.score_file_for_query(
                    query=query,
                    file_path=str(file_path),
                    file_content=content
                )
                
                content_scored.append((file_path, content_score))
                
                if self.debug and content_score > path_score:
                    print(f"   📈 {file_path.name}: {path_score:.3f} → {content_score:.3f}")
            
            except Exception as e:
                # If can't read, keep path score
                content_scored.append((file_path, path_score))
                if self.debug:
                    print(f"   ⚠️  {file_path.name}: read failed")
        
        # LEVEL 1 FIX: Boost root-level documentation
        # Root README.md should ALWAYS rank higher than subdirectory READMEs
        boosted_scores = []
        for file_path, score in content_scored:
            boost = 0.0
            
            # Check if it's a root-level README
            try:
                rel_path = file_path.relative_to(self.repo_path)
                is_root_readme = (
                    rel_path.name.upper() == 'README.MD' and 
                    len(rel_path.parts) == 1  # No parent directories
                )
                
                if is_root_readme:
                    boost = 1.0  # Massive boost for root README
                    if self.debug:
                        print(f"   🚀 ROOT README BOOST: {file_path.name}: {score:.3f} → {score + boost:.3f}")
                
                # Also boost other root-level docs
                elif len(rel_path.parts) == 1 and any(doc in rel_path.name.upper() for doc in ['CHANGELOG', 'CONTRIBUTING', 'LICENSE']):
                    boost = 0.3
            
            except:
                pass
            
            boosted_scores.append((file_path, score + boost))
        
        # Final sort with boosted scores
        boosted_scores.sort(key=lambda x: x[1], reverse=True)
        
        if self.debug:
            print(f"\n[Final] Top semantic matches (after boosts):")
            for file_path, score in boosted_scores[:5]:
                print(f"   {score:.3f} - {file_path.name}")
        
        return boosted_scores
    
    def _detect_languages(self) -> List[str]:
        """
        Detect languages using universal language detector.
        Supports 100+ languages with NO hardcoding.
        """
        from .language_detector import LanguageDetector
        
        detector = LanguageDetector(debug=self.debug)
        lang_counts = detector.detect_languages(self.repo_path)
        
        # Return languages sorted by file count
        return [lang for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)]

    
    def _detect_frameworks(self) -> List[str]:
        """
        Detect frameworks from:
        1. Manifest files (requirements.txt, package.json, etc.)
        2. Import statements in code (finds optional deps like ChromaDB)
        3. Config files (docker-compose.yml, Dockerfile)
        
        Fully dynamic - works for ANY language.
        """
        frameworks = set()
        
        # 1. Python manifests
        frameworks.update(self._scan_python_manifests())
        
        # 2. JavaScript/TypeScript manifests
        frameworks.update(self._scan_js_manifests())
        
        # 3. Go manifests
        frameworks.update(self._scan_go_manifests())
        
        # 4. Java manifests
        frameworks.update(self._scan_java_manifests())
        
        # 5. Docker/Infrastructure
        frameworks.update(self._scan_infrastructure())
        
        # 6. Import-based detection (finds optional deps!)
        frameworks.update(self._scan_imports())
        
        return sorted(list(frameworks))
    
    def _scan_python_manifests(self) -> Set[str]:
        """Scan Python manifest files"""
        frameworks = set()
        
        # Check requirements.txt
        req_files = list(self.repo_path.rglob('requirements*.txt'))
        for req_file in req_files:
            try:
                content = req_file.read_text().lower()
                
                # Web frameworks
                if 'fastapi' in content:
                    frameworks.add('FastAPI')
                if 'django' in content:
                    frameworks.add('Django')
                if 'flask' in content:
                    frameworks.add('Flask')
                
                # Task queues
                if 'celery' in content:
                    frameworks.add('Celery')
                if 'rq' in content:
                    frameworks.add('RQ')
                
                # Databases
                if 'redis' in content:
                    frameworks.add('Redis')
                if 'postgres' in content or 'psycopg' in content:
                    frameworks.add('PostgreSQL')
                if 'mysql' in content or 'pymysql' in content:
                    frameworks.add('MySQL')
                if 'mongodb' in content or 'pymongo' in content:
                    frameworks.add('MongoDB')
                
                # Vector DBs (often optional deps!)
                if 'chromadb' in content or 'chroma' in content:
                    frameworks.add('ChromaDB')
                if 'pinecone' in content:
                    frameworks.add('Pinecone')
                if 'weaviate' in content:
                    frameworks.add('Weaviate')
                if 'faiss' in content:
                    frameworks.add('FAISS')
                
                # ML/AI
                if 'tensorflow' in content:
                    frameworks.add('TensorFlow')
                if 'pytorch' in content or 'torch' in content:
                    frameworks.add('PyTorch')
                if 'scikit-learn' in content or 'sklearn' in content:
                    frameworks.add('Scikit-Learn')
                
            except:
                pass
        
        # Check pyproject.toml
        pyproject = self.repo_path / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text().lower()
                if 'fastapi' in content:
                    frameworks.add('FastAPI')
                if 'django' in content:
                    frameworks.add('Django')
            except:
                pass
        
        return frameworks
    
    def _scan_js_manifests(self) -> Set[str]:
        """Scan JavaScript/TypeScript manifests"""
        frameworks = set()
        
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                import json
                pkg = json.loads(package_json.read_text())
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                
                # Web frameworks
                if 'next' in deps:
                    frameworks.add('Next.js')
                if 'react' in deps:
                    frameworks.add('React')
                if 'vue' in deps:
                    frameworks.add('Vue')
                if 'express' in deps:
                    frameworks.add('Express')
                if 'fastify' in deps:
                    frameworks.add('Fastify')
                
                # Vector DBs
                if 'chromadb' in deps or '@chromadb/chromadb' in deps:
                    frameworks.add('ChromaDB')
                
            except:
                pass
        
        return frameworks
    
    def _scan_go_manifests(self) -> Set[str]:
        """Scan Go manifests"""
        frameworks = set()
        
        go_mod = self.repo_path / 'go.mod'
        if go_mod.exists():
            try:
                content = go_mod.read_text().lower()
                
                # Web frameworks
                if 'gin-gonic/gin' in content:
                    frameworks.add('Gin')
                if 'echo' in content:
                    frameworks.add('Echo')
                if 'fiber' in content:
                    frameworks.add('Fiber')
                
                # Databases
                if 'gorm' in content:
                    frameworks.add('GORM')
                
            except:
                pass
        
        return frameworks
    
    def _scan_java_manifests(self) -> Set[str]:
        """Scan Java manifests"""
        frameworks = set()
        
        # Maven
        pom_xml = self.repo_path / 'pom.xml'
        if pom_xml.exists():
            try:
                content = pom_xml.read_text().lower()
                
                if 'spring-boot' in content:
                    frameworks.add('Spring Boot')
                if 'hibernate' in content:
                    frameworks.add('Hibernate')
                
            except:
                pass
        
        # Gradle
        build_gradle = self.repo_path / 'build.gradle'
        if build_gradle.exists():
            try:
                content = build_gradle.read_text().lower()
                
                if 'spring-boot' in content:
                    frameworks.add('Spring Boot')
                
            except:
                pass
        
        return frameworks
    
    def _scan_infrastructure(self) -> Set[str]:
        """Scan infrastructure configs"""
        frameworks = set()
        
        # Docker
        if (self.repo_path / 'Dockerfile').exists():
            frameworks.add('Docker')
        
        if (self.repo_path / 'docker-compose.yml').exists() or (self.repo_path / 'docker-compose.yaml').exists():
            frameworks.add('Docker Compose')
            
            # Check what's in docker-compose
            for compose_file in ['docker-compose.yml', 'docker-compose.yaml']:
                compose_path = self.repo_path / compose_file
                if compose_path.exists():
                    try:
                        content = compose_path.read_text().lower()
                        
                        if 'redis' in content:
                            frameworks.add('Redis')
                        if 'postgres' in content:
                            frameworks.add('PostgreSQL')
                        if 'mongo' in content:
                            frameworks.add('MongoDB')
                        
                    except:
                        pass
        
        return frameworks
    
    def _scan_imports(self) -> Set[str]:
        """
        Scan actual code imports to find optional dependencies.
        This finds things like ChromaDB that might not be in requirements.txt!
        
        Dynamic - checks Python, JS, Go, Java imports.
        """
        frameworks = set()
        
        # Limit scan to avoid slowdown (max 50 files)
        files_to_scan = []
        
        # Python files
        for py_file in list(self.repo_path.rglob('*.py'))[:30]:
            if not any(skip in py_file.parts for skip in ['venv', 'node_modules', '.venv', '__pycache__']):
                files_to_scan.append(('python', py_file))
        
        # JS/TS files
        for js_file in list(self.repo_path.rglob('*.js'))[:10]:
            if not any(skip in js_file.parts for skip in ['node_modules', 'dist', 'build']):
                files_to_scan.append(('javascript', js_file))
        
        # Scan files
        for lang, file_path in files_to_scan:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                if lang == 'python':
                    # Python imports
                    lines = content.split('\n')[:50]  # First 50 lines only
                    
                    for line in lines:
                        line_lower = line.lower().strip()
                        
                        if line_lower.startswith('import ') or line_lower.startswith('from '):
                            # Vector DBs
                            if 'chromadb' in line_lower or 'chroma' in line_lower:
                                frameworks.add('ChromaDB')
                            if 'pinecone' in line_lower:
                                frameworks.add('Pinecone')
                            if 'weaviate' in line_lower:
                                frameworks.add('Weaviate')
                            if 'faiss' in line_lower:
                                frameworks.add('FAISS')
                            
                            # AI/ML models
                            if 'ollama' in line_lower:
                                frameworks.add('Ollama')
                            if 'openai' in line_lower:
                                frameworks.add('OpenAI')
                            if 'anthropic' in line_lower:
                                frameworks.add('Anthropic')
                            
                            # ORMs
                            if 'sqlalchemy' in line_lower:
                                frameworks.add('SQLAlchemy')
                
                elif lang == 'javascript':
                    # JS imports
                    lines = content.split('\n')[:50]
                    
                    for line in lines:
                        line_lower = line.lower().strip()
                        
                        if 'require(' in line_lower or 'import ' in line_lower:
                            if 'chromadb' in line_lower:
                                frameworks.add('ChromaDB')
            
            except:
                pass
        
        return frameworks
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze directory structure for patterns"""
        structure = {
            'has_src': (self.repo_path / 'src').exists(),
            'has_app': (self.repo_path / 'app').exists(),
            'has_lib': (self.repo_path / 'lib').exists(),
            'has_tests': (self.repo_path / 'tests').exists() or (self.repo_path / 'test').exists(),
            'has_docs': (self.repo_path / 'docs').exists(),
        }
        
        return structure
    
    def _find_entry_points(self) -> List[str]:
        """Find likely entry points"""
        entry_candidates = ['main.py', 'app.py', 'index.py', 'server.py', '__init__.py', 'index.ts', 'index.js', 'main.go']
        
        entry_points = []
        for candidate in entry_candidates:
            matches = list(self.repo_path.rglob(candidate))
            # Filter ignores
            matches = [m for m in matches if not any(skip in m.parts for skip in ['venv', 'node_modules', 'test'])]
            
            if matches:
                entry_points.extend([str(m.relative_to(self.repo_path)) for m in matches[:2]])  # Max 2 per type
        
        return entry_points[:5]  # Cap at 5 total
    
    def _extract_readme_hints(self) -> str:
        """Extract hints from README"""
        readme_files = ['README.md', 'readme.md', 'README.txt', 'README']
        
        for readme in readme_files:
            readme_path = self.repo_path / readme
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8')
                    # Return first 1000 chars
                    return content[:1000]
                except:
                    pass
        
        return ""

"""
StackSense Semantic Analyzer
Lightweight TF-IDF based semantic code analysis with advanced features
"""
import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeSlice:
    """Import from repo_scanner for type hints"""
    file_path: str
    slice_type: str
    name: str
    start_line: int
    end_line: int
    content: str
    hash: str
    language: str


class SemanticAnalyzer:
    """
    Lightweight semantic analysis using TF-IDF + Cosine Similarity.
    
    Features:
    - Code-aware tokenization (imports, functions, comments)
    - LSA (TruncatedSVD) for semantic depth
    - Hybrid similarity (lexical + structural + import overlap)
    - Topology awareness (respect project structure)
    - Advanced term weighting (support/confidence)
    """
    
    def __init__(
        self,
        use_lsa: bool = True,
        lsa_components: int = 200,
        similarity_weights: Tuple[float, float, float] = (0.6, 0.2, 0.2),
        debug: bool = False
    ):
        """
        Initialize analyzer.
        
        Args:
            use_lsa: Apply LSA (TruncatedSVD) for semantic depth
            lsa_components: Number of LSA components (100-300)
            similarity_weights: (cosine, import_overlap, folder_proximity)
            debug: Enable debug logging
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import normalize
        
        self.use_lsa = use_lsa
        self.lsa_components = lsa_components
        self.weights = similarity_weights
        self.debug = debug
        
        # Store DBSCAN class for later use
        self.DBSCAN = DBSCAN
        
        # TF-IDF vectorizer with optimized parameters
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),          # Unigrams, bigrams, trigrams
            max_features=5000,            # Limit vocabulary
            stop_words='english',         # Remove common words
            min_df=1,                     # Changed from 2 to handle tiny groups
            max_df=0.95,                  # Changed from 0.8 to be more lenient
            token_pattern=r'(?u)\b\w+\b', # Include underscores
            lowercase=True,
            norm='l2'                     # L2 normalization
        )
        
        # LSA (optional dimensionality reduction)
        self.lsa = TruncatedSVD(
            n_components=lsa_components,
            random_state=42
        ) if use_lsa else None
        
        # DBSCAN clustering - eps will be set adaptively
        self.clustering = None  # Initialize in analyze_files based on repo size
        
        # Weights for hybrid similarity
        self.weights = (0.6, 0.2, 0.2)  # (cosine, imports, folder)
    
    def _get_adaptive_eps(self, num_files: int) -> float:
        """
        Get adaptive DBSCAN eps based on repo size.
        
        Now with topology fallback, we can use stricter (more accurate) eps values.
        
        Args:
            num_files: Total number of files in the group
            
        Returns:
            Optimal eps value
        """
        if num_files < 10:
            return 0.40  # Moderate for tiny groups (topology will catch the rest)
        elif num_files < 30:
            return 0.35  # Moderate for small groups
        elif num_files < 100:
            return 0.32  # Slightly lenient for small repos
        elif num_files < 300:
            return 0.30  # Standard for medium repos
        else:
            return 0.28  # Strict for large repos (better precision)
    
    def _detect_topology(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Detect project topology (backend, frontend, services, etc.).
        
        Args:
            file_paths: List of file paths
            
        Returns:
            {topology_name: [file_paths]}
        """
        topology_patterns = {
            # Backend patterns
            'backend_django': ['/models/', '/views/', '/serializers/', '/api/'],
            'backend_flask': ['/routes/', '/blueprints/', '/app/'],
            'backend_fastapi': ['/routers/', '/schemas/', '/crud/'],
            
            # Frontend patterns
            'frontend_react': ['/components/', '/hooks/', '/pages/', '/app/'],
            'frontend_nextjs': ['/app/', '/pages/', '/components/', '/lib/'],
            'frontend_vue': ['/components/', '/views/', '/composables/'],
            
            # Common patterns
            'database': ['/models/', '/migrations/', '/db/', '/schema/'],
            'api': ['/api/', '/endpoints/', '/routes/'],
            'services': ['/services/', '/workers/', '/tasks/'],
            'tests': ['/tests/', '/test_', '/__tests__/'],
            'config': ['/config/', '/settings/', '/env/'],
            'utils': ['/utils/', '/helpers/', '/lib/'],
        }
        
        groups = {}
        ungrouped = []
        
        for file_path in file_paths:
            assigned = False
            path_lower = file_path.lower()
            
            for group_name, patterns in topology_patterns.items():
                if any(pattern in path_lower for pattern in patterns):
                    if group_name not in groups:
                        groups[group_name] = []
                    groups[group_name].append(file_path)
                    assigned = True
                    break
            
            if not assigned:
                ungrouped.append(file_path)
        
        # Add ungrouped as "core"
        if ungrouped:
            groups['core'] = ungrouped
        
        if self.debug:
            print(f"[Analyzer] Detected {len(groups)} topology groups:")
            for name, files in groups.items():
                print(f"   • {name}: {len(files)} files")
        
        return groups
    
    def _extract_code_features(self, slice_obj: CodeSlice) -> str:
        """
        Extract meaningful features from code.
        
        Extracts:
        - Import statements (high weight)
        - Class/function names
        - Comments and docstrings
        - Variable names
        
        Returns:
            Feature string for TF-IDF
        """
        features = []
        
        # Extract imports (weight: 3x)
        imports = self._extract_imports(slice_obj.content, slice_obj.language)
        features.extend(imports * 3)
        
        # Extract definitions (weight: 2x)
        definitions = self._extract_definitions(slice_obj.content, slice_obj.language)
        features.extend(definitions * 2)
        
        # Extract comments (weight: 1x)
        comments = self._extract_comments(slice_obj.content, slice_obj.language)
        features.extend(comments)
        
        # File name tokens (weight: 2x)
        file_name = Path(slice_obj.file_path).stem
        file_tokens = file_name.replace('.', '_').replace('-', '_').split('_')
        features.extend(file_tokens * 2)
        
        # Folder path tokens (weight: 1x)
        folder_parts = Path(slice_obj.file_path).parts[:-1]
        features.extend(folder_parts)
        
        return ' '.join(features)
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        if language == 'python':
            # import X, from Y import Z
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith(('import ', 'from ')):
                    # Extract module names
                    parts = line.replace('import', '').replace('from', '')
                    parts = parts.split('as')[0].strip()  # Remove aliases
                    tokens = re.findall(r'\w+', parts)
                    imports.extend(tokens)
        
        elif language in ['javascript', 'typescript', 'react', 'react-typescript']:
            # import X from 'Y', require('X')
            import_pattern = r"(?:import|require)\s*\(?['\"]([^'\"]+)['\"]"
            matches = re.findall(import_pattern, content)
            for match in matches:
                # Extract module name
                tokens = match.split('/')[-1].replace('.js', '').replace('.ts', '')
                imports.append(tokens)
        
        return [imp.replace('.', '_').replace('-', '_') for imp in imports if imp]
    
    def _extract_definitions(self, content: str, language: str) -> List[str]:
        """Extract function/class names"""
        definitions = []
        
        if language == 'python':
            # class X, def Y
            class_pattern = r'class\s+(\w+)'
            func_pattern = r'def\s+(\w+)'
            definitions.extend(re.findall(class_pattern, content))
            definitions.extend(re.findall(func_pattern, content))
        
        elif language in ['javascript', 'typescript', 'react', 'react-typescript']:
            # class X, function Y, const Z =
            class_pattern = r'class\s+(\w+)'
            func_pattern = r'function\s+(\w+)'
            const_pattern = r'(?:const|let|var)\s+(\w+)'
            arrow_pattern = r'(\w+)\s*=\s*\([^)]*\)\s*=>'
            
            definitions.extend(re.findall(class_pattern, content))
            definitions.extend(re.findall(func_pattern, content))
            definitions.extend(re.findall(const_pattern, content))
            definitions.extend(re.findall(arrow_pattern, content))
        
        return definitions
    
    def _extract_comments(self, content: str, language: str) -> List[str]:
        """Extract comments and docstrings"""
        comments = []
        
        if language == 'python':
            # """docstring""" and # comment
            docstring_pattern = r'"""(.*?)"""'
            comment_pattern = r'#\s*(.*?)$'
            comments.extend(re.findall(docstring_pattern, content, re.DOTALL))
            comments.extend(re.findall(comment_pattern, content, re.MULTILINE))
        
        elif language in ['javascript', 'typescript', 'react', 'react-typescript']:
            # /* comment */ and // comment
            block_pattern = r'/\*(.*?)\*/'
            line_pattern = r'//\s*(.*?)$'
            comments.extend(re.findall(block_pattern, content, re.DOTALL))
            comments.extend(re.findall(line_pattern, content, re.MULTILINE))
        
        # Clean and tokenize comments
        cleaned = []
        for comment in comments:
            tokens = re.findall(r'\w+', comment.lower())
            cleaned.extend([t for t in tokens if len(t) > 2])
        
        return cleaned
    
    def _compute_import_overlap(self, slices: List[CodeSlice]) -> np.ndarray:
        """
        Compute import overlap matrix using Jaccard similarity.
        
        Returns:
            NxN matrix of import overlap scores
        """
        n = len(slices)
        overlap_matrix = np.zeros((n, n))
        
        # Extract imports for all files
        imports_by_file = []
        for slice_obj in slices:
            imports = set(self._extract_imports(slice_obj.content, slice_obj.language))
            imports_by_file.append(imports)
        
        # Compute Jaccard similarity
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    overlap_matrix[i, j] = 1.0
                else:
                    imports_i = imports_by_file[i]
                    imports_j = imports_by_file[j]
                    
                    if not imports_i or not imports_j:
                        similarity = 0.0
                    else:
                        intersection = len(imports_i & imports_j)
                        union = len(imports_i | imports_j)
                        similarity = intersection / union if union > 0 else 0.0
                    
                    overlap_matrix[i, j] = similarity
                    overlap_matrix[j, i] = similarity
        
        return overlap_matrix
    
    def _compute_folder_proximity(self, file_paths: List[str]) -> np.ndarray:
        """
        Compute folder proximity matrix.
        
        Files in same folder get higher scores.
        
        Returns:
            NxN matrix of folder proximity scores
        """
        n = len(file_paths)
        proximity_matrix = np.zeros((n, n))
        
        for i in range(n):
            path_i = Path(file_paths[i])
            for j in range(i, n):
                path_j = Path(file_paths[j])
                
                if i == j:
                    proximity_matrix[i, j] = 1.0
                else:
                    # Compute common path depth
                    parts_i = path_i.parts[:-1]  # Exclude filename
                    parts_j = path_j.parts[:-1]
                    
                    # Find common prefix
                    common = 0
                    for pi, pj in zip(parts_i, parts_j):
                        if pi == pj:
                            common += 1
                        else:
                            break
                    
                    # Normalize by max depth
                    max_depth = max(len(parts_i), len(parts_j))
                    similarity = common / max_depth if max_depth > 0 else 0.0
                    
                    proximity_matrix[i, j] = similarity
                    proximity_matrix[j, i] = similarity
        
        return proximity_matrix
    
    async def analyze_files(
        self,
        slices: List[CodeSlice],
        use_topology: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze files and generate clusters.
        
        OPTIMIZATION: Works at FILE level, not slice level.
        
        Args:
            slices: List of code slices to analyze
            use_topology: Use topology-aware grouping
            
        Returns:
            {
                'clusters': {'module_name': [files], ...},
                'similarity_matrix': np.ndarray,
                'dependencies': {file: [deps], ...},
                'topology_groups': {...},
                'confidence_scores': {...}
            }
        """
        if not slices:
            return {
                'clusters': {},
                'similarity_matrix': None,
                'dependencies': {},
                'topology_groups': {},
                'confidence_scores': {}
            }
        
        # ⚡ OPTIMIZATION 1: Aggregate slices by file
        # Instead of analyzing 5485 slices, analyze 329 files
        file_to_slices = {}
        for s in slices:
            if s.file_path not in file_to_slices:
                file_to_slices[s.file_path] = []
            file_to_slices[s.file_path].append(s)
        
        # Create one "mega slice" per file by combining all slices
        file_slices = []
        for file_path, slices_list in file_to_slices.items():
            # Combine content from all slices in this file
            combined_slice = CodeSlice(
                file_path=file_path,
                slice_type='file',
                name=file_path.split('/')[-1],
                start_line=min(s.start_line for s in slices_list),
                end_line=max(s.end_line for s in slices_list),
                content=' '.join([s.content for s in slices_list[:10]]),  # First 10 slices only
                hash=slices_list[0].hash,
                language=slices_list[0].language
            )
            file_slices.append(combined_slice)
        
        if self.debug:
            print(f"[Analyzer] Aggregated {len(slices)} slices → {len(file_slices)} files")
        
        file_paths = [s.file_path for s in file_slices]
        
        # Stage 1.5: Topology Detection
        topology_groups = {}
        if use_topology:
            topology_groups = self._detect_topology(file_paths)
        else:
            topology_groups = {'all': file_paths}
        
        # Analyze each topology group separately
        all_clusters = {}
        all_deps = {}
        global_similarity = None
        
        for group_name, group_files in topology_groups.items():
            group_slices = [s for s in file_slices if s.file_path in group_files]
            
            # ⚡ OPTIMIZATION 2: Skip tiny groups
            if len(group_slices) < 2:
                all_clusters[f"{group_name}_single"] = group_files
                continue
            
            # ⚡ OPTIMIZATION 3: Sample huge groups
            max_files = 200  # Don't analyze more than 200 files per group
            if len(group_slices) > max_files:
                if self.debug:
                    print(f"\n[Analyzer] {group_name} too large ({len(group_slices)} files), sampling {max_files}...")
                # Sample prioritizing recently modified (heuristic: later in list)
                step = len(group_slices) // max_files
                group_slices = group_slices[::step][:max_files]
                group_files = [s.file_path for s in group_slices]
            
            if self.debug:
                print(f"\n[Analyzer] Analyzing {group_name} ({len(group_slices)} files)...")
            
            # Extract features
            features = [self._extract_code_features(s) for s in group_slices]
            
            # ⚡ OPTIMIZATION 4: Skip empty features
            non_empty = [(f, s, p) for f, s, p in zip(features, group_slices, group_files) if f.strip()]
            if len(non_empty) < 2:
                continue
            
            features, group_slices, group_files = zip(*non_empty)
            features = list(features)
            group_slices = list(group_slices)
            group_files = list(group_files)
            
            # TF-IDF vectorization
            try:
                tfidf_matrix = self.vectorizer.fit_transform(features)
            except Exception as e:
                if self.debug:
                    print(f"   TF-IDF failed: {e}")
                continue
            
            # ⚡ OPTIMIZATION 5: Skip LSA for small groups or when vocab is too small
            if self.use_lsa and tfidf_matrix.shape[0] > 30 and tfidf_matrix.shape[1] > self.lsa_components:
                if self.debug:
                    print(f"   Applying LSA ({self.lsa_components} components)...")
                try:
                    reduced_matrix = self.lsa.fit_transform(tfidf_matrix)
                    variance_explained = self.lsa.explained_variance_ratio_.sum()
                    if self.debug:
                        print(f"   Variance explained: {variance_explained:.2%}")
                except Exception as e:
                    if self.debug:
                        print(f"   LSA failed, using raw TF-IDF: {e}")
                    reduced_matrix = tfidf_matrix.toarray()
            else:
                reduced_matrix = tfidf_matrix.toarray()
            
            # Compute similarity matrices
            from sklearn.metrics.pairwise import cosine_similarity
            
            cosine_sim = cosine_similarity(reduced_matrix)
            
            # ⚡ OPTIMIZATION 6: Skip expensive computations for large groups
            if len(group_slices) > 100:
                # For very large groups, use cosine only
                hybrid_similarity = cosine_sim
            else:
                import_overlap = self._compute_import_overlap(group_slices)
                folder_proximity = self._compute_folder_proximity(group_files)
                
                # Hybrid similarity
                w_cos, w_import, w_folder = self.weights
                hybrid_similarity = (
                    w_cos * cosine_sim +
                    w_import * import_overlap +
                    w_folder * folder_proximity
                )
            
            # Clip to [0, 1] to prevent negative distances
            hybrid_similarity = np.clip(hybrid_similarity, 0.0, 1.0)
            
            if self.debug:
                print(f"   Similarity computed, range: [{hybrid_similarity.min():.3f}, {hybrid_similarity.max():.3f}]")
            
            # Clustering with DBSCAN
            distance_matrix = 1 - hybrid_similarity
            
            # Ensure non-negative (double-check)
            # ⚡ OPTIMIZATION 7: Adaptive DBSCAN eps based on group size
            adaptive_eps = self._get_adaptive_eps(len(group_files))
            
            if self.debug:
                print(f"   Using adaptive eps={adaptive_eps:.2f} for {len(group_files)} files")
            
            # Create DBSCAN with adaptive eps
            clustering = self.DBSCAN(
                eps=adaptive_eps,
                min_samples=2,
                metric='precomputed'
            )
            
            # Cluster based on distance matrix
            labels = clustering.fit_predict(distance_matrix)
            
            # ⚡ OPTIMIZATION 8: Multi-layered fallback if no clusters found
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            
            if n_clusters == 0 and len(group_files) >= 3:
                # DBSCAN found no clusters, use intelligent fallback
                if self.debug:
                    print(f"   No clusters found, using multi-layered fallback...")
                
                # Layer 1: Group by language (Python, JS, Go, etc.)
                language_groups = {}
                for idx, file_path in enumerate(group_files):
                    # Detect language from extension
                    ext = Path(file_path).suffix.lower()
                    lang_map = {
                        '.py': 'python',
                        '.js': 'javascript',
                        '.ts': 'typescript',
                        '.jsx': 'react',
                        '.tsx': 'react-ts',
                        '.go': 'go',
                        '.java': 'java',
                        '.rb': 'ruby',
                        '.php': 'php',
                        '.cs': 'csharp',
                        '.rs': 'rust',
                        '.kt': 'kotlin',
                    }
                    lang = lang_map.get(ext, 'other')
                    
                    if lang not in language_groups:
                        language_groups[lang] = []
                    language_groups[lang].append((idx, file_path))
                
                # Layer 2: Within each language, group by framework patterns
                cluster_id = 0
                labels = np.array([-1] * len(group_files))
                
                for lang, files in language_groups.items():
                    if len(files) < 2:
                        continue
                    
                    # Framework-specific patterns
                    framework_patterns = {
                        # Python/Django patterns
                        'models': ['models/', 'model.py', '/models.py'],
                        'views': ['views/', 'view.py', '/views.py'],
                        'serializers': ['serializers/', 'serializer.py'],
                        'tasks': ['tasks/', 'task.py', 'celery'],
                        'api': ['api/', 'endpoints/', 'routes/'],
                        'migrations': ['migrations/'],
                        'security': ['security/', 'auth/', 'permissions/'],
                        'utils': ['utils/', 'helpers/', 'lib/'],
                        
                        # JavaScript/React patterns
                        'components': ['components/', 'Component.', '/components/'],
                        'hooks': ['hooks/', 'use', '/hooks/'],
                        'pages': ['pages/', 'Page.', '/pages/'],
                        'services': ['services/', 'Service.', 'api/'],
                        'store': ['store/', 'redux/', 'state/'],
                        'styles': ['styles/', 'css/', 'scss/'],
                        
                        # Java/Spring patterns
                        'controllers': ['controller/', 'Controller.'],
                        'repositories': ['repository/', 'Repository.', 'dao/'],
                        'entities': ['entity/', 'Entity.', 'domain/'],
                        'config': ['config/', 'configuration/'],
                        
                        # Go patterns
                        'handlers': ['handlers/', 'handler.go'],
                        'middleware': ['middleware/'],
                        'pkg': ['pkg/'],
                    }
                    
                    # Group files by pattern
                    pattern_groups = {}
                    for idx, file_path in files:
                        file_lower = file_path.lower()
                        assigned = False
                        
                        for pattern_name, patterns in framework_patterns.items():
                            if any(p in file_lower for p in patterns):
                                if pattern_name not in pattern_groups:
                                    pattern_groups[pattern_name] = []
                                pattern_groups[pattern_name].append(idx)
                                assigned = True
                                break
                        
                        # Layer 3: If no pattern match, group by subdirectory
                        if not assigned:
                            path = Path(file_path)
                            if len(path.parts) > 1:
                                subdir = path.parts[-2]
                            else:
                                subdir = "root"
                            
                            if subdir not in pattern_groups:
                                pattern_groups[subdir] = []
                            pattern_groups[subdir].append(idx)
                    
                    # Create clusters from groups with ≥2 files
                    for group_name, indices in pattern_groups.items():
                        if len(indices) >= 2:
                            for idx in indices:
                                labels[idx] = cluster_id
                            cluster_id += 1
                            if self.debug:
                                print(f"      [{lang}] {group_name}: {len(indices)} files")
            
            # Group files by cluster
            for idx, label in enumerate(labels):
                if label == -1:  # Noise
                    continue
                
                cluster_name = f"{group_name}_module_{label}"
                if cluster_name not in all_clusters:
                    all_clusters[cluster_name] = []
                
                all_clusters[cluster_name].append(group_files[idx])
            
            if self.debug:
                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                n_noise = list(labels).count(-1)
                print(f"   Found {n_clusters} clusters, {n_noise} noise points")
        
        # Build dependency graph (using original slices, not aggregated)
        dependencies = self._build_dependency_graph(slices)
        
        # Compute confidence scores
        confidence_scores = self._compute_confidence_scores(all_clusters, dependencies)
        
        return {
            'clusters': all_clusters,
            'similarity_matrix': global_similarity,
            'dependencies': dependencies,
            'topology_groups': topology_groups,
            'confidence_scores': confidence_scores
        }
    
    def _build_dependency_graph(self, slices: List[CodeSlice]) -> Dict[str, List[str]]:
        """Build import dependency graph"""
        graph = {}
        
        # Map module names to file paths
        module_to_file = {}
        for s in slices:
            # Extract module name from path
            path_obj = Path(s.file_path)
            module = str(path_obj.with_suffix('')).replace('/', '.').replace('\\', '.')
            module_to_file[module] = s.file_path
            
            # Also add just the filename without extension
            stem = path_obj.stem
            module_to_file[stem] = s.file_path
        
        # Extract imports and map to files
        for s in slices:
            imports = self._extract_imports(s.content, s.language)
            deps = set()
            
            for imp in imports:
                # Try to find matching file
                for module, path in module_to_file.items():
                    if path == s.file_path:
                        continue
                    
                    # Check if import matches module
                    if (imp in module or 
                        module.endswith(f".{imp}") or
                        module == imp):
                        deps.add(path)
            
            if deps:
                graph[s.file_path] = list(deps)
        
        return graph
    
    def _compute_confidence_scores(
        self,
        clusters: Dict[str, List[str]],
        dependencies: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Compute confidence score for each cluster.
        
        Based on:
        - Cluster size (larger = more confident)
        - Internal dependencies (more = more confident)
        - File name consistency (similar names = more confident)
        
        Returns:
            {cluster_name: confidence_score (0-1)}
        """
        scores = {}
        
        for cluster_name, files in clusters.items():
            score = 0.5  # Base score
            
            # Size factor (2-10 files is optimal)
            if 2 <= len(files) <= 10:
                score += 0.2
            elif len(files) > 10:
                score += 0.1
            
            # Dependency factor
            internal_deps = 0
            for file in files:
                if file in dependencies:
                    for dep in dependencies[file]:
                        if dep in files:
                            internal_deps += 1
            
            if internal_deps > 0:
                score += min(0.2, internal_deps * 0.05)
            
            # Name consistency factor
            stems = [Path(f).stem for f in files]
            common_tokens = set(stems[0].lower().split('_'))
            for stem in stems[1:]:
                common_tokens &= set(stem.lower().split('_'))
            
            if common_tokens:
                score += 0.1
            
            scores[cluster_name] = min(1.0, score)
        
        return scores

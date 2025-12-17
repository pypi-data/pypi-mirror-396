"""
StackSense Diagram Builder
Universal code dependency diagram generator using Tree-sitter + regex fallbacks  
"""
import os
import re
import json
import hashlib
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import networkx as nx

# Use tree-sitter 0.21.3 (compatible with tree-sitter-languages)
# Suppress deprecation warning from tree_sitter internals
try:
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
        from tree_sitter_languages import get_language, get_parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    # Show info once - diagrams still work via regex
    import sys
    if not getattr(sys, '_stacksense_diagram_ts_warning', False):
        import logging
        logging.getLogger(__name__).info(
            "⚠️  Diagram system: tree-sitter unavailable. Using regex fallback. "
            "For enhanced accuracy: pip install 'stacksense[full]' (Python <3.13)"
        )
        sys._stacksense_diagram_ts_warning = True


@dataclass
class ParsedFile:
    """Parsed file information"""
    path: str
    language: str
    imports: List[str]
    functions: List[str]
    classes: List[str]
    exports: List[str]
    # NEW: Symbol usage tracking
    function_calls: List[str] = None  # Functions called in this file
    class_instantiations: List[str] = None  # Classes instantiated
    namespace_map: Dict[str, str] = None  # Import aliases (name -> real_module)
    
    def __post_init__(self):
        if self.function_calls is None:
            self.function_calls = []
        if self.class_instantiations is None:
            self.class_instantiations = []
        if self.namespace_map is None:
            self.namespace_map = {}
    
    
@dataclass
class Cluster:
    """Code cluster (subsystem)"""
    id: str
    name: str
    files: List[str]
    purpose: str
    entry_points: List[str]


@dataclass
class Diagram:
    """Complete dependency diagram"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    clusters: List[Cluster]
    metadata: Dict[str, Any]
    

class DiagramBuilder:
    """
    Universal diagram builder supporting all languages.
    
    Strategy:
    1. Detect language for each file
    2. Parse with Tree-sitter (if available) or regex fallback
    3. Build dependency graph
    4. Detect clusters
    5. Generate multiple output formats
    """
    
    # Language extension mapping
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
        '.kt': 'kotlin',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'c_sharp',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.m': 'objective_c',
        '.mm': 'objective_c',
        '.scala': 'scala',
        '.r': 'r',
        '.lua': 'lua',
        '.pl': 'perl',
        '.sh': 'bash',
        '.dart': 'dart',
    }
    
    # Tree-sitter query templates for imports
    IMPORT_QUERIES = {
        'python': """
            (import_statement) @import
            (import_from_statement) @import_from
        """,
        'javascript': """
            (import_statement) @import
            (call_expression
              function: (identifier) @func_name (#eq? @func_name "require")
              arguments: (arguments (string) @require_path)) @require
        """,
        'typescript': """
            (import_statement) @import
        """,
        'go': """
            (import_declaration) @import
        """,
        'rust': """
            (use_declaration) @use
            (extern_crate_declaration) @extern
        """,
        'java': """
            (import_declaration) @import
        """,
    }
    
    # Regex fallback patterns for imports
    IMPORT_PATTERNS = {
        'python': [
            r'^import\s+([\w\.]+)',
            r'^from\s+([\w\.]+)\s+import',
        ],
        'javascript': [
            r'import\s+.*\s+from\s+[\'"](.+)[\'"]',
            r'require\([\'"](.+)[\'"]\)',
        ],
        'typescript': [
            r'import\s+.*\s+from\s+[\'"](.+)[\'"]',
        ],
        'go': [
            r'import\s+"(.+)"',
            r'import\s+\(\s*"(.+)"',
        ],
        'rust': [
            r'use\s+([\w:]+)',
            r'extern\s+crate\s+(\w+)',
        ],
        'java': [
            r'import\s+([\w\.]+)',
        ],
        'kotlin': [
            r'import\s+([\w\.]+)',
        ],
        'ruby': [
            r'require\s+[\'"](.+)[\'"]',
        ],
        'php': [
            r'use\s+([\w\\]+)',
            r'require_once\s+[\'"](.+)[\'"]',
        ],
    }
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.use_tree_sitter = TREE_SITTER_AVAILABLE
        
        # Dynamically detect standard library modules
        self.stdlib_modules = self._detect_stdlib_modules()
        
        if not self.use_tree_sitter and self.debug:
            print("[DiagramBuilder] Tree-sitter not available, using regex fallback")
    
    def _detect_stdlib_modules(self) -> Set[str]:
        """Dynamically detect Python standard library modules"""
        stdlib_modules = set()
        
        # Get stdlib module names from sys
        try:
            import distutils.sysconfig as sysconfig
            std_lib = sysconfig.get_python_lib(standard_lib=True)
            
            # Add common stdlib modules
            stdlib_modules.update([
                # Core
                'os', 'sys', 'io', 're', 'json', 'csv', 'xml', 'html',
                # Data structures
                'collections', 'heapq', 'bisect', 'array', 'queue',
                # Functional
                'functools', 'itertools', 'operator',
                # Files
                'pathlib', 'shutil', 'tempfile', 'glob', 'fnmatch',
                # Typing
                'typing', 'types', 'abc', 'dataclasses',
                # Datetime
                'datetime', 'time', 'calendar',
                # Math
                'math', 'random', 'statistics', 'decimal', 'fractions',
                # Networking
                'socket', 'ssl', 'http', 'urllib', 'email',
                # Threading
                'threading', 'multiprocessing', 'concurrent', 'asyncio',
                # misc
                'logging', 'argparse', 'unittest', 'warnings', 'subprocess',
                'hashlib', 'secrets', 'uuid', 'base64', 'struct',
                # Build/install
                'setuptools', 'distutils', 'pkg_resources', 'importlib',
            ])
        except:
            # Fallback to common modules
            stdlib_modules.update([
                'os', 'sys', 'json', 'pathlib', 'typing', 'datetime',
                'collections', 'functools', 'itertools', 'subprocess',
                'logging', 'argparse', 'unittest', 'threading', 'asyncio'
            ])
        
        return stdlib_modules
    
    def build_diagram(self, repo_path: Path, file_index: Dict[str, Any]) -> Diagram:
        """
        Build dependency diagram for a repository.
        
        Args:
            repo_path: Repository root path
            file_index: File index from scanner {file_path: {language, ...}}
            
        Returns:
            Complete Diagram object
        """
        if self.debug:
            print(f"[DiagramBuilder] Building diagram for: {repo_path}")
        
        # Parse all files
        parsed_files = []
        for file_path, file_info in file_index.items():
            language = file_info.get('language', 'unknown')
            
            if language == 'unknown':
                continue
            
            full_path = repo_path / file_path
            
            if not full_path.exists():
                continue
            
            # Pass repo_path for consistent relative path calculation
            parsed = self._parse_file(full_path, language, repo_path)
            if parsed:
                parsed_files.append(parsed)
        
        if self.debug:
            print(f"[DiagramBuilder] Parsed {len(parsed_files)} files")
        
        # Build dependency graph
        graph = self._build_dependency_graph(parsed_files, repo_path)
        
        # Detect clusters
        clusters = self._detect_clusters(graph, parsed_files)
        
        # Extract metadata
        metadata = self._extract_metadata(parsed_files, graph)
        
        # Convert to diagram format
        nodes = []
        for file in parsed_files:
            nodes.append({
                'id': file.path,
                'language': file.language,
                'type': self._classify_node_type(file),
                'functions': file.functions,
                'classes': file.classes,
                'imports': file.imports,
            })
        
        edges = []
        for u, v, data in graph.edges(data=True):
            edges.append({
                'from': u,
                'to': v,
                'type': data.get('type', 'imports')
            })
        
        diagram = Diagram(
            nodes=nodes,
            edges=edges,
            clusters=clusters,
            metadata=metadata
        )
        
        if self.debug:
            print(f"[DiagramBuilder] Created diagram: {len(nodes)} nodes, {len(edges)} edges, {len(clusters)} clusters")
        
        return diagram
    
    def _parse_file(self, file_path: Path, language: str, repo_path: Path = None) -> Optional[ParsedFile]:
        """Parse a single file using Tree-sitter or regex"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            if self.debug:
                print(f"[DiagramBuilder] Error reading {file_path}: {e}")
            return None
        
        # Use CONSISTENT path format: relative to repo root
        if repo_path:
            try:
                rel_path = str(file_path.relative_to(repo_path))
            except ValueError:
                rel_path = str(file_path)
        else:
            rel_path = str(file_path)
        
        # Try Tree-sitter first
        if self.use_tree_sitter and language in self.IMPORT_QUERIES:
            result = self._parse_with_treesitter(content, language, rel_path)
            if result:
                return result
        
        # Fallback to regex
        return self._parse_with_regex(content, language, rel_path)
    
    def _parse_with_treesitter(self, content: str, language: str, file_path: str) -> Optional[ParsedFile]:
        """Parse using Tree-sitter 0.25.2 API via wrapper functions"""
        try:
            # CORRECT 0.25.2 SYNTAX - Use tree_sitter_languages wrapper
            from tree_sitter_languages import get_language, get_parser
            
            # This is the RIGHT way for 0.25.2
            ts_language = get_language(language)
            parser = get_parser(language)
            
            # Parse
            tree = parser.parse(bytes(content, 'utf8'))
            root = tree.root_node
            
            imports = []
            functions = []
            classes = []
            exports = []
            function_calls = []
            class_instantiations = []
            namespace_map = {}
            
            # Parse imports with query API
            if language in self.IMPORT_QUERIES:
                query = ts_language.query(self.IMPORT_QUERIES[language])
                
                for node, _ in query.captures(root):
                    import_text = node.text.decode('utf8')
                    
                    # Extract module name
                    module = self._extract_module_name(import_text, language)
                    if module:
                        imports.append(module)
                    
                    # Track import aliases for namespace mapping
                    if language == 'python':
                        # Handle: from X import Y as Z
                        if ' as ' in import_text:
                            parts = import_text.split(' as ')
                            if len(parts) == 2:
                                real_name = parts[0].strip().split()[-1]
                                alias = parts[1].strip()
                                namespace_map[alias] = real_name
                        # Handle: import X as Y
                        elif import_text.startswith('import') and ' as ' in import_text:
                            parts = import_text.replace('import', '').split(' as ')
                            if len(parts) == 2:
                                namespace_map[parts[1].strip()] = parts[0].strip()
            
            # Parse functions and classes
            self._extract_definitions_treesitter(root, functions, classes, exports)
            
            # Extract function calls and class instantiations
            self._extract_symbol_usage(root, function_calls, class_instantiations, language)
            
            return ParsedFile(
                path=file_path,
                language=language,
                imports=list(set(imports)),
                functions=functions,
                classes=classes,
                exports=exports,
                function_calls=list(set(function_calls)),
                class_instantiations=list(set(class_instantiations)),
                namespace_map=namespace_map
            )
            
        except Exception as e:
            if self.debug:
                print(f"[DiagramBuilder] Tree-sitter parse error for {file_path}: {e}")
            return None
    
    def _extract_definitions_treesitter(self, node, functions: List, classes: List, exports: List):
        """Extract function and class definitions from Tree-sitter AST"""
        if node.type == 'function_definition':
            for child in node.children:
                if child.type == 'identifier':
                    functions.append(child.text.decode('utf8'))
                    break
        elif node.type == 'class_definition':
            for child in node.children:
                if child.type == 'identifier':
                    classes.append(child.text.decode('utf8'))
                    break
        elif node.type in ['export_statement', 'export_declaration']:
            exports.append(node.text.decode('utf8')[:50])  # Truncate for brevity
        
        # Recurse
        for child in node.children:
            self._extract_definitions_treesitter(child, functions, classes, exports)
    
    def _extract_symbol_usage(self, node, function_calls: List, class_instantiations: List, language: str):
        """NEW: Extract function calls and class instantiations from Tree-sitter AST"""
        if language == 'python':
            # Function call: some_func(...)
            if node.type == 'call':
                for child in node.children:
                    if child.type in ['identifier', 'attribute']:
                        func_name = child.text.decode('utf8')
                        if func_name and not func_name.startswith('_'):
                            function_calls.append(func_name)
                        break
            
            # Class instantiation:  SomeClass(...)
            elif node.type == 'call' and node.children:
                first_child = node.children[0]
                if first_child.type == 'identifier':
                    name = first_child.text.decode('utf8')
                    # Heuristic: starts with capital = likely a class
                    if name and name[0].isupper():
                        class_instantiations.append(name)
        
        elif language in ['javascript', 'typescript']:
            # new SomeClass(...)
            if node.type == 'new_expression':
                for child in node.children:
                    if child.type == 'identifier':
                        class_instantiations.append(child.text.decode('utf8'))
                        break
            
            # function calls
            elif node.type == 'call_expression':
                for child in node.children:
                    if child.type in ['identifier', 'member_expression']:
                        function_calls.append(child.text.decode('utf8'))
                        break
        
        # Recurse
        for child in node.children:
            self._extract_symbol_usage(child, function_calls, class_instantiations, language)
    
    def _parse_with_regex(self, content: str, language: str, file_path: str) -> ParsedFile:
        """Parse using regex patterns"""
        imports = []
        functions = []
        classes = []
        
        # Extract imports
        if language in self.IMPORT_PATTERNS:
            for pattern in self.IMPORT_PATTERNS[language]:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.extend(matches)
        
        # Extract functions (generic patterns)
        func_patterns = {
            'python': r'^def\s+(\w+)\s*\(',
            'javascript': r'function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\(.*\)\s*=>',
            'go': r'func\s+(\w+)\s*\(',
            'rust': r'fn\s+(\w+)\s*[\(<]',
            'java': r'(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(',
        }
        
        if language in func_patterns:
            func_matches = re.findall(func_patterns[language], content, re.MULTILINE)
            # Flatten tuples from alternation patterns
            for match in func_matches:
                if isinstance(match, tuple):
                    functions.extend([m for m in match if m])
                else:
                    functions.append(match)
        
        # Extract classes (generic patterns)
        class_patterns = {
            'python': r'^class\s+(\w+)',
            'javascript': r'class\s+(\w+)',
            'java': r'class\s+(\w+)',
            'go': r'type\s+(\w+)\s+struct',
            'rust': r'struct\s+(\w+)',
        }
        
        if language in class_patterns:
            class_matches = re.findall(class_patterns[language], content, re.MULTILINE)
            classes.extend(class_matches)
        
        return ParsedFile(
            path=file_path,
            language=language,
            imports=list(set(imports)),
            functions=functions[:20],  # Limit for performance
            classes=classes[:20],
            exports=[]
        )
    
    def _extract_module_name(self, import_text: str, language: str) -> Optional[str]:
        """Extract module name from import statement"""
        if language == 'python':
            match = re.search(r'import\s+([\w\.]+)|from\s+([\w\.]+)', import_text)
            if match:
                return match.group(1) or match.group(2)
        
        elif language in ['javascript', 'typescript']:
            match = re.search(r'from\s+[\'"](.+)[\'"]|require\([\'"](.+)[\'"]\)', import_text)
            if match:
                return match.group(1) or match.group(2)
        
        elif language == 'go':
            match = re.search(r'"(.+)"', import_text)
            if match:
                return match.group(1)
        
        elif language == 'rust':
            match = re.search(r'use\s+([\w:]+)', import_text)
            if match:
                return match.group(1)
        
        return None
    
    def _build_dependency_graph(self, parsed_files: List[ParsedFile], repo_path: Path) -> nx.DiGraph:
        """Build NetworkX directed graph from parsed files"""
        graph = nx.DiGraph()
        
        # Add all nodes
        for file in parsed_files:
            graph.add_node(file.path, data=file)
        
        # Create comprehensive module->file lookup
        module_to_file = {}
        for file in parsed_files:
            path_obj = Path(file.path)
            
            # 1. Full path
            module_to_file[file.path] = file.path
            
            # 2. Filename without extension
            stem = path_obj.stem
            if stem not in module_to_file:  # Don't overwrite if duplicate names
                module_to_file[stem] = file.path
            
            # 3. All parent paths
            parts = path_obj.parts
            for i in range(len(parts)):
                partial = '/'.join(parts[i:])
                module_to_file[partial] = file.path
                
                # Also add without extension
                partial_no_ext = partial.replace('.py', '').replace('.js', '').replace('.ts', '')
                module_to_file[partial_no_ext] = file.path
            
            # 4. Dot notation (all variations)
            if '/' in file.path:
                dot_notation = file.path.replace('/', '.')
                for ext in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                    dot_notation = dot_notation.replace(ext, '')
                module_to_file[dot_notation] = file.path
                
                # Partial dot notations
                dot_parts = dot_notation.split('.')
                for i in range(len(dot_parts)):
                    partial_dot = '.'.join(dot_parts[i:])
                    module_to_file[partial_dot] = file.path
        
        # Add edges based on imports
        edges_added = 0
        edges_seen = set()  # Prevent duplicates
        
        for file in parsed_files:
            for imp in file.imports:
                # Skip standard library/external imports (DYNAMIC)
                imp_base = imp.split('.')[0]  # Get base module
                if imp_base in self.stdlib_modules:
                    continue
                
                # Try to resolve import to a file
                target_file = self._resolve_import(imp, module_to_file, repo_path)
                
                if target_file and target_file in graph:
                    edge_key = (file.path, target_file)
                    if edge_key not in edges_seen:  # Prevent duplicates
                        graph.add_edge(file.path, target_file, type='imports')
                        edges_seen.add(edge_key)
                        edges_added += 1
        
        if self.debug:
            print(f"[DiagramBuilder] Added {edges_added} dependency edges")
        
        return graph
    
    def _resolve_import(self, import_name: str, module_to_file: Dict[str, str], repo_path: Path) -> Optional[str]:
        """Resolve import to actual file with improved matching"""
        # 1. Direct lookup (most common)
        if import_name in module_to_file:
            return module_to_file[import_name]
        
        # 2. Check if it's a relative import (starts with '.')
        if import_name.startswith('.'):
            # Remove leading dots
            clean_import = import_name.lstrip('.')
            if clean_import in module_to_file:
                return module_to_file[clean_import]
        
        # 3. Try all path variations
        variations = [
            import_name,
            import_name.replace('.', '/'),
            import_name.replace('.', '/') + '.py',
            import_name.replace('.', '/') + '.js',
            import_name.replace('.', '/') + '.ts',
            import_name.replace('.', '/') + '.jsx',
            import_name.replace('.', '/') + '.tsx',
            import_name + '.py',
            import_name + '.js',
            import_name + '.ts',
            import_name + '/__init__.py',
            import_name.split('.')[0],  # Base module
        ]
        
        for var in variations:
            if var in module_to_file:
                return module_to_file[var]
        
        # 4. Fuzzy matching (last resort)
        # Match if import name appears anywhere in the module path
        import_parts = import_name.replace('.', '/').split('/')
        for module_key, file_path in module_to_file.items():
            file_parts = file_path.replace('.', '/').split('/')
            
            # Check if all import parts appear in order in file path
            if all(part in file_parts for part in import_parts if part):
                return file_path
        
        return None
    
    def _detect_clusters(self, graph: nx.DiGraph, parsed_files: List[ParsedFile]) -> List[Cluster]:
        """Detect clusters (subsystems) using graph algorithms"""
        clusters = []
        
        # Use connected components for undirected version
        undirected = graph.to_undirected()
        components = list(nx.connected_components(undirected))
        
        for i, component in enumerate(components):
            if len(component) < 2:  # Skip single-file "clusters"
                continue
            
            files = list(component)
            
            # Infer cluster purpose from file names
            purpose = self._infer_cluster_purpose(files)
            
            # Find entry points (nodes with no incoming edges or high out-degree)
            entry_points = [
                node for node in files
                if graph.in_degree(node) == 0 or graph.out_degree(node) > 2
            ]
            
            cluster = Cluster(
                id=f"cluster_{i}",
                name=self._generate_cluster_name(files),
                files=files,
                purpose=purpose,
                entry_points=entry_points[:3]  # Top 3
            )
            
            clusters.append(cluster)
        
        return clusters
    
    def _infer_cluster_purpose(self, files: List[str]) -> str:
        """Infer cluster purpose from file names"""
        keywords = defaultdict(int)
        
        for file in files:
            parts = Path(file).parts
            for part in parts:
                # Extract words
                words = re.findall(r'\w+', part.lower())
                for word in words:
                    if len(word) > 2:  # Skip short words
                        keywords[word] += 1
        
        # Get most common keywords
        if keywords:
            most_common = max(keywords.items(), key=lambda x: x[1])
            return most_common[0]
        
        return "unknown"
    
    def _generate_cluster_name(self, files: List[str]) -> str:
        """Generate readable cluster name"""
        # Find common directory prefix
        if not files:
            return "cluster"
        
        paths = [Path(f).parts for f in files]
        
        # Find common prefix
        if len(paths) == 1:
            return paths[0][0] if paths[0] else "root"
        
        common = []
        for parts in zip(*paths):
            if len(set(parts)) == 1:
                common.append(parts[0])
            else:
                break
        
        return '/'.join(common) if common else "mixed"
    
    def _extract_metadata(self, parsed_files: List[ParsedFile], graph: nx.DiGraph) -> Dict:
        """Extract high-level metadata"""
        metadata = {
            'total_files': len(parsed_files),
            'languages': list(set(f.language for f in parsed_files)),
            'entry_points': self._find_entry_points(parsed_files),
            'hub_files': self._find_hub_files(graph),
        }
        
        return metadata
    
    def _find_entry_points(self, parsed_files: List[ParsedFile]) -> List[str]:
        """Find likely entry point files"""
        entry_names = {
            'main.py', 'app.py', 'index.js', 'index.ts', 'main.go',
            'main.rs', 'Main.java', 'manage.py', '__init__.py'
        }
        
        entry_points = []
        for file in parsed_files:
            filename = Path(file.path).name
            if filename in entry_names:
                entry_points.append(file.path)
        
        return entry_points[:5]
    
    def _find_hub_files(self, graph: nx.DiGraph) -> List[str]:
        """Find hub files (high connection count)"""
        degrees = dict(graph.degree())
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        
        return [node for node, degree in sorted_nodes[:10] if degree > 1]
    
    def _classify_node_type(self, file: ParsedFile) -> str:
        """Classify node type from file characteristics"""
        filename = Path(file.path).name.lower()
        
        if 'test' in filename:
            return 'test'
        elif 'model' in filename:
            return 'model'
        elif 'view' in filename or 'component' in filename:
            return 'view'
        elif 'controller' in filename or 'route' in filename:
            return 'controller'
        elif 'service' in filename or 'handler' in filename:
            return 'service'
        elif 'util' in filename or 'helper' in filename:
            return 'utility'
        elif 'config' in filename:
            return 'config'
        else:
            return 'module'
    
    def save_diagram(self, diagram: Diagram, output_dir: Path):
        """
        Save diagram in multiple formats.
        
        Args:
            diagram: Diagram to save
            output_dir: Directory to save files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = output_dir / 'dependency_graph.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'nodes': diagram.nodes,
                'edges': diagram.edges,
                'clusters': [asdict(c) for c in diagram.clusters],
                'metadata': diagram.metadata
            }, f, indent=2)
        
        if self.debug:
            print(f"[DiagramBuilder] Saved JSON: {json_path}")
        
        # Save Mermaid
        mermaid_path = output_dir / 'dependency_graph.mermaid'
        mermaid_content = self._generate_mermaid(diagram)
        with open(mermaid_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_content)
        
        if self.debug:
            print(f"[DiagramBuilder] Saved Mermaid: {mermaid_path}")
    
    def _generate_mermaid(self, diagram: Diagram) -> str:
        """Generate Mermaid diagram syntax"""
        lines = ["graph TD"]
        
        # Add nodes
        for node in diagram.nodes[:50]:  # Limit for readability
            node_id = self._sanitize_mermaid_id(node['id'])
            label = Path(node['id']).name
            lines.append(f'    {node_id}["{label}"]')
        
        # Add edges
        for edge in diagram.edges[:100]:  # Limit for readability
            from_id = self._sanitize_mermaid_id(edge['from'])
            to_id = self._sanitize_mermaid_id(edge['to'])
            lines.append(f'    {from_id} --> {to_id}')
        
        return '\n'.join(lines)
    
    def _sanitize_mermaid_id(self, text: str) -> str:
        """Sanitize text for Mermaid node ID"""
        # Remove special characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        # Ensure it starts with a letter
        if not sanitized[0].isalpha():
            sanitized = 'n_' + sanitized
        return sanitized
    
    # ==========================================================================
    # DIAGRAM MODIFICATION METHODS
    # ==========================================================================
    
    def load_diagram(self, diagram_path: Path) -> Optional[Diagram]:
        """
        Load a saved diagram from JSON file.
        
        Args:
            diagram_path: Path to dependency_graph.json
            
        Returns:
            Diagram object or None if failed
        """
        try:
            with open(diagram_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct Cluster objects
            clusters = []
            for c in data.get('clusters', []):
                clusters.append(Cluster(
                    id=c.get('id', ''),
                    name=c.get('name', ''),
                    files=c.get('files', []),
                    purpose=c.get('purpose', ''),
                    entry_points=c.get('entry_points', [])
                ))
            
            return Diagram(
                nodes=data.get('nodes', []),
                edges=data.get('edges', []),
                clusters=clusters,
                metadata=data.get('metadata', {})
            )
        except Exception as e:
            if self.debug:
                print(f"[DiagramBuilder] Failed to load diagram: {e}")
            return None
    
    def add_node(self, diagram: Diagram, node_id: str, language: str = 'python',
                 node_type: str = 'module', functions: List[str] = None,
                 classes: List[str] = None, imports: List[str] = None) -> Diagram:
        """
        Add a new node to the diagram.
        
        Args:
            diagram: Existing Diagram object
            node_id: Unique identifier (usually file path)
            language: Programming language
            node_type: Type of node (module, service, model, etc.)
            functions: List of function names
            classes: List of class names
            imports: List of imports
            
        Returns:
            Updated Diagram object
        """
        # Check if node already exists
        existing_ids = [n['id'] for n in diagram.nodes]
        if node_id in existing_ids:
            if self.debug:
                print(f"[DiagramBuilder] Node {node_id} already exists")
            return diagram
        
        new_node = {
            'id': node_id,
            'language': language,
            'type': node_type,
            'functions': functions or [],
            'classes': classes or [],
            'imports': imports or []
        }
        
        diagram.nodes.append(new_node)
        diagram.metadata['total_files'] = len(diagram.nodes)
        
        if self.debug:
            print(f"[DiagramBuilder] Added node: {node_id}")
        
        return diagram
    
    def remove_node(self, diagram: Diagram, node_id: str) -> Diagram:
        """
        Remove a node and all its edges from the diagram.
        
        Args:
            diagram: Existing Diagram object
            node_id: Node ID to remove
            
        Returns:
            Updated Diagram object
        """
        # Remove node
        diagram.nodes = [n for n in diagram.nodes if n['id'] != node_id]
        
        # Remove all edges involving this node
        diagram.edges = [
            e for e in diagram.edges 
            if e['from'] != node_id and e['to'] != node_id
        ]
        
        # Update clusters
        for cluster in diagram.clusters:
            if node_id in cluster.files:
                cluster.files.remove(node_id)
            if node_id in cluster.entry_points:
                cluster.entry_points.remove(node_id)
        
        # Remove empty clusters
        diagram.clusters = [c for c in diagram.clusters if len(c.files) > 0]
        
        diagram.metadata['total_files'] = len(diagram.nodes)
        
        if self.debug:
            print(f"[DiagramBuilder] Removed node: {node_id}")
        
        return diagram
    
    def add_edge(self, diagram: Diagram, from_node: str, to_node: str,
                 edge_type: str = 'imports') -> Diagram:
        """
        Add a new edge (dependency) between nodes.
        
        Args:
            diagram: Existing Diagram object
            from_node: Source node ID
            to_node: Target node ID
            edge_type: Type of relationship (imports, calls, etc.)
            
        Returns:
            Updated Diagram object
        """
        # Check if nodes exist
        node_ids = [n['id'] for n in diagram.nodes]
        if from_node not in node_ids or to_node not in node_ids:
            if self.debug:
                print(f"[DiagramBuilder] Cannot add edge: node not found")
            return diagram
        
        # Check if edge already exists
        for edge in diagram.edges:
            if edge['from'] == from_node and edge['to'] == to_node:
                if self.debug:
                    print(f"[DiagramBuilder] Edge already exists")
                return diagram
        
        new_edge = {
            'from': from_node,
            'to': to_node,
            'type': edge_type
        }
        
        diagram.edges.append(new_edge)
        
        if self.debug:
            print(f"[DiagramBuilder] Added edge: {from_node} -> {to_node}")
        
        return diagram
    
    def remove_edge(self, diagram: Diagram, from_node: str, to_node: str) -> Diagram:
        """
        Remove an edge between nodes.
        
        Args:
            diagram: Existing Diagram object
            from_node: Source node ID
            to_node: Target node ID
            
        Returns:
            Updated Diagram object
        """
        diagram.edges = [
            e for e in diagram.edges
            if not (e['from'] == from_node and e['to'] == to_node)
        ]
        
        if self.debug:
            print(f"[DiagramBuilder] Removed edge: {from_node} -> {to_node}")
        
        return diagram
    
    def update_node(self, diagram: Diagram, node_id: str, 
                    updates: Dict[str, Any]) -> Diagram:
        """
        Update an existing node's properties.
        
        Args:
            diagram: Existing Diagram object
            node_id: Node ID to update
            updates: Dictionary of properties to update
            
        Returns:
            Updated Diagram object
        """
        for node in diagram.nodes:
            if node['id'] == node_id:
                for key, value in updates.items():
                    if key != 'id':  # Never change the ID
                        node[key] = value
                
                if self.debug:
                    print(f"[DiagramBuilder] Updated node: {node_id}")
                break
        
        return diagram
    
    def merge_diagrams(self, base: Diagram, other: Diagram) -> Diagram:
        """
        Merge two diagrams together.
        
        Args:
            base: Base Diagram to merge into
            other: Other Diagram to merge from
            
        Returns:
            Merged Diagram object
        """
        existing_node_ids = set(n['id'] for n in base.nodes)
        
        # Add new nodes
        for node in other.nodes:
            if node['id'] not in existing_node_ids:
                base.nodes.append(node)
                existing_node_ids.add(node['id'])
        
        # Add new edges
        existing_edges = set((e['from'], e['to']) for e in base.edges)
        for edge in other.edges:
            edge_tuple = (edge['from'], edge['to'])
            if edge_tuple not in existing_edges:
                base.edges.append(edge)
                existing_edges.add(edge_tuple)
        
        # Update metadata
        base.metadata['total_files'] = len(base.nodes)
        base.metadata['languages'] = list(set(
            base.metadata.get('languages', []) + 
            other.metadata.get('languages', [])
        ))
        
        if self.debug:
            print(f"[DiagramBuilder] Merged diagrams: {len(base.nodes)} nodes, {len(base.edges)} edges")
        
        return base


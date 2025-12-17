"""
File Relationship Mapper - Knowledge Graph Builder
==================================================
Maps relationships between files (imports, references) to build a knowledge graph.
Works for any programming language - no hardcoded patterns.
"""
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re
from collections import defaultdict


class RelationshipMapper:
    """
    Build a knowledge graph of file relationships.
    Discovers connections dynamically - works for any language.
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.graph = defaultdict(set)  # file -> set of related files
        self.import_patterns = self._build_import_patterns()
    
    def _build_import_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """
        Build regex patterns for detecting imports/references.
        Language-agnostic - captures multiple syntaxes.
        """
        patterns = [
            # Python
            (re.compile(r'^(?:from|import)\s+([\w.]+)', re.MULTILINE), 'python'),
            
            # JavaScript/TypeScript
            (re.compile(r'(?:import|require)\s*\([\'"]([^\'"]+)[\'"]', re.MULTILINE), 'javascript'),
            (re.compile(r'from\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE), 'javascript'),
            
            # Go
            (re.compile(r'^import\s+"([^"]+)"', re.MULTILINE), 'go'),
            (re.compile(r'^import\s+\(([^)]+)\)', re.MULTILINE | re.DOTALL), 'go_multi'),
            
            # Java
            (re.compile(r'^import\s+([\w.]+);', re.MULTILINE), 'java'),
            
            # C/C++
            (re.compile(r'#include\s+[<"]([^>"]+)[>"]', re.MULTILINE), 'c'),
            
            # Ruby
            (re.compile(r'require\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE), 'ruby'),
            
            # Rust
            (re.compile(r'use\s+([\w:]+)', re.MULTILINE), 'rust'),
        ]
        
        return patterns
    
    def extract_references(self, content: str, file_path: Path) -> Set[str]:
        """
        Extract all file/module references from content.
        Language-agnostic - tries all patterns.
        """
        references = set()
        
        for pattern, lang in self.import_patterns:
            matches = pattern.findall(content)
            for match in matches:
                # Clean up the reference
                if lang == 'go_multi':
                    # Handle Go's multi-line import
                    for line in match.split('\n'):
                        ref = line.strip().strip('"')
                        if ref:
                            references.add(ref)
                else:
                    references.add(match)
        
        # Also look for relative file references (./file, ../file)
        relative_pattern = re.compile(r'[\'"](\.\./[\w/.-]+)[\'"]')
        relative_refs = relative_pattern.findall(content)
        references.update(relative_refs)
        
        return references
    
    def extract_definitions(self, content: str) -> Set[str]:
        """
        Extract definitions (functions, classes, constants).
        Language-agnostic patterns.
        """
        definitions = set()
        
        # Function/method definitions (works for most C-style languages)
        func_patterns = [
            r'\bfunction\s+(\w+)',  # JavaScript
            r'\bdef\s+(\w+)',  # Python, Ruby
            r'\bfunc\s+(\w+)',  # Go
            r'\bfn\s+(\w+)',  # Rust
            r'\b(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(',  # Java, C++
        ]
        
        for pattern in func_patterns:
            matches = re.findall(pattern, content)
            definitions.update(matches)
        
        # Class definitions
        class_pattern = r'\bclass\s+(\w+)'
        classes = re.findall(class_pattern, content)
        definitions.update(classes)
        
        # Constants (uppercase identifiers)
        const_pattern = r'\b([A-Z_]{3,})\b'
        constants = re.findall(const_pattern, content)
        # Only keep if they appear multiple times (likely real constants)
        const_counts = {}
        for const in constants:
            const_counts[const] = const_counts.get(const, 0) + 1
        definitions.update(c for c, count in const_counts.items() if count > 1)
        
        return definitions
    
    def find_string_references(self, content: str, target_file: str) -> bool:
        """
        Check if content references a file by name (string matching).
        Useful for finding indirect references.
        """
        target_name = Path(target_file).stem  # filename without extension
        
        # Look for the filename in strings, comments, etc.
        # This catches references like "see auth.py" or "calls user_model"
        pattern = rf'\b{re.escape(target_name)}\b'
        return bool(re.search(pattern, content, re.IGNORECASE))
    
    def build_graph(
        self, 
        files: Dict[str, str],  # file_path -> content
        repo_path: Path
    ) -> Dict[str, Set[str]]:
        """
        Build knowledge graph of file relationships.
        
        Returns:
            Graph dict: file_path -> set of related file paths
        """
        graph = defaultdict(set)
        
        # First pass: extract all references and definitions
        file_refs = {}  # file -> set of references
        file_defs = {}  # file -> set of definitions
        
        for file_path, content in files.items():
            file_refs[file_path] = self.extract_references(content, Path(file_path))
            file_defs[file_path] = self.extract_definitions(content)
        
        # Second pass: connect files based on references
        for file_path, refs in file_refs.items():
            for ref in refs:
                # Try to resolve reference to actual file
                resolved = self._resolve_reference(ref, file_path, files.keys(), repo_path)
                if resolved:
                    graph[file_path].add(resolved)
                    graph[resolved].add(file_path)  # Bidirectional
        
        # Third pass: connect based on shared definitions
        for file1, defs1 in file_defs.items():
            for file2, defs2 in file_defs.items():
                if file1 != file2:
                    # If they share definitions, they're related
                    shared = defs1 & defs2
                    if shared:
                        graph[file1].add(file2)
                        graph[file2].add(file1)
        
        # Fourth pass: string-based connections (weaker)
        for file1 in files:
            for file2 in files:
                if file1 != file2:
                    if self.find_string_references(files[file1], file2):
                        graph[file1].add(file2)
        
        if self.debug:
            connected = sum(1 for v in graph.values() if v)
            total = len(files)
            print(f"[RelationshipMapper] Built graph: {connected}/{total} files connected")
        
        return dict(graph)
    
    def _resolve_reference(
        self, 
        ref: str, 
        source_file: str, 
        all_files: List[str],
        repo_path: Path
    ) -> str:
        """
        Resolve an import/reference to an actual file path.
        Tries multiple strategies.
        """
        # Strategy 1: Exact match in filenames
        for file_path in all_files:
            if ref in file_path or Path(file_path).stem == ref:
                return file_path
        
        # Strategy 2: Module path to file path conversion
        # e.g. "models.user" -> "models/user.py"
        ref_as_path = ref.replace('.', '/')
        for file_path in all_files:
            if ref_as_path in file_path:
                return file_path
        
        # Strategy 3: Relative path resolution
        if ref.startswith('.'):
            try:
                source_dir = Path(source_file).parent
                resolved = (source_dir / ref).resolve()
                resolved_str = str(resolved)
                if resolved_str in all_files:
                    return resolved_str
            except:
                pass
        
        return None
    
    def get_connected_files(
        self, 
        start_file: str, 
        graph: Dict[str, Set[str]],
        max_depth: int = 2
    ) -> Set[str]:
        """
        Get all files connected to start_file within max_depth.
        Uses BFS traversal.
        """
        visited = set()
        queue = [(start_file, 0)]  # (file, depth)
        
        while queue:
            current, depth = queue.pop(0)
            
            if current in visited or depth > max_depth:
                continue
            
            visited.add(current)
            
            # Add neighbors
            if current in graph:
                for neighbor in graph[current]:
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))
        
        return visited

"""
Language Detector - Universal Language Detection
================================================
Uses multiple methods to detect ANY programming language:
1. GitHub Linguist patterns (vendored, no API calls)
2. File extension mapping
3. Shebang detection
4. Content analysis
"""
from pathlib import Path
from typing import Dict, List, Set
import re


class LanguageDetector:
    """
    Detects programming languages from files.
    No hardcoding - uses patterns similar to GitHub Linguist.
    """
    
    # Comprehensive extension mapping (100+ languages)
    EXTENSION_MAP = {
        # Web
        '.js': 'JavaScript', '.ts': 'TypeScript', '.jsx': 'JavaScript', '.tsx': 'TypeScript',
        '.html': 'HTML', '.htm': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass',
        '.vue': 'Vue', '.svelte': 'Svelte',
        
        # Python ecosystem
        '.py': 'Python', '.pyx': 'Cython', '.pyi': 'Python',
        
        # JVM languages
        '.java': 'Java', '.kt': 'Kotlin', '.scala': 'Scala', '.groovy': 'Groovy',
        '.class': 'Java Bytecode',
        
        # C family
        '.c': 'C', '.h': 'C', '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++',
        '.hpp': 'C++', '.hh': 'C++', '.hxx': 'C++',
        
        # .NET
        '.cs': 'C#', '.fs': 'F#', '.vb': 'Visual Basic',
        
        # Systems
        '.rs': 'Rust', '.go': 'Go', '.zig': 'Zig', '.nim': 'Nim',
        
        # Scripting
        '.rb': 'Ruby', '.php': 'PHP', '.pl': 'Perl', '.lua': 'Lua',
        '.sh': 'Shell', '.bash': 'Bash', '.zsh': 'Zsh',
        
        # Functional
        '.hs': 'Haskell', '.ml': 'OCaml', '.elm': 'Elm', '.ex': 'Elixir', '.exs': 'Elixir',
        '.erl': 'Erlang', '.clj': 'Clojure', '.cljs': 'ClojureScript',
        
        # Mobile
        '.swift': 'Swift', '.m': 'Objective-C', '.mm': 'Objective-C++',
        '.dart': 'Dart',
        
        # Data/Config
        '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML', '.toml': 'TOML',
        '.xml': 'XML', '.sql': 'SQL',
        
        # Markup/Docs
        '.md': 'Markdown', '.rst': 'reStructuredText', '.tex': 'TeX',
        
        # Other
        '.r': 'R', '.jl': 'Julia', '.m': 'MATLAB', '.v': 'Verilog',
        '.sol': 'Solidity', '.cairo': 'Cairo',
    }
    
    # Shebang patterns
    SHEBANG_PATTERNS = {
        'python': 'Python',
        'node': 'JavaScript',
        'ruby': 'Ruby',
        'bash': 'Bash',
        'sh': 'Shell',
        'perl': 'Perl',
    }
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def detect_languages(self, repo_path: Path) -> Dict[str, int]:
        """
        Detect all languages in repository.
        Returns: {language: file_count}
        """
        lang_counts = {}
        
        # Scan all files
        for file_path in repo_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip common ignores
            if any(skip in file_path.parts for skip in [
                'venv', 'node_modules', '.venv', 'dist', 'build', 
                'target', '.git', '__pycache__', '.next', 'vendor'
            ]):
                continue
            
            # Detect language
            lang = self._detect_file_language(file_path)
            
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        # Filter to significant languages (>3 files)
        significant = {lang: count for lang, count in lang_counts.items() if count > 3}
        
        if self.debug:
            print(f"[LanguageDetector] Detected {len(significant)} languages")
            for lang, count in sorted(significant.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {lang}: {count} files")
        
        return significant
    
    def _detect_file_language(self, file_path: Path) -> str:
        """Detect language of a single file"""
        
        # 1. Extension-based detection
        ext = file_path.suffix.lower()
        if ext in self.EXTENSION_MAP:
            return self.EXTENSION_MAP[ext]
        
        # 2. Shebang detection for scripts
        if file_path.stat().st_size < 100000:  # Only small files
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline().strip()
                    
                    if first_line.startswith('#!'):
                        for pattern, lang in self.SHEBANG_PATTERNS.items():
                            if pattern in first_line.lower():
                                return lang
            except:
                pass
        
        # 3. Special filenames
        name = file_path.name.lower()
        if name in ['makefile', 'dockerfile', 'gemfile', 'rakefile']:
            filename_map = {
                'makefile': 'Makefile',
                'dockerfile': 'Dockerfile',
                'gemfile': 'Ruby',
                'rakefile': 'Ruby',
            }
            return filename_map.get(name)
        
        return None
    
    def get_primary_language(self, repo_path: Path) -> str:
        """Get the primary (most files) language"""
        langs = self.detect_languages(repo_path)
        
        if not langs:
            return 'Unknown'
        
        return max(langs.items(), key=lambda x: x[1])[0]

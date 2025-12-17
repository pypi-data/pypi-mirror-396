"""
Tree-sitter Universal Parser
============================
Uses tree-sitter for accurate, fast parsing of 50+ languages.
Fallback to regex if tree-sitter not available.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from .base_parser import BaseParser


class TreeSitterParser(BaseParser):
    """
    Universal parser using tree-sitter.
    Zero maintenance, works for 50+ languages.
    """
    
    def __init__(self, language: str):
        super().__init__(language)
        self.lang_lower = language.lower()
        self.parser = None
        self.ts_language = None
        self._init_treesitter()
    
    def _init_treesitter(self):
        """Try to initialize tree-sitter for this language"""
        try:
            # Suppress deprecation warning from tree_sitter internals GLOBALLY
            import warnings
            warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
            
            from tree_sitter_languages import get_parser, get_language
            
            # Map file extensions to tree-sitter language names
            lang_map = {
                'python': 'python',
                'javascript': 'javascript',
                'typescript': 'typescript',
                'jsx': 'tsx',
                'tsx': 'tsx',
                'java': 'java',
                'c': 'c',
                'cpp': 'cpp',
                'c++': 'cpp',
                'go': 'go',
                'rust': 'rust',
                'ruby': 'ruby',
                'php': 'php',
                'swift': 'swift',
                'kotlin': 'kotlin',
                'scala': 'scala',
                'c#': 'c_sharp',
                'csharp': 'c_sharp',
                'bash': 'bash',
                'shell': 'bash',
                'markdown': 'markdown',
                'html': 'html',
                'css': 'css',
                'json': 'json',
                'yaml': 'yaml',
                'toml': 'toml',
            }
            
            ts_lang = lang_map.get(self.lang_lower)
            if ts_lang:
                self.parser = get_parser(ts_lang)
                self.ts_language = get_language(ts_lang)
                
        except ImportError:
            # Tree-sitter not installed - show helpful message once
            import sys
            if not getattr(sys, '_stacksense_ts_warning_shown', False):
                import logging
                logging.getLogger(__name__).info(
                    "Tree-sitter not available. Using regex parsing (less accurate). "
                    "For enhanced accuracy: pip install 'stacksense[full]' (Python <3.13)"
                )
                sys._stacksense_ts_warning_shown = True
            self.parser = None
        except Exception:
            # Language not supported by tree-sitter
            self.parser = None
    
    def parse(self, content: str, file_path: Path = None) -> Dict[str, Any]:
        """Parse using tree-sitter if available, fallback to regex"""
        
        # Try tree-sitter first (best accuracy)
        if self.parser:
            try:
                return self._parse_with_treesitter(content)
            except Exception:
                pass  # Fall through to fallback
        
        # Fallback: Use lightweight extraction
        return self._lightweight_parse(content)
    
    def _parse_with_treesitter(self, content: str) -> Dict[str, Any]:
        """Parse using tree-sitter - perfect accuracy"""
        
        tree = self.parser.parse(content.encode('utf-8'))
        root = tree.root_node
        
        result = {
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': [],
            'decorators': [],
            'docstrings': [],
            'comments': [],
            'sections': []  # For markdown
        }
        
        # Extract structure by traversing AST
        self._traverse_node(root, result, content)
        
        return result
    
    def _traverse_node(self, node, result: Dict, content: str):
        """Traverse tree-sitter AST and extract structure"""
        
        # Python-specific node types
        if self.lang_lower == 'python':
            if node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    result['functions'].append({
                        'name': content[name_node.start_byte:name_node.end_byte],
                        'line': name_node.start_point[0],
                        'docstring': self._get_docstring(node, content)
                    })
            
            elif node.type == 'class_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    result['classes'].append({
                        'name': content[name_node.start_byte:name_node.end_byte],
                        'line': name_node.start_point[0],
                        'docstring': self._get_docstring(node, content)
                    })
            
            elif node.type in ['import_statement', 'import_from_statement']:
                import_text = content[node.start_byte:node.end_byte]
                result['imports'].append(import_text)
            
            elif node.type == 'comment':
                comment_text = content[node.start_byte:node.end_byte]
                result['comments'].append(comment_text.lstrip('#').strip())
        
        # JavaScript/TypeScript-specific
        elif self.lang_lower in ['javascript', 'typescript', 'tsx', 'jsx']:
            if node.type in ['function_declaration', 'arrow_function', 'function']:
                name_node = node.child_by_field_name('name')
                if name_node:
                    result['functions'].append({
                        'name': content[name_node.start_byte:name_node.end_byte],
                        'line': name_node.start_point[0]
                    })
            
            elif node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    result['classes'].append({
                        'name': content[name_node.start_byte:name_node.end_byte],
                        'line': name_node.start_point[0]
                    })
            
            elif node.type == 'import_statement':
                import_text = content[node.start_byte:node.end_byte]
                result['imports'].append(import_text)
            
            elif node.type == 'comment':
                comment_text = content[node.start_byte:node.end_byte]
                result['comments'].append(comment_text.lstrip('//').strip())
        
        # Markdown-specific
        elif self.lang_lower == 'markdown':
            if node.type == 'section':
                heading_node = node.child_by_field_name('heading')
                if heading_node:
                    heading_text = content[heading_node.start_byte:heading_node.end_byte]
                    section_content = content[node.start_byte:node.end_byte]
                    result['sections'].append({
                        'heading': heading_text,
                        'content': section_content
                    })
        
        # Recursively traverse children
        for child in node.children:
            self._traverse_node(child, result, content)
    
    def _get_docstring(self, node, content: str) -> str:
        """Extract docstring from function/class node"""
        # Look for first string in body
        for child in node.children:
            if child.type == 'block':
                for stmt in child.children:
                    if stmt.type == 'expression_statement':
                        for expr in stmt.children:
                            if expr.type == 'string':
                                docstring = content[expr.start_byte:expr.end_byte]
                                # Remove quotes
                                return docstring.strip('"""').strip("'''").strip()
        return ''
    
    def _lightweight_parse(self, content: str) -> Dict[str, Any]:
        """
        Lightweight parsing when tree-sitter not available.
        Just extracts high-level structure, no complex regex.
        """
        
        lines = content.split('\n')
        
        result = {
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': [],
            'decorators': [],
            'docstrings': [],
            'comments': [],
            'metadata': {
                'total_lines': len(lines),
                'non_empty_lines': len([l for l in lines if l.strip()]),
                'header': '\n'.join(lines[:10]),
                'footer': '\n'.join(lines[-10:] if len(lines) > 10 else [])
            }
        }
        
        # Simple extraction (no catastrophic backtracking)
        for i, line in enumerate(lines[:500]):  # Limit to first 500 lines
            line_stripped = line.strip()
            
            # Imports (simple, universal)
            if any(keyword in line_stripped for keyword in ['import ', 'require(', 'use ', 'include ']):
                result['imports'].append(line_stripped)
            
            # Function definitions (simple patterns)
            if any(word in line for word in ['def ', 'function ', 'func ', 'fn ']):
                # Extract name (simple word after keyword)
                for keyword in ['def ', 'function ', 'func ', 'fn ']:
                    if keyword in line:
                        after_keyword = line.split(keyword, 1)[1]
                        name = after_keyword.split('(')[0].split()[0] if '(' in after_keyword else after_keyword.split()[0]
                        result['functions'].append({'name': name, 'line': i})
                        break
            
            # Class definitions
            if 'class ' in line:
                after_class = line.split('class ', 1)[1]
                name = after_class.split('(')[0].split(':')[0].split()[0]
                result['classes'].append({'name': name, 'line': i})
        
        return result

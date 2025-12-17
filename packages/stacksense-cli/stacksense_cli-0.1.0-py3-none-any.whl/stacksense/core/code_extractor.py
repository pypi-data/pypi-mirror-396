"""
Code Structure Extractor
=========================
Extract code structure from Python and TypeScript files using AST parsing.
Provides actual code details (fields, methods, signatures) to prevent AI hallucinations.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import re
from collections import defaultdict


class CodeExtractor:
    """Extract code structure using language-specific parsers"""
    
    def __init__(self, repo_path: Path, debug: bool = False):
        self.repo_path = Path(repo_path)
        self.debug = debug
        self.cache = {}  # file_path -> extracted structure
        self.critical_files_found = []  # Track what critical files we found
        
        # Detect languages/frameworks
        self.languages = self._detect_languages()
        self.frameworks = self._detect_frameworks()
        
        if self.debug:
            print(f"[Extractor] Languages: {self.languages}")
            print(f"[Extractor] Frameworks: {self.frameworks}")
    
    def _detect_languages(self) -> set:
        """Detect languages in repository"""
        languages = set()
        
        # Count file extensions
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.go': 'go',
            '.java': 'java',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
            '.ipynb': 'jupyter',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
        }
        
        for ext, lang in extensions.items():
            files = list(self.repo_path.rglob(f'*{ext}'))
            # Filter out venv, node_modules
            files = [f for f in files if not any(skip in f.parts for skip in ['venv', 'node_modules', '.venv', 'site-packages', 'dist', 'build'])]
            
            if len(files) > 3:  # At least 3 files to count as "using this language"
                languages.add(lang)
        
        return languages
    
    def _detect_frameworks(self) -> set:
        """Detect frameworks from manifest files"""
        frameworks = set()
        
        # Python frameworks
        if (self.repo_path / 'requirements.txt').exists() or (self.repo_path / 'setup.py').exists():
            # Could use actual content parsing here, but keeping it simple
            pass
        
        # JavaScript frameworks
        if (self.repo_path / 'package.json').exists():
            frameworks.add('node')
        
        # Go
        if (self.repo_path / 'go.mod').exists():
            frameworks.add('go')
        
        # Java/Maven
        if (self.repo_path / 'pom.xml').exists():
            frameworks.add('maven')
        
        # Ruby
        if (self.repo_path / 'Gemfile').exists():
            frameworks.add('ruby')
        
        return frameworks
    
    def _generate_critical_patterns(self) -> List[str]:
        """
        Generate critical file patterns based on detected languages/frameworks.
        This is DYNAMIC, not hardcoded!
        """
        patterns = []
        
        # Python patterns
        if 'python' in self.languages:
            patterns.extend([
                '/models/', 'models.py',  # Django/SQLAlchemy models
                '/views/', 'views.py',     # MVC views
                '/serializers/', 'serializer',  # API serializers
                '/schemas/', 'schema.py',  # Schema definitions
                '/services/', 'service.py',  # Business logic
                '/controllers/', 'controller',  # Controllers
                'app.py', 'main.py', '__init__.py',  # Entry points
            ])
            
            # ML-specific patterns for Python
            if any((self.repo_path / f).exists() for f in ['requirements.txt', 'environment.yml']):
                patterns.extend([
                    'model.pkl', 'model.h5', 'model.pt',  # Trained models
                    '/models/', 'train.py', 'inference.py',  # ML code
                    'dataset.py', 'preprocessing.py',
                ])
        
        # JavaScript/TypeScript patterns
        if 'javascript' in self.languages or 'typescript' in self.languages:
            patterns.extend([
                '/models/', '/schemas/',  # Data models
                '/controllers/', '/routes/',  # API structure  
                '/services/', '/utils/',  # Business logic
                'index.ts', 'index.js', 'app.ts', 'app.js',  # Entry points
                '/api/', '/pages/',  # Next.js/React structure
            ])
        
        # Go patterns
        if 'go' in self.languages:
            patterns.extend([
                '/models/', '/entities/',  # Data models
                '/handlers/', '/controllers/',  # HTTP handlers
                '/services/', '/repositories/',  # Business logic
                'main.go', 'server.go',  # Entry points
            ])
        
        # Java patterns
        if 'java' in self.languages:
            patterns.extend([
                '/models/', '/entities/', '/domain/',  # Domain models
                '/controllers/', '/resources/',  # REST controllers
                '/services/', '/repositories/',  # Service layer
                'Application.java', 'Main.java',  # Entry points
            ])
        
        # Ruby/Rails patterns
        if 'ruby' in self.languages:
            patterns.extend([
                '/models/', '/app/models/',  # ActiveRecord models
                '/controllers/', '/app/controllers/',  # Controllers
                '/services/', '/lib/',  # Business logic
            ])
        
        # Generic patterns (work for most languages)
        patterns.extend([
            '/core/', '/src/', '/lib/',  # Core code directories
            'config', 'settings',  # Configuration
            'test', 'spec',  # Tests (can be important)
        ])
        
        return patterns
    
    def _is_critical_file(self, file_path: Path) -> bool:
        """Check if file matches dynamically generated critical patterns"""
        file_str = str(file_path).lower()
        
        # Generate patterns on first call
        if not hasattr(self, '_critical_patterns_cache'):
            self._critical_patterns_cache = self._generate_critical_patterns()
        
        for pattern in self._critical_patterns_cache:
            if pattern in file_str:
                return True
        
        return False
    
    def _find_critical_files(self) -> List[Path]:
        """Find all critical files in repository"""
        
        critical_files = []
        
        # Search based on detected languages
        for lang in self.languages:
            if lang == 'python':
                file_pattern = '*.py'
            elif lang in ['javascript', 'typescript']:
                file_pattern = '*.[jt]s*'
            elif lang == 'go':
                file_pattern = '*.go'
            elif lang == 'java':
                file_pattern = '*.java'
            elif lang == 'ruby':
                file_pattern = '*.rb'
            elif lang == 'jupyter':
                file_pattern = '*.ipynb'
            else:
                continue
            
            for file in self.repo_path.rglob(file_pattern):
                # Skip common ignore patterns
                if any(skip in file.parts for skip in ['venv', 'node_modules', '.venv', 'site-packages', 'dist', 'build', 'target', '.git']):
                    continue
                
                if self._is_critical_file(file):
                    critical_files.append(file)
        
        if self.debug:
            print(f"[Extractor] 🔥 Found {len(critical_files)} critical files from patterns")
        
        self.critical_files_found = critical_files
        return critical_files
    
    def extract_all(self, file_paths: List[Path]) -> Dict[str, Any]:
        """
        Extract code structure from multiple files.
        
        Args:
            file_paths: List of file paths to extract from
        
        Returns:
            Dict mapping file paths to extracted structures
        """
        structures = {}
        
        for file_path in file_paths:
            try:
                if file_path.suffix == '.py':
                    structures[str(file_path)] = self.extract_python(file_path)
                elif file_path.suffix in ['.ts', '.tsx', '.js', '.jsx']:
                    structures[str(file_path)] = self.extract_typescript(file_path)
            except Exception as e:
                if self.debug:
                    print(f"[Extractor] Failed to extract {file_path}: {e}")
        
        return structures
    
    
    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Universal extraction method - works for ANY file type dynamically.
        No hardcoding - adapts based on file extension.
        """
        if str(file_path) in self.cache:
            return self.cache[str(file_path)]
        
        suffix = file_path.suffix.lower()
        result = {}
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Python files - use AST
            if suffix == '.py':
                result = self._extract_python_ast(content)
            
            # JavaScript/TypeScript - regex patterns
            elif suffix in ['.js', '.jsx', '.ts', '.tsx']:
                result = self._extract_javascript_patterns(content)
            
            # Markdown - extract sections and content
            elif suffix in ['.md', '.markdown']:
                result = self._extract_markdown_structure(content)
            
            # HTML - extract structure
            elif suffix in ['.html', '.htm']:
                result = self._extract_html_structure(content)
            
            # Config files - parse as key-value
            elif suffix in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
                result = self._extract_config_content(content, suffix)
            
            # Generic text files - extract sections
            else:
                result = self._extract_generic_text(content)
            
            # Add metadata
            result['file_type'] = suffix
            result['file_name'] = file_path.name
            result['size'] = len(content)
            
            self.cache[str(file_path)] = result
            return result
        
        except Exception as e:
            if self.debug:
                print(f"[Extractor] Error extracting {file_path.name}: {str(e)[:50]}")
            return {'error': str(e), 'file_type': suffix}
    
    def _extract_python_ast(self, content: str) -> Dict[str, Any]:
        """Extract Python using AST"""
        try:
            tree = ast.parse(content)
            
            result = {
                'classes': [],
                'functions': [],
                'constants': {},
                'imports': []
            }
            
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    result['classes'].append(self._extract_class(node, content))
                elif isinstance(node, ast.FunctionDef):
                    result['functions'].append(self._extract_function(node))
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            result['constants'][target.id] = self._extract_value(node.value)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    result['imports'].extend(self._extract_imports(node))
            
            return result
        except:
            return {'classes': [], 'functions': [], 'error': 'AST parse failed'}
    
    def _extract_javascript_patterns(self, content: str) -> Dict[str, Any]:
        """Extract JavaScript/TypeScript using regex patterns"""
        result = {
            'functions': [],
            'classes': [],
            'exports': [],
            'interfaces': [],
            'types': []
        }
        
        # Extract functions
        func_patterns = [
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(',
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
        ]
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                result['functions'].append({'name': match.group(1)})
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, content):
            result['classes'].append({
                'name': match.group(1),
                'extends': match.group(2) if match.group(2) else None
            })
        
        # Extract interfaces (TypeScript)
        interface_pattern = r'interface\s+(\w+)\s*{'
        for match in re.finditer(interface_pattern, content):
            result['interfaces'].append({'name': match.group(1)})
        
        # Extract type definitions (TypeScript)
        type_pattern = r'type\s+(\w+)\s*='
        for match in re.finditer(type_pattern, content):
            result['types'].append({'name': match.group(1)})
        
        return result
    
    def _extract_markdown_structure(self, content: str) -> Dict[str, Any]:
        """Extract markdown sections and key content"""
        result = {
            'headings': [],
            'sections': {},
            'code_blocks': [],
            'links': []
        }
        
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Extract headings
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                heading = line.lstrip('#').strip()
                result['headings'].append({
                    'level': level,
                    'text': heading
                })
                
                # Save previous section
                if current_section:
                    result['sections'][current_section] = '\n'.join(current_content)
                
                current_section = heading
                current_content = []
            else:
                current_content.append(line)
            
            # Extract code blocks
            if line.strip().startswith('```'):
                lang = line.strip()[3:].strip()
                if lang:
                    result['code_blocks'].append({'language': lang})
            
            # Extract links
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            for match in re.finditer(link_pattern, line):
                result['links'].append({
                    'text': match.group(1),
                    'url': match.group(2)
                })
        
        # Save last section
        if current_section:
            result['sections'][current_section] = '\n'.join(current_content)
        
        # Add full content preview (first 1000 chars)
        result['preview'] = content[:1000]
        
        return result
    
    def _extract_html_structure(self, content: str) -> Dict[str, Any]:
        """Extract HTML structure"""
        result = {
            'title': '',
            'headings': [],
            'forms': [],
            'scripts': []
        }
        
        # Extract title
        title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            result['title'] = title_match.group(1)
        
        # Extract headings
        for level in range(1, 7):
            pattern = f'<h{level}[^>]*>([^<]+)</h{level}>'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                result['headings'].append({
                    'level': level,
                    'text': match.group(1).strip()
                })
        
        # Extract forms
        form_pattern = r'<form[^>]*>'
        result['forms'] = [{'found': True} for _ in re.finditer(form_pattern, content, re.IGNORECASE)]
        
        return result
    
    def _extract_config_content(self, content: str, suffix: str) -> Dict[str, Any]:
        """Extract config file content"""
        result = {'type': 'config', 'format': suffix}
        
        try:
            if suffix == '.json':
                import json
                data = json.loads(content)
                result['keys'] = list(data.keys()) if isinstance(data, dict) else []
                result['preview'] = str(data)[:500]
            elif suffix in ['.yaml', '.yml']:
                # Simple YAML key extraction
                keys = re.findall(r'^(\w+):', content, re.MULTILINE)
                result['keys'] = keys
                result['preview'] = content[:500]
            else:
                # Generic config
                result['preview'] = content[:500]
        except:
            result['preview'] = content[:500]
        
        return result
    
    def _extract_generic_text(self, content: str) -> Dict[str, Any]:
        """Extract from generic text files"""
        lines = content.split('\n')
        
        return {
            'type': 'text',
            'line_count': len(lines),
            'preview': content[:1000],
            'non_empty_lines': len([l for l in lines if l.strip()])
        }
    
    def _extract_class(self, node: ast.ClassDef, full_content: str) -> Dict[str, Any]:
        """Extract class structure including Django model fields"""
        
        class_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'bases': [self._get_name(base) for base in node.bases],
            'methods': [],
            'fields': {},
            'choices': {},
            'line_start': node.lineno,
            'line_end': node.end_lineno
        }
        
        # Extract methods and fields
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info['methods'].append(self._extract_function(item))
            
            elif isinstance(item, ast.Assign):
                # Check for CHOICES constants (Django models)
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        
                        # Django CHOICES pattern
                        if var_name.endswith('_CHOICES') or 'CHOICES' in var_name:
                            try:
                                choices_value = ast.literal_eval(ast.unparse(item.value))
                                class_info['choices'][var_name] = choices_value
                            except:
                                # Store as string if can't evaluate
                                class_info['choices'][var_name] = ast.unparse(item.value)
                        
                        # Model fields (models.CharField, etc.)
                        elif 'models.' in ast.unparse(item.value):
                            field_info = self._extract_django_field(item, full_content)
                            if field_info:
                                class_info['fields'][var_name] = field_info
        
        return class_info
    
    def _extract_django_field(self, node: ast.Assign, full_content: str) -> Optional[Dict]:
        """Extract Django model field details"""
        
        try:
            value_str = ast.unparse(node.value)
            
            # Basic field type
            field_type = None
            if 'CharField' in value_str:
                field_type = 'CharField'
            elif 'IntegerField' in value_str:
                field_type = 'IntegerField'
            elif 'BooleanField' in value_str:
                field_type = 'BooleanField'
            elif 'ForeignKey' in value_str:
                field_type = 'ForeignKey'
            elif 'DateTimeField' in value_str:
                field_type = 'DateTimeField'
            elif 'TextField' in value_str:
                field_type = 'TextField'
            
            if not field_type:
                return None
            
            field_info = {'type': field_type}
            
            # Extract common parameters
            if isinstance(node.value, ast.Call):
                for keyword in node.value.keywords:
                    if keyword.arg in ['max_length', 'default', 'null', 'blank', 'unique']:
                        try:
                            field_info[keyword.arg] = ast.literal_eval(ast.unparse(keyword.value))
                        except:
                            field_info[keyword.arg] = ast.unparse(keyword.value)
                    
                    # Choices reference
                    if keyword.arg == 'choices':
                        field_info['choices_ref'] = ast.unparse(keyword.value)
            
            return field_info
        
        except:
            return None
    
    def _extract_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract function/method signature"""
        
        return {
            'name': node.name,
            'params': [arg.arg for arg in node.args.args],
            'docstring': ast.get_docstring(node),
            'decorators': [self._get_name(dec) for dec in node.decorator_list],
            'line_start': node.lineno,
            'line_end': node.end_lineno,
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _extract_imports(self, node) -> List[str]:
        """Extract import statements"""
        
        imports = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)
        
        return imports
    
    def _extract_value(self, node) -> Any:
        """Extract value from AST node"""
        
        try:
            return ast.literal_eval(ast.unparse(node))
        except:
            return ast.unparse(node)
    
    def _get_name(self, node) -> str:
        """Get name from AST node"""
        
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return ast.unparse(node)
        else:
            return ast.unparse(node)
    
    def get_snippet(self, file_path: Path, start_line: int, end_line: int) -> str:
        """Get code snippet from file"""
        
        try:
            lines = file_path.read_text(encoding='utf-8').split('\n')
            snippet_lines = lines[start_line-1:end_line]
            return '\n'.join(snippet_lines)
        except:
            return ""
    
    def extract_for_modules(self, modules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract code structure for specific modules.
        Prioritizes: 1) Critical files, 2) Models/views, 3) Dependencies
        
        Args:
            modules: Dict of module info from scanner
        
        Returns:
            Enhanced modules with code extracts
        """
        # STEP 1: Find and extract ALL critical files first
        critical_files = self._find_critical_files()
        critical_extracts = {}
        
        for file_path in critical_files:
            if file_path.suffix == '.py':
                extract = self.extract_python(file_path)
                if extract and (extract['classes'] or extract['functions']):
                    critical_extracts[str(file_path)] = extract
        
        if self.debug and critical_extracts:
            print(f"[Extractor] ✅ Extracted {len(critical_extracts)} critical files")
        
        # STEP 2: Extract from modules (files + dependencies)
        enhanced_modules = {}
        
        for module_key, module_data in modules.items():
            if not isinstance(module_data, dict):
                continue
            
            files = module_data.get('files', [])
            dependencies = module_data.get('dependencies', [])
            
            if not files and not dependencies:
                continue
            
            # Combine files + top dependencies
            all_candidates = list(files) + list(dependencies)[:5]  # Limit deps to 5
            
            # Prioritize important files (language-aware)
            def priority_score(file_path_str):
                """Score files by importance based on language patterns"""
                name_lower = file_path_str.lower()
                score = 0
                
                # CRITICAL files get max priority (from dynamic patterns)
                if self._is_critical_file(Path(file_path_str)):
                    score += 1000
                
                # Language-specific prioritization
                if 'python' in self.languages:
                    # Python: models, views, services, serializers
                    if any(p in name_lower for p in ['/models/', 'models.py']):
                        score += 100
                    elif any(p in name_lower for p in ['/views/', 'views.py']):
                        score += 70
                    elif any(p in name_lower for p in ['/serializers/', 'serializer']):
                        score += 80
                    elif any(p in name_lower for p in ['/services/', 'service']):
                        score += 60
                    elif name_lower.endswith('.py'):
                        score += 10
                
                if 'javascript' in self.languages or 'typescript' in self.languages:
                    # JS/TS: models, controllers, routes, components
                    if any(p in name_lower for p in ['/models/', '/schemas/']):
                        score += 100
                    elif any(p in name_lower for p in ['/controllers/', '/routes/']):
                        score += 70
                    elif any(p in name_lower for p in ['/services/', '/utils/']):
                        score += 60
                    elif any(p in name_lower for p in ['/components/', '/views/']):
                        score += 50
                    elif name_lower.endswith(('.ts', '.tsx', '.js', '.jsx')):
                        score += 10
                
                if 'go' in self.languages:
                    # Go: models, handlers, services
                    if any(p in name_lower for p in ['/models/', '/entities/']):
                        score += 100
                    elif any(p in name_lower for p in ['/handlers/', '/controllers/']):
                        score += 70
                    elif any(p in name_lower for p in ['/services/', '/repositories/']):
                        score += 60
                    elif name_lower.endswith('.go'):
                        score += 10
                
                if 'java' in self.languages:
                    # Java: entities, controllers, services
                    if any(p in name_lower for p in ['/models/', '/entities/', '/domain/']):
                        score += 100
                    elif any(p in name_lower for p in ['/controllers/', '/resources/']):
                        score += 70
                    elif any(p in name_lower for p in ['/services/', '/repositories/']):
                        score += 60
                    elif name_lower.endswith('.java'):
                        score += 10
                
                # Generic patterns (all languages)
                if any(p in name_lower for p in ['/core/', '/src/', '/app/']):
                    score += 40
                
                # De-prioritize tests (but don't exclude)
                if any(p in name_lower for p in ['test', 'spec', '__test__']):
                    score -= 20
                
                return score
            
            # Sort by priority
            sorted_candidates = sorted(all_candidates, key=priority_score, reverse=True)
            
            # Extract from top 15 files (increased from 10)
            key_files = sorted_candidates[:15]
            
            extracts = {}
            for file_path_str in key_files:
                file_path = Path(file_path_str)
                
                # Skip if already in critical extracts
                if str(file_path) in critical_extracts:
                    extracts[str(file_path)] = critical_extracts[str(file_path)]
                    continue
                
                if not file_path.exists():
                    continue
                
                if file_path.suffix == '.py':
                    extract = self.extract_python(file_path)
                    if extract and (extract['classes'] or extract['functions']):
                        extracts[str(file_path)] = extract
                
                elif file_path.suffix in ['.ts', '.tsx']:
                    extract = self.extract_typescript(file_path)
                    if extract and (extract['interfaces'] or extract['functions']):
                        extracts[str(file_path)] = extract
            
            # Add extracts to module
            if extracts:
                enhanced_module = module_data.copy()
                enhanced_module['code_extracts'] = extracts
                enhanced_modules[module_key] = enhanced_module
            else:
                enhanced_modules[module_key] = module_data
        
        # STEP 3: Diagnostic - report what we found
        if self.debug:
            total_extracts = sum(1 for m in enhanced_modules.values() 
                               if isinstance(m, dict) and 'code_extracts' in m)
            print(f"[Extractor] 📊 Final stats: {total_extracts}/{len(modules)} modules enriched")
            
            # Check if we got User model
            user_found = False
            for m in enhanced_modules.values():
                if isinstance(m, dict) and 'code_extracts' in m:
                    for file_path, extract in m['code_extracts'].items():
                        if 'user.py' in file_path.lower():
                            for cls in extract.get('classes', []):
                                if cls['name'] == 'User':
                                    user_found = True
                                    choices = cls.get('choices', {})
                                    print(f"[Extractor] ✅ User model extracted with {len(choices)} CHOICES sets")
            
            if not user_found:
                print(f"[Extractor] ⚠️  User model NOT extracted")
        
        return enhanced_modules


def extract_code_structures(repo_path: Path, modules: Dict[str, Any], debug: bool = False) -> Dict[str, Any]:
    """
    Convenience function to extract code structures for modules.
    
    Args:
        repo_path: Repository path
        modules: Module dict from scanner
        debug: Enable debug output
    
    Returns:
        Enhanced modules with code extracts
    """
    extractor = CodeExtractor(repo_path, debug=debug)
    return extractor.extract_for_modules(modules)

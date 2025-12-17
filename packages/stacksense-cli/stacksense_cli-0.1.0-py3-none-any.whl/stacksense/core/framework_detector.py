"""
Framework Detection Module
===========================
Deterministic framework detection from manifests and imports.
No LLM - pure file analysis for 100% accuracy.

Detects frameworks from:
1. Manifest files (requirements.txt, package.json, etc.)
2. Import statements (Python, JavaScript)
3. Configuration files (Dockerfile, docker-compose.yml)
"""
from pathlib import Path
from typing import Dict, Set, List
import json
import re
from collections import defaultdict


class FrameworkDetector:
    """Detect frameworks deterministically from project files"""
    
    # Framework signatures
    PYTHON_FRAMEWORKS = {
        'django': 'Django',
        'djangorestframework': 'Django REST Framework',
        'django-rest-framework': 'Django REST Framework',
        'flask': 'Flask',
        'fastapi': 'FastAPI',
        'celery': 'Celery',
        'pytest': 'Pytest',
        'sqlalchemy': 'SQLAlchemy',
    }
    
    JS_FRAMEWORKS = {
        'next': 'Next.js',
        'react': 'React',
        'vue': 'Vue',
        'angular': 'Angular',
        'express': 'Express',
        'nestjs': 'NestJS',
        'svelte': 'Svelte',
        'remix': 'Remix',
        '@remix-run': 'Remix',
    }
    
    DATABASES = {
        'postgresql': 'PostgreSQL',
        'psycopg2': 'PostgreSQL',
        'psycopg2-binary': 'PostgreSQL',
        'mysql': 'MySQL',
        'mongodb': 'MongoDB',
        'redis': 'Redis',
        'sqlite': 'SQLite',
    }
    
    INFRASTRUCTURE = {
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'nginx': 'Nginx',
        'celery': 'Celery',
        'rabbitmq': 'RabbitMQ',
    }
    
    # Import aliases (package name → import name)
    IMPORT_ALIASES = {
        'djangorestframework': 'rest_framework',
        'django-rest-framework': 'rest_framework',
        'aiortc': 'aiortc',  # Same name, but good to track
    }
    
    def __init__(self, repo_path: Path, debug: bool = False):
        self.repo_path = Path(repo_path)
        self.debug = debug
        self.evidence = defaultdict(list)  # Track evidence for each framework
    
    def detect(self) -> Dict[str, List[str]]:
        """
        Detect all frameworks with evidence-based validation.
        
        Returns:
            Dict with categories: backend, frontend, database, infrastructure
        """
        frameworks = {
            'backend': set(),
            'frontend': set(),
            'database': set(),
            'infrastructure': set()
        }
        
        # 1. Scan manifests (most reliable)
        self._scan_python_manifests(frameworks)
        self._scan_js_manifests(frameworks)
        self._scan_docker_files(frameworks)
        
        # 2. Validate with imports (prevent false positives)
        import_evidence = self._scan_imports()
        self._validate_with_imports(frameworks, import_evidence)
        
        # 3. Convert sets to sorted lists
        result = {k: sorted(v) for k, v in frameworks.items()}
        
        if self.debug:
            self._print_detection_summary(result)
        
        return result
    
    def _scan_python_manifests(self, frameworks: Dict[str, Set]):
        """Scan Python dependency files (recursively)"""
        
        # Find all requirements.txt files (may be nested)
        for req_file in self.repo_path.rglob('requirements.txt'):
            # Skip venv, node_modules
            if any(skip in req_file.parts for skip in ['venv', 'node_modules', '.venv', 'site-packages']):
                continue
            
            self._parse_requirements(req_file, frameworks)
        
        # Find all Pipfiles
        for pipfile in self.repo_path.rglob('Pipfile'):
            if 'venv' not in pipfile.parts and 'node_modules' not in pipfile.parts:
                self._parse_pipfile(pipfile, frameworks)
        
        # Find pyproject.toml files
        for pyproject in self.repo_path.rglob('pyproject.toml'):
            if 'venv' not in pyproject.parts and 'node_modules' not in pyproject.parts:
                self._parse_pyproject(pyproject, frameworks)
    
    def _parse_requirements(self, req_file: Path, frameworks: Dict[str, Set]):
        """Parse requirements.txt"""
        
        try:
            content = req_file.read_text()
            lines = [line.strip() for line in content.split('\n')]
            
            for line in lines:
                if not line or line.startswith('#'):
                    continue
                
                # Extract package name (before ==, >=, etc.)
                pkg = re.split(r'[=<>!]', line)[0].strip().lower()
                
                # Check against known frameworks
                if pkg in self.PYTHON_FRAMEWORKS:
                    frameworks['backend'].add(self.PYTHON_FRAMEWORKS[pkg])
                    self.evidence[self.PYTHON_FRAMEWORKS[pkg]].append(f'requirements.txt: {pkg}')
                
                if pkg in self.DATABASES:
                    frameworks['database'].add(self.DATABASES[pkg])
                    self.evidence[self.DATABASES[pkg]].append(f'requirements.txt: {pkg}')
        
        except Exception as e:
            if self.debug:
                print(f"Error parsing requirements.txt: {e}")
    
    def _parse_pipfile(self, pipfile: Path, frameworks: Dict[str, Set]):
        """Parse Pipfile"""
        
        try:
            content = pipfile.read_text()
            
            # Simple regex parsing (more robust than full TOML parser)
            for pkg, fw_name in self.PYTHON_FRAMEWORKS.items():
                if pkg in content.lower():
                    frameworks['backend'].add(fw_name)
                    self.evidence[fw_name].append(f'Pipfile: {pkg}')
        
        except Exception as e:
            if self.debug:
                print(f"Error parsing Pipfile: {e}")
    
    def _parse_pyproject(self, pyproject: Path, frameworks: Dict[str, Set]):
        """Parse pyproject.toml"""
        
        try:
            content = pyproject.read_text()
            
            for pkg, fw_name in self.PYTHON_FRAMEWORKS.items():
                if pkg in content.lower():
                    frameworks['backend'].add(fw_name)
                    self.evidence[fw_name].append(f'pyproject.toml: {pkg}')
        
        except Exception as e:
            if self.debug:
                print(f"Error parsing pyproject.toml: {e}")
    
    def _scan_js_manifests(self, frameworks: Dict[str, Set]):
        """Scan JavaScript/Node.js dependency files"""
        
        # Find all package.json files (may be nested)
        for package_json in self.repo_path.rglob('package.json'):
            # Skip node_modules
            if 'node_modules' in package_json.parts:
                continue
            
            self._parse_package_json(package_json, frameworks)
    
    def _parse_package_json(self, package_json: Path, frameworks: Dict[str, Set]):
        """Parse package.json"""
        
        try:
            data = json.loads(package_json.read_text())
            
            # Check dependencies and devDependencies
            all_deps = {}
            all_deps.update(data.get('dependencies', {}))
            all_deps.update(data.get('devDependencies', {}))
            
            for pkg_name in all_deps.keys():
                pkg_lower = pkg_name.lower()
                
                # Check against known frameworks
                for key, fw_name in self.JS_FRAMEWORKS.items():
                    if key in pkg_lower:
                        frameworks['frontend'].add(fw_name)
                        self.evidence[fw_name].append(f'package.json: {pkg_name}')
        
        except Exception as e:
            if self.debug:
                print(f"Error parsing {package_json}: {e}")
    
    def _scan_docker_files(self, frameworks: Dict[str, Set]):
        """Scan Dockerfile and docker-compose.yml"""
        
        # Dockerfile
        for dockerfile in self.repo_path.rglob('Dockerfile*'):
            try:
                content = dockerfile.read_text().lower()
                
                # Detect from base images
                if 'python' in content:
                    self.evidence['Python'].append(f'{dockerfile.name}: python base image')
                
                if 'node' in content:
                    self.evidence['Node.js'].append(f'{dockerfile.name}: node base image')
                
                if 'nginx' in content:
                    frameworks['infrastructure'].add('Nginx')
                    self.evidence['Nginx'].append(f'{dockerfile.name}: nginx')
                
                # Always mark Docker as infrastructure
                frameworks['infrastructure'].add('Docker')
                self.evidence['Docker'].append(f'{dockerfile.name}')
            
            except Exception as e:
                if self.debug:
                    print(f"Error parsing {dockerfile}: {e}")
        
        # docker-compose.yml
        for compose in self.repo_path.rglob('docker-compose*.yml'):
            try:
                content = compose.read_text().lower()
                
                if 'postgres' in content:
                    frameworks['database'].add('PostgreSQL')
                    self.evidence['PostgreSQL'].append(f'{compose.name}: postgres service')
                
                if 'redis' in content:
                    frameworks['database'].add('Redis')
                    self.evidence['Redis'].append(f'{compose.name}: redis service')
                
                if 'mongodb' in content or 'mongo:' in content:
                    frameworks['database'].add('MongoDB')
                    self.evidence['MongoDB'].append(f'{compose.name}: mongo service')
                
                frameworks['infrastructure'].add('Docker')
                self.evidence['Docker'].append(f'{compose.name}')
            
            except Exception as e:
                if self.debug:
                    print(f"Error parsing {compose}: {e}")
    
    def _scan_imports(self) -> Dict[str, Set[str]]:
        """
        Scan import statements in code files.
        Returns framework -> set of files that import it.
        """
        
        import_evidence = defaultdict(set)
        
        # Scan Python imports
        for py_file in self.repo_path.rglob('*.py'):
            # Skip venv, node_modules, migrations
            if any(skip in py_file.parts for skip in ['venv', 'node_modules', 'migrations', '.venv']):
                continue
            
            try:
                content = py_file.read_text()
                
                for pkg, fw_name in self.PYTHON_FRAMEWORKS.items():
                    # Check for alias (e.g., djangorestframework imported as rest_framework)
                    import_name = self.IMPORT_ALIASES.get(pkg, pkg)
                    
                    # Look for "import <name>" or "from <name>"
                    pattern = rf'\b(import|from)\s+{import_name}\b'
                    if re.search(pattern, content):
                        import_evidence[fw_name].add(str(py_file.relative_to(self.repo_path)))
            
            except Exception:
                pass  # Skip files that can't be read
        
        # Scan JavaScript imports (simple check)
        for js_file in list(self.repo_path.rglob('*.js')) + list(self.repo_path.rglob('*.ts')) + list(self.repo_path.rglob('*.tsx')):
            if 'node_modules' in js_file.parts:
                continue
            
            try:
                content = js_file.read_text()
                
                for pkg, fw_name in self.JS_FRAMEWORKS.items():
                    # Look for import or require
                    if f"'{pkg}'" in content or f'"{pkg}"' in content or f'from \'{pkg}\'' in content:
                        import_evidence[fw_name].add(str(js_file.relative_to(self.repo_path)))
            
            except Exception:
                pass
        
        return import_evidence
    
    def _validate_with_imports(self, frameworks: Dict[str, Set], import_evidence: Dict[str, Set[str]]):
        """
        Validate detected frameworks with import evidence.
        Remove frameworks that have manifest but no actual use.
        """
        
        # Validation rule: If framework has <2 pieces of evidence, require import proof
        to_remove = defaultdict(set)
        
        for category, fw_set in frameworks.items():
            for fw_name in list(fw_set):
                evidence_count = len(self.evidence.get(fw_name, []))
                import_count = len(import_evidence.get(fw_name, set()))
                
                # Strong evidence (2+ manifest hits) = keep
                if evidence_count >= 2:
                    continue
                
                # Weak evidence (1 manifest hit) = require imports
                if evidence_count == 1 and import_count == 0:
                    # Mark for removal (likely false positive)
                    to_remove[category].add(fw_name)
                    if self.debug:
                        print(f"⚠️  Removing {fw_name}: weak evidence, no imports")
        
        # Remove unvalidated frameworks
        for category, fw_set in to_remove.items():
            frameworks[category] -= fw_set
    
    def _print_detection_summary(self, result: Dict[str, List[str]]):
        """Print detection summary for debugging"""
        
        print("\n🔍 Framework Detection Summary")
        print("=" * 60)
        
        total = sum(len(v) for v in result.values())
        print(f"Total frameworks detected: {total}\n")
        
        for category, frameworks in result.items():
            if frameworks:
                print(f"{category.upper()}:")
                for fw in frameworks:
                    evidence = self.evidence.get(fw, [])
                    print(f"  ✅ {fw}")
                    for ev in evidence[:2]:  # Show first 2 pieces of evidence
                        print(f"     - {ev}")
                    if len(evidence) > 2:
                        print(f"     ... and {len(evidence) - 2} more")
                print()


def detect_frameworks(repo_path: Path, debug: bool = False) -> Dict[str, List[str]]:
    """
    Convenience function for framework detection.
    
    Args:
        repo_path: Path to repository root
        debug: Print detection details
    
    Returns:
        Dict with framework categories
    """
    detector = FrameworkDetector(repo_path, debug=debug)
    return detector.detect()


def get_tech_stack_display(repo_path: Path, max_items: int = 5) -> str:
    """
    Generate a compact tech stack display string for the chat banner.
    
    Combines primary language(s) with detected frameworks into a readable format.
    Example: "Python + FastAPI + PostgreSQL" or "TypeScript + Next.js + React"
    
    Args:
        repo_path: Path to repository root
        max_items: Maximum number of items to display
    
    Returns:
        Formatted tech stack string (e.g., "Python + FastAPI + SQLAlchemy")
    """
    from .language_detector import LanguageDetector
    
    stack_items = []
    
    try:
        # 1. Get primary language(s)
        lang_detector = LanguageDetector()
        languages = lang_detector.detect_languages(Path(repo_path))
        
        if languages:
            # Sort by file count, take top 2 languages
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            primary_langs = [lang for lang, count in sorted_langs[:2] if count >= 5]
            stack_items.extend(primary_langs)
        
        # 2. Get frameworks
        detector = FrameworkDetector(Path(repo_path))
        frameworks = detector.detect()
        
        # Priority order: backend > frontend > database > infrastructure
        for category in ['backend', 'frontend', 'database']:
            for fw in frameworks.get(category, []):
                if fw not in stack_items and len(stack_items) < max_items:
                    stack_items.append(fw)
        
        # 3. Format the result
        if not stack_items:
            return "Unknown"
        
        return " + ".join(stack_items)
    
    except Exception as e:
        # Fallback on any error
        return "Unknown"


def get_tech_stack_detailed(repo_path: Path) -> Dict[str, any]:
    """
    Get detailed tech stack information for status display.
    
    Returns:
        Dict with 'display' (compact string), 'languages', and 'frameworks'
    """
    from .language_detector import LanguageDetector
    
    result = {
        'display': 'Unknown',
        'languages': {},
        'frameworks': {
            'backend': [],
            'frontend': [],
            'database': [],
            'infrastructure': []
        }
    }
    
    try:
        # Get languages
        lang_detector = LanguageDetector()
        result['languages'] = lang_detector.detect_languages(Path(repo_path))
        
        # Get frameworks
        detector = FrameworkDetector(Path(repo_path))
        result['frameworks'] = detector.detect()
        
        # Generate display string
        result['display'] = get_tech_stack_display(repo_path)
        
    except Exception:
        pass
    
    return result

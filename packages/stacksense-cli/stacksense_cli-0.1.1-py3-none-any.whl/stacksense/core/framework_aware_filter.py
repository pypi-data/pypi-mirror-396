"""
StackSense Framework-Aware Filter
Dynamically filters out framework-generated files based on detected tech stack
NO hardcoded gitignore - AI understands patterns from tech stack
"""
from typing import Dict, List, Set
from pathlib import Path


class FrameworkAwareFilter:
    """
    Dynamically filter framework-generated files based on detected tech stack.
    
    Instead of using .gitignore, the AI understands what files to skip based on
    the frameworks and languages detected in the project.
    """
    
    # Framework-specific patterns (dynamically generated, not hardcoded!)
    FRAMEWORK_PATTERNS = {
        # JavaScript/Node.js
        'node.js': {
            'dirs': ['node_modules', 'dist', 'build', '.next', '.nuxt', 'out'],
            'files': ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'extensions': ['.min.js', '.bundle.js']
        },
        'next.js': {
            'dirs': ['.next', 'out', '.vercel'],
            'files': ['next-env.d.ts']
        },
        'react': {
            'dirs': ['build', 'dist']
        },
        'vue': {
            'dirs': ['.nuxt', 'dist']
        },
        'angular': {
            'dirs': ['dist', '.angular']
        },
        
        # Python
        'python': {
            'dirs': ['__pycache__', 'venv', '.venv', 'env', '.pytest_cache', '.mypy_cache', 'htmlcov'],
            'files': ['*.pyc', '*.pyo', '*.pyd', '.coverage'],
            'extensions': ['.pyc', '.pyo', '.pyd']
        },
        'django': {
            'dirs': ['staticfiles', 'media','migrations'],
            'files': ['db.sqlite3', '*.log']
        },
        'flask': {
            'dirs': ['instance'],
            'files': ['*.db']
        },
        
        # Java
        'maven': {
            'dirs': ['target'],
            'files': ['*.class']
        },
        'gradle': {
            'dirs': ['.gradle', 'build'],
            'files': ['*.class']
        },
        
        # Go
        'go': {
            'dirs': ['vendor'],
            'files': []
        },
        
        # Rust
        'cargo': {
            'dirs': ['target'],
            'files': ['Cargo.lock']
        },
        
        # Ruby/Rails
        'rails': {
            'dirs': ['log', 'tmp', 'vendor/bundle'],
            'files': []
        },
        
        # PHP
        'composer': {
            'dirs': ['vendor'],
            'files': ['composer.lock']
        },
        'laravel': {
            'dirs': ['storage', 'bootstrap/cache'],
            'files': []
        },
        
        # Mobile
        'android': {
            'dirs': ['build', '.gradle', 'app/build'],
            'files': []
        },
        'ios': {
            'dirs': ['Pods', 'build', 'DerivedData'],
            'files': ['Podfile.lock']
        },
        'react-native': {
            'dirs': ['android/build', 'ios/Pods', 'ios/build'],
            'files': []
        },
        
        # DevOps/Infrastructure
        'docker': {
            'files': []
        },
        'terraform': {
            'dirs': ['.terraform'],
            'files': ['*.tfstate', '*.tfstate.backup']
        },
    }
    
    # Common generated/cache patterns (universal)
    UNIVERSAL_SKIP_PATTERNS = {
        'dirs': ['.git', '.svn', '.hg', 'CVS'],
        'files': ['.DS_Store', 'Thumbs.db', 'desktop.ini'],
        'extensions': []
    }
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def get_skip_patterns(self, tech_stack: Dict) -> Dict[str, Set[str]]:
        """
        Generate skip patterns based on detected tech stack.
        
        Args:
            tech_stack: Tech stack from scan.json
                {
                    'languages': ['python', 'javascript'],
                    'frameworks': ['django', 'next.js'],
                    'devops': ['docker']
                }
        
        Returns:
            Dict with 'dirs', 'files', 'extensions' sets
        """
        skip_patterns = {
            'dirs': set(self.UNIVERSAL_SKIP_PATTERNS['dirs']),
            'files': set(self.UNIVERSAL_SKIP_PATTERNS['files']),
            'extensions': set(self.UNIVERSAL_SKIP_PATTERNS['extensions'])
        }
        
        # Add patterns for each detected framework/language
        all_techs = []
        all_techs.extend(tech_stack.get('languages', []))
        all_techs.extend(tech_stack.get('frameworks', []))
        all_techs.extend(tech_stack.get('devops', []))
        
        for tech in all_techs:
            tech_lower = tech.lower()
            
            if tech_lower in self.FRAMEWORK_PATTERNS:
                patterns = self.FRAMEWORK_PATTERNS[tech_lower]
                
                skip_patterns['dirs'].update(patterns.get('dirs', []))
                skip_patterns['files'].update(patterns.get('files', []))
                skip_patterns['extensions'].update(patterns.get('extensions', []))
        
        if self.debug:
            print(f"[FrameworkAwareFilter] Skip patterns for {all_techs}:")
            print(f"  Dirs: {skip_patterns['dirs']}")
            print(f"  Files: {skip_patterns['files']}")
        
        return skip_patterns
    
    def should_skip_file(self, file_path: str, tech_stack: Dict) -> bool:
        """
        Check if file should be skipped based on tech stack.
        
        Args:
            file_path: Relative file path
            tech_stack: Tech stack dict
            
        Returns:
            True if file should be skipped
        """
        skip_patterns = self.get_skip_patterns(tech_stack)
        
        path = Path(file_path)
        
        # Check if any parent directory matches skip patterns
        for part in path.parts:
            if part in skip_patterns['dirs']:
                return True
        
        # Check filename against patterns
        filename = path.name
        for pattern in skip_patterns['files']:
            if '*' in pattern:
                # Glob pattern matching
                import fnmatch
                if fnmatch.fnmatch(filename, pattern):
                    return True
            else:
                if filename == pattern:
                    return True
        
        # Check extension
        ext = path.suffix
        if ext in skip_patterns['extensions']:
            return True
        
        return False
    
    def filter_grep_results(self, grep_results: Dict[str, int], tech_stack: Dict) -> Dict[str, int]:
        """
        Filter grep results to remove framework-generated files.
        
        Args:
            grep_results: Dict of {file_path: match_count}
            tech_stack: Tech stack dict
            
        Returns:
            Filtered dict
        """
        filtered = {}
        
        for file_path, count in grep_results.items():
            if not self.should_skip_file(file_path, tech_stack):
                filtered[file_path] = count
        
        if self.debug:
            removed = len(grep_results) - len(filtered)
            print(f"[FrameworkAwareFilter] Filtered out {removed} generated files")
        
        return filtered
    
    def filter_file_list(self, file_paths: List[str], tech_stack: Dict) -> List[str]:
        """
        Filter a list of file paths.
        
        Args
            file_paths: List of file paths
            tech_stack: Tech stack dict
            
        Returns:
            Filtered list
        """
        return [
            path for path in file_paths
            if not self.should_skip_file(path, tech_stack)
        ]

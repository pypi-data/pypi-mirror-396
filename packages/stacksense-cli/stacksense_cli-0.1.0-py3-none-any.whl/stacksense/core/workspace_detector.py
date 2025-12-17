"""
StackSense Workspace Detector
Automatically detects workspace structure: single repo, polygon repos, or monorepo
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class TechStackSignature:
    """Tech stack signature from gitignore analysis"""
    languages: Set[str]
    frameworks: Set[str]
    patterns: Set[str]
    
    
@dataclass
class RepoInfo:
    """Information about a detected repository"""
    path: Path
    name: str
    git_root: Optional[Path]
    tech_signature: TechStackSignature
    is_monorepo: bool
    
    
@dataclass
class WorkspaceStructure:
    """Complete workspace structure"""
    workspace_path: Path
    workspace_name: str
    repos: List[RepoInfo]
    structure_type: str  # 'single_repo', 'polygon_repos', 'monorepo'


class WorkspaceDetector:
    """
    Detects workspace structure by analyzing:
    1. Git repositories
    2. Gitignore patterns (tech stack signatures)
    3. Multiple tech stacks in one repo (monorepo detection)
    """
    
    # Tech stack patterns to detect from gitignore
    TECH_PATTERNS = {
        # JavaScript/Node.js - only specific patterns
        'node_modules': ('javascript', 'node.js'),
        '.next': ('javascript', 'next.js'),
        '.nuxt': ('javascript', 'nuxt.js'),
        'package-lock.json': ('javascript', 'npm'),
        'yarn.lock': ('javascript', 'yarn'),
        
        # Python
        '__pycache__': ('python', 'python'),
        '*.pyc': ('python', 'python'),
        'venv': ('python', 'virtualenv'),
        '.venv': ('python', 'virtualenv'),
        'env': ('python', 'virtualenv'),
        '.pytest_cache': ('python', 'pytest'),
        '*.egg-info': ('python', 'build'),
        '.eggs': ('python', 'build'),
        
        # Django specific
        'staticfiles': ('python', 'django'),
        'db.sqlite3': ('python', 'django'),
        
        # Ruby/Rails
        'vendor/bundle': ('ruby', 'rails'),
        '.bundle': ('ruby', 'bundler'),
        
        # Java
        'target': ('java', 'maven'),
        '.gradle': ('java', 'gradle'),
        
        # Go
        # 'vendor': ('go', 'go'),  # Too generic
        
        # Rust
        'target/debug': ('rust', 'cargo'),
        'target/release': ('rust', 'cargo'),
        'Cargo.lock': ('rust', 'cargo'),
        
        # PHP
        # 'vendor': ('php', 'composer'),  # Too generic
        
        # Mobile
        'Pods': ('swift', 'cocoapods'),
        '.expo': ('javascript', 'expo'),
        'android/build': ('kotlin', 'android'),
        'ios/build': ('swift', 'ios'),
        
        # DevOps
        '.terraform': ('devops', 'terraform'),
        '.docker': ('devops', 'docker'),
    }
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        
    def detect_workspace_structure(self, workspace_path: Path) -> WorkspaceStructure:
        """
        Detect complete workspace structure.
        
        Args:
            workspace_path: Root path of workspace
            
        Returns:
            WorkspaceStructure with detected repos and type
        """
        workspace_path = Path(workspace_path).resolve()
        workspace_name = workspace_path.name
        
        if self.debug:
            print(f"[WorkspaceDetector] Analyzing workspace: {workspace_path}")
        
        # Find all git repositories
        git_repos = self._find_git_repos(workspace_path)
        
        if self.debug:
            print(f"[WorkspaceDetector] Found {len(git_repos)} git repo(s)")
        
        # Analyze each repository
        repos = []
        for git_root in git_repos:
            repo_info = self._analyze_repo(git_root, workspace_path)
            repos.append(repo_info)
            
        # Determine workspace type
        structure_type = self._determine_structure_type(repos, workspace_path)
        
        if self.debug:
            print(f"[WorkspaceDetector] Workspace type: {structure_type}")
        
        return WorkspaceStructure(
            workspace_path=workspace_path,
            workspace_name=workspace_name,
            repos=repos,
            structure_type=structure_type
        )
    
    def _find_git_repos(self, workspace_path: Path) -> List[Path]:
        """
        Find all .git directories in workspace.
        
        Args:
            workspace_path: Root path to search
            
        Returns:
            List of paths containing .git directories
        """
        git_repos = []
        
        for root, dirs, files in os.walk(workspace_path):
            # Skip common ignore directories for faster scanning
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '__pycache__', 'venv', '.venv', 'env',
                'build', 'dist', 'target', 'vendor', '.terraform'
            }]
            
            if '.git' in dirs:
                git_repos.append(Path(root))
                # Don't search inside this git repo for more git repos
                dirs[:] = []
        
        return git_repos
    
    def _analyze_repo(self, repo_path: Path, workspace_path: Path) -> RepoInfo:
        """
        Analyze a single repository.
        
        Args:
            repo_path: Path to repository root
            workspace_path: Workspace root path
            
        Returns:
            RepoInfo with detected information
        """
        repo_name = repo_path.name
        
        # Analyze gitignore
        gitignore_path = repo_path / '.gitignore'
        tech_signature = self._analyze_gitignore(gitignore_path)
        
        # Detect if monorepo
        is_monorepo = self._detect_monorepo(repo_path, tech_signature)
        
        return RepoInfo(
            path=repo_path,
            name=repo_name,
            git_root=repo_path,
            tech_signature=tech_signature,
            is_monorepo=is_monorepo
        )
    
    def _analyze_gitignore(self, gitignore_path: Path) -> TechStackSignature:
        """
        Extract tech stack signature from gitignore.
        
        Args:
            gitignore_path: Path to .gitignore file
            
        Returns:
            TechStackSignature with detected patterns
        """
        languages = set()
        frameworks = set()
        patterns = set()
        
        if not gitignore_path.exists():
            return TechStackSignature(languages, frameworks, patterns)
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for line in content.split('\n'):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                patterns.add(line)
                
                # Check against known patterns
                for pattern, (lang, framework) in self.TECH_PATTERNS.items():
                    if pattern in line:
                        languages.add(lang)
                        frameworks.add(framework)
        
        except Exception as e:
            if self.debug:
                print(f"[WorkspaceDetector] Error reading gitignore: {e}")
        
        return TechStackSignature(languages, frameworks, patterns)
    
    def _detect_monorepo(self, repo_path: Path, tech_signature: TechStackSignature) -> bool:
        """
        Detect if repository is a monorepo.
        
        A monorepo has:
        1. Multiple distinct tech stacks
        2. Multiple package.json/setup.py/pom.xml files in different directories
        3. Workspace configuration (lerna.json, nx.json, etc.)
        
        Args:
            repo_path: Repository path
            tech_signature: Tech stack signature
            
        Returns:
            True if monorepo detected
        """
        # Check 1: Multiple languages (strong indicator)
        if len(tech_signature.languages) >= 3:
            return True
        
        # Check 2: Look for workspace config files
        monorepo_indicators = [
            'lerna.json',          # JavaScript monorepo
            'nx.json',             # Nx monorepo
            'pnpm-workspace.yaml', # pnpm workspaces
            'workspace',           # Cargo workspaces (Rust)
            'BUILD',               # Bazel
            'WORKSPACE',           # Bazel
        ]
        
        for indicator in monorepo_indicators:
            if (repo_path / indicator).exists():
                return True
        
        # Check 3: Multiple package managers in subdirectories
        package_files = {
            'package.json': 'javascript',
            'setup.py': 'python',
            'Cargo.toml': 'rust',
            'go.mod': 'go',
            'pom.xml': 'java',
        }
        
        package_counts = defaultdict(int)
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common ignore dirs
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '__pycache__', 'venv', 'build', 'dist', 'target'
            }]
            
            for package_file in package_files:
                if package_file in files:
                    lang = package_files[package_file]
                    package_counts[lang] += 1
        
        # If multiple instances of same package manager, likely monorepo
        for lang, count in package_counts.items():
            if count > 1:
                return True
        
        return False
    
    def _determine_structure_type(self, repos: List[RepoInfo], workspace_path: Path) -> str:
        """
        Determine workspace structure type.
        
        Args:
            repos: List of detected repositories
            workspace_path: Workspace root path
            
        Returns:
            'single_repo', 'polygon_repos', or 'monorepo'
        """
        if not repos:
            # No git repos found - treat as single repo
            return 'single_repo'
        
        if len(repos) == 1:
            # Single git repo
            if repos[0].is_monorepo:
                return 'monorepo'
            else:
                return 'single_repo'
        
        # Multiple git repos - polygon workspace
        return 'polygon_repos'
    
    def get_repo_storage_path(self, repo_info: RepoInfo, base_path: Path) -> Path:
        """
        Get storage path for a repository.
        
        Args:
            repo_info: Repository information
            base_path: Base storage path (e.g., ~/.stacksense/)
            
        Returns:
            Path for repo storage
        """
        return base_path / repo_info.name

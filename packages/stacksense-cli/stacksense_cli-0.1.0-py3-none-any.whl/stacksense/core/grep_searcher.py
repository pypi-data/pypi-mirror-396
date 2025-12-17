"""
StackSense Grep Searcher
Multi-tool grep search with intelligent fallbacks: pss → ripgrep → pure Python
"""
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import threading


class GrepSearcher:
    """
    Fast grep-based keyword search with multiple tool fallbacks.
    
    Priority:
    1. pss (Perl-style search, very fast)
    2. ripgrep (rg, blazing fast)
    3. Pure Python (multi-threaded fallback)
    """
    
    def __init__(self, workspace_path: Path, file_index: Optional[Dict] = None, debug: bool = False):
        """
        Args:
            workspace_path: Root path to search
            file_index: Optional file index (limits search to tracked files)
            debug: Enable debug logging
        """
        self.workspace_path = workspace_path
        self.file_index = file_index
        self.debug = debug
        
        # Detect available tools
        self.has_pss = self._check_tool('pss')
        self.has_ripgrep = self._check_tool('rg')
        
        if self.debug:
            print(f"[GrepSearcher] Available tools: pss={self.has_pss}, rg={self.has_ripgrep}")
    
    def _check_tool(self, tool_name: str) -> bool:
        """Check if a command-line tool is available"""
        try:
            result = subprocess.run(
                [tool_name, '--version'],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def search_keywords(self, keywords: List[str]) -> Dict[str, int]:
        """
        Search for keywords and return files with match counts.
        
        Args:
            keywords: List of keywords to search
            
        Returns:
            Dict mapping file paths to total match count
        """
        all_matches = defaultdict(int)
        
        for keyword in keywords:
            keyword_matches = self.search_keyword(keyword)
            
            # Merge results
            for file_path, count in keyword_matches.items():
                all_matches[file_path] += count
        
        # Sort by match count (descending)
        sorted_matches = dict(
            sorted(all_matches.items(), key=lambda x: x[1], reverse=True)
        )
        
        if self.debug:
            print(f"[GrepSearcher] Found {len(sorted_matches)} files with matches")
        
        return sorted_matches
    
    def search_keyword(self, keyword: str) -> Dict[str, int]:
        """
        Search for a single keyword.
        
        Args:
            keyword: Keyword to search
            
        Returns:
            Dict mapping file paths to match count
        """
        # Try tools in order of preference
        if self.has_pss:
            result = self._search_with_pss(keyword)
            if result is not None:
                return result
        
        if self.has_ripgrep:
            result = self._search_with_ripgrep(keyword)
            if result is not None:
                return result
        
        # Fallback to pure Python
        return self._search_with_python(keyword)
    
    def _search_with_pss(self, keyword: str) -> Optional[Dict[str, int]]:
        """Search using pss"""
        try:
            # pss with count flag
            cmd = [
                'pss',
                '--nocolor',
                '--count',
                keyword,
                str(self.workspace_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode in [0, 1]:  # 1 means no matches
                return self._parse_count_output(result.stdout)
            
        except (subprocess.TimeoutExpired, Exception) as e:
            if self.debug:
                print(f"[GrepSearcher] pss error: {e}")
        
        return None
    
    def _search_with_ripgrep(self, keyword: str) -> Optional[Dict[str, int]]:
        """Search using ripgrep"""
        try:
            # ripgrep with count flag
            cmd = [
                'rg',
                '--count',
                '--no-heading',
                '--color=never',
                keyword,
                str(self.workspace_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode in [0, 1]:  # 1 means no matches
                return self._parse_count_output(result.stdout)
            
        except (subprocess.TimeoutExpired, Exception) as e:
            if self.debug:
                print(f"[GrepSearcher] ripgrep error: {e}")
        
        return None
    
    def _parse_count_output(self, output: str) -> Dict[str, int]:
        """
        Parse grep count output.
        Format: file:count or file.ext:count
        """
        matches = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Try to parse file:count
            parts = line.rsplit(':', 1)
            if len(parts) == 2:
                file_path, count_str = parts
                try:
                    count = int(count_str)
                    
                    # Make relative to workspace
                    if file_path.startswith(str(self.workspace_path)):
                        file_path = str(Path(file_path).relative_to(self.workspace_path))
                    
                    matches[file_path] = count
                except ValueError:
                    pass
        
        return matches
    
    def _search_with_python(self, keyword: str) -> Dict[str, int]:
        """
        Fast pure Python grep using multi-threading.
        Only searches files from file_index if available.
        """
        matches = {}
        lock = threading.Lock()
        
        # Get files to search
        if self.file_index:
            # Use tracked files only
            files_to_search = [
                self.workspace_path / file_path 
                for file_path in self.file_index.keys()
            ]
        else:
            # Walk directory
            files_to_search = []
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if d not in {
                    '.git', 'node_modules', '__pycache__', 'venv', '.venv',
                    'build', 'dist', 'target', '.next', 'vendor'
                }]
                
                for file in files:
                    file_path = Path(root) / file
                    files_to_search.append(file_path)
        
        # Search function for thread pool
        def search_file(file_path: Path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Count matches (case-insensitive)
                count = len(re.findall(re.escape(keyword), content, re.IGNORECASE))
                
                if count > 0:
                    # Get relative path
                    try:
                        rel_path = str(file_path.relative_to(self.workspace_path))
                    except ValueError:
                        rel_path = str(file_path)
                    
                    with lock:
                        matches[rel_path] = count
                        
            except Exception:
                pass  # Skip files that can't be read
        
        # Use thread pool for parallel search
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(search_file, files_to_search)
        
        if self.debug:
            print(f"[GrepSearcher] Python grep found {len(matches)} matches for '{keyword}'")
        
        return matches


import os  # Import at top if not already there

"""
StackSense Workspace Cache Manager
Persistent caching for repository analysis to avoid rescanning
"""
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class WorkspaceCache:
    """Manages persistent cache for workspace analysis"""
    
    def __init__(self, workspace_path: str, debug: bool = False):
        """
        Initialize cache manager.
        
        Args:
            workspace_path: Path to workspace root
            debug: Enable debug logging
        """
        self.workspace_path = Path(workspace_path)
        self.cache_dir = self.workspace_path / '.stacksense'
        self.cache_file = self.cache_dir / 'workspace_index.json'
        self.debug = debug
        
        # Cache settings
        self.max_age_hours = 1  # Cache expires after 1 hour
    
    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load cached workspace analysis.
        
        Returns:
            Cached data if valid, None if stale or missing
        """
        if not self.cache_file.exists():
            if self.debug:
                print("[Cache] No cache file found")
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            # Validate cache
            if self._is_stale(cache):
                if self.debug:
                    print("[Cache] Cache is stale, will rescan")
                return None
            
            if self.debug:
                print(f"[Cache] ✅ Loaded valid cache from {self.cache_file}")
            
            return cache.get('data')
        
        except Exception as e:
            if self.debug:
                print(f"[Cache] Failed to load cache: {e}")
            return None
    
    def save(self, data: Dict[str, Any]):
        """
        Save workspace analysis to cache.
        
        Args:
            data: Workspace analysis data to cache
        """
        try:
            # Create cache directory
            self.cache_dir.mkdir(exist_ok=True)
            
            # Build cache object
            cache = {
                'timestamp': datetime.now().isoformat(),
                'git_head': self._get_git_head(),
                'workspace': str(self.workspace_path),
                'data': data
            }
            
            # Write to file
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
            
            if self.debug:
                print(f"[Cache] ✅ Saved cache to {self.cache_file}")
        
        except Exception as e:
            if self.debug:
                print(f"[Cache] Failed to save cache: {e}")
    
    def invalidate(self):
        """Delete cache file to force rescan"""
        if self.cache_file.exists():
            self.cache_file.unlink()
            if self.debug:
                print("[Cache] Cache invalidated")
    
    def _is_stale(self, cache: Dict[str, Any]) -> bool:
        """
        Check if cache needs refresh.
        
        Args:
            cache: Cache object to validate
            
        Returns:
            True if cache is stale and needs refresh
        """
        # Check git HEAD changed (code changed)
        current_head = self._get_git_head()
        cached_head = cache.get('git_head')
        
        if current_head and cached_head and current_head != cached_head:
            if self.debug:
                print(f"[Cache] Git HEAD changed: {cached_head[:8]} → {current_head[:8]}")
            return True
        
        # Check age
        try:
            cached_time = datetime.fromisoformat(cache['timestamp'])
            age = datetime.now() - cached_time
            
            if age > timedelta(hours=self.max_age_hours):
                if self.debug:
                    print(f"[Cache] Cache too old: {age.total_seconds() / 3600:.1f}h")
                return True
        except (KeyError, ValueError):
            return True
        
        return False
    
    def _get_git_head(self) -> Optional[str]:
        """
        Get current git HEAD commit hash.
        
        Returns:
            Commit hash or None if not a git repo
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache info
        """
        if not self.cache_file.exists():
            return {'exists': False}
        
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            cached_time = datetime.fromisoformat(cache['timestamp'])
            age = datetime.now() - cached_time
            
            return {
                'exists': True,
                'timestamp': cache['timestamp'],
                'age_hours': age.total_seconds() / 3600,
                'git_head': cache.get('git_head', 'unknown')[:8],
                'is_stale': self._is_stale(cache),
                'size_kb': self.cache_file.stat().st_size / 1024
            }
        except Exception as e:
            return {'exists': True, 'error': str(e)}

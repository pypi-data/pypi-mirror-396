"""
Scan Cache - Persistent JSON Storage
=====================================
Saves repo scans for instant loading in future sessions.
Updates incrementally like VS Code auto-save.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class ScanCache:
    """
    Persistent cache for repo scans.
    Enables "AI remembers" UX without re-scanning.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir is None:
            cache_dir = Path.home() / '.commit-checker' / 'cache'
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.debug = False
    
    def get_cache_path(self, repo_path: str) -> Path:
        """
        Generate cache file path for repository.
        Uses hash for uniqueness, name for readability.
        """
        # Hash for uniqueness
        repo_hash = hashlib.md5(repo_path.encode()).hexdigest()[:12]
        
        # Name for readability
        repo_name = Path(repo_path).name
        
        return self.cache_dir / f"{repo_name}_{repo_hash}.json"
    
    def load(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """
        Load cache if exists and valid.
        Returns None if doesn't exist or invalid.
        """
        cache_path = self.get_cache_path(repo_path)
        
        if not cache_path.exists():
            if self.debug:
                print(f"[Cache] No cache found for {Path(repo_path).name}")
            return None
        
        try:
            cache = json.loads(cache_path.read_text())
            
            # Validate cache
            if self._is_valid(cache, repo_path):
                if self.debug:
                    age = datetime.now() - datetime.fromisoformat(cache['last_updated'])
                    print(f"[Cache] ✅ Loaded cache ({age.total_seconds() / 3600:.1f}h old)")
                return cache
            else:
                if self.debug:
                    print(f"[Cache] ⚠️  Cache invalid (repo changed or expired)")
                return None
        
        except Exception as e:
            if self.debug:
                print(f"[Cache] Error loading: {e}")
            return None
    
    def save(self, repo_path: str, data: Dict[str, Any], trigger: str = 'manual'):
        """
        Save cache with atomic write (VS Code style).
        
        Args:
            repo_path: Repository path
            data: Data to cache
            trigger: What triggered the save ('initial_scan', 'query', 'manual')
        """
        cache_path = self.get_cache_path(repo_path)
        
        # Add metadata
        cache_data = {
            **data,
            'repo_path': repo_path,
            'last_updated': datetime.now().isoformat(),
            'save_trigger': trigger,
            'cache_version': '2.0'
        }
        
        # Add git hash if available
        git_hash = self._get_git_hash(repo_path)
        if git_hash:
            cache_data['git_head'] = git_hash
        
        # Atomic write (temp file + rename)
        temp_path = cache_path.with_suffix('.tmp')
        
        try:
            temp_path.write_text(json.dumps(cache_data, indent=2))
            temp_path.replace(cache_path)  # Atomic on POSIX
            
            if self.debug:
                size_kb = cache_path.stat().st_size / 1024
                print(f"[Cache] 💾 Saved ({size_kb:.1f} KB, trigger: {trigger})")
        
        except Exception as e:
            if self.debug:
                print(f"[Cache] Error saving: {e}")
            if temp_path.exists():
                temp_path.unlink()
    
    def update_incremental(self, repo_path: str, updates: Dict[str, Any]):
        """
        Incremental update - merge new data with existing.
        Like VS Code auto-save on file changes.
        """
        # Load existing
        cache = self.load(repo_path)
        
        if cache is None:
            # No existing cache, save as new
            self.save(repo_path, updates, trigger='incremental_new')
            return
        
        # Merge updates
        if 'query_specific_extractions' in updates:
            # Add to discoveries
            if 'discoveries' not in cache:
                cache['discoveries'] = {}
            
            cache['discoveries'].update(updates['query_specific_extractions'])
        
        # Merge any other fields
        for key, value in updates.items():
            if key not in ['repo_path', 'last_updated', 'git_head']:
                cache[key] = value
        
        # Save
        self.save(repo_path, cache, trigger='incremental_update')
    
    def _is_valid(self, cache: Dict[str, Any], repo_path: str) -> bool:
        """
        Check if cache is still valid.
        Invalid if: (1) repo changed (git hash), (2) expired (>7 days)
        """
        # Check git hash (if repo has git)
        current_git_hash = self._get_git_hash(repo_path)
        if current_git_hash:
            cached_git_hash = cache.get('git_head')
            if cached_git_hash and current_git_hash != cached_git_hash:
                return False  # Repo changed!
        
        # Check expiry (7 days default)
        try:
            last_updated = datetime.fromisoformat(cache['last_updated'])
            age = datetime.now() - last_updated
            
            if age > timedelta(days=7):
                return False  # Too old!
        except:
            return False  # Invalid timestamp
        
        return True
    
    def _get_git_hash(self, repo_path: str) -> Optional[str]:
        """Get current git HEAD hash"""
        git_head_file = Path(repo_path) / '.git' / 'HEAD'
        
        if not git_head_file.exists():
            return None
        
        try:
            head_content = git_head_file.read_text().strip()
            
            # If HEAD is a ref, resolve it
            if head_content.startswith('ref:'):
                ref_path = head_content.split(' ')[1]
                ref_file = Path(repo_path) / '.git' / ref_path
                if ref_file.exists():
                    return ref_file.read_text().strip()
            
            return head_content
        except:
            return None
    
    def clear_cache(self, repo_path: str) -> bool:
        """Delete cache for repository"""
        cache_path = self.get_cache_path(repo_path)
        
        if cache_path.exists():
            cache_path.unlink()
            if self.debug:
                print(f"[Cache] 🗑️  Deleted cache for {Path(repo_path).name}")
            return True
        
        return False
    
    def list_caches(self) -> list:
        """List all cached repositories"""
        caches = []
        
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                cache = json.loads(cache_file.read_text())
                caches.append({
                    'name': Path(cache['repo_path']).name,
                    'path': cache['repo_path'],
                    'last_updated': cache['last_updated'],
                    'size_kb': cache_file.stat().st_size / 1024
                })
            except:
                pass
        
        return caches

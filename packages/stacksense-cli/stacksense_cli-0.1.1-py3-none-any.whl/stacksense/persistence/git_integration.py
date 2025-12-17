"""
Git Integration - Detect Repository Changes
============================================
Monitors git status to detect file changes and update structure.json incrementally.
"""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class GitIntegration:
    """
    Detects git changes to keep structure.json in sync with reality.
    Works without GitPython for simplicity.
    """
    
    def __init__(self, repo_path: Path, debug: bool = False):
        self.repo_path = Path(repo_path)
        self.debug = debug
        
        self.git_dir = self.repo_path / '.git'
        self.is_git_repo = self.git_dir.exists()
    
    def get_current_head(self) -> Optional[str]:
        """
        Get current git HEAD commit hash.
        Returns None if not a git repo.
        """
        if not self.is_git_repo:
            return None
        
        head_file = self.git_dir / 'HEAD'
        if not head_file.exists():
            return None
        
        try:
            head_content = head_file.read_text().strip()
            
            # If HEAD points to a ref, resolve it
            if head_content.startswith('ref:'):
                ref_path = head_content.split(' ')[1]
                ref_file = self.git_dir / ref_path
                
                if ref_file.exists():
                    return ref_file.read_text().strip()
            
            # Direct commit hash
            return head_content
        except Exception as e:
            if self.debug:
                print(f"[Git] Error reading HEAD: {e}")
            return None
    
    def detect_changes(self) -> Dict[str, List[str]]:
        """
        Detect git changes without GitPython.
        Returns dict with 'modified', 'added', 'deleted' file lists.
        
        NOTE: This is a simplified version. For production, consider GitPython.
        """
        if not self.is_git_repo:
            if self.debug:
                print("[Git] Not a git repository")
            return {'modified': [], 'added': [], 'deleted': []}
        
        # For now, return empty changes
        # TODO: Implement full git status parsing or use GitPython
        changes = {
            'modified': [],
            'added': [],
            'deleted': [],
            'last_check': datetime.now().isoformat()
        }
        
        if self.debug:
            print(f"[Git] Change detection: {len(changes['modified'])} modified, {len(changes['added'])} added, {len(changes['deleted'])} deleted")
        
        return changes
    
    def has_uncommitted_changes(self) -> bool:
        """
        Quick check if there are uncommitted changes.
        """
        changes = self.detect_changes()
        return bool(changes['modified'] or changes['added'] or changes['deleted'])

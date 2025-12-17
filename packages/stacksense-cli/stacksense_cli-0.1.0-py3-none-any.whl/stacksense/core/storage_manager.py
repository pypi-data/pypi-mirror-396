"""
StackSense Storage Manager
Manages ~/.stacksense/ folder structure and JSON file operations
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from threading import Lock


class StorageManager:
    """
    Manages StackSense storage at ~/.stacksense/
    
    Structure:
        ~/.stacksense/
            {workspace_name}/
                {repo_name}/
                    scan/
                        diagrams/
                            dependency_graph.json
                            dependency_graph.mermaid
                            dependency_graph.svg
                        scan.json
                        ai_memory.json
                        group.json
                    search/
                        search.json
                        relevance.json
                    todo/
                        todo.json
    """
    
    def __init__(self, debug: bool = False):
        self.base_path = Path.home() / '.stacksense'
        self.debug = debug
        self._locks = {}  # File-level locks for concurrent access
        
        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def get_workspace_path(self, workspace_name: str) -> Path:
        """Get path to workspace directory"""
        return self.base_path / workspace_name
    
    def get_repo_path(self, workspace_name: str, repo_name: str) -> Path:
        """Get path to repo directory"""
        return self.get_workspace_path(workspace_name) / repo_name
    
    def get_scan_path(self, workspace_name: str, repo_name: str) -> Path:
        """Get path to scan directory"""
        return self.get_repo_path(workspace_name, repo_name) / 'scan'
    
    def get_search_path(self, workspace_name: str, repo_name: str) -> Path:
        """Get path to search directory"""
        return self.get_repo_path(workspace_name, repo_name) / 'search'
    
    def get_todo_path(self, workspace_name: str, repo_name: str) -> Path:
        """Get path to todo directory"""
        return self.get_repo_path(workspace_name, repo_name) / 'todo'
    
    def get_diagrams_path(self, workspace_name: str, repo_name: str) -> Path:
        """Get path to diagrams directory"""
        return self.get_scan_path(workspace_name, repo_name) / 'diagrams'
    
    def initialize_repo_structure(self, workspace_name: str, repo_name: str):
        """
        Initialize complete folder structure for a repository.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
        """
        repo_path = self.get_repo_path(workspace_name, repo_name)
        
        if self.debug:
            print(f"[StorageManager] Initializing: {repo_path}")
        
        # Create all directories
        scan_path = self.get_scan_path(workspace_name, repo_name)
        search_path = self.get_search_path(workspace_name, repo_name)
        todo_path = self.get_todo_path(workspace_name, repo_name)
        diagrams_path = self.get_diagrams_path(workspace_name, repo_name)
        
        for path in [scan_path, search_path, todo_path, diagrams_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize JSON files with default structures
        self._ensure_json_file(scan_path / 'scan.json', self._default_scan_json())
        self._ensure_json_file(scan_path / 'ai_memory.json', self._default_ai_memory_json())
        self._ensure_json_file(scan_path / 'group.json', self._default_group_json())
        self._ensure_json_file(search_path / 'search.json', self._default_search_json())
        self._ensure_json_file(search_path / 'relevance.json', self._default_relevance_json())
        self._ensure_json_file(todo_path / 'todo.json', self._default_todo_json())
    
    def _ensure_json_file(self, file_path: Path, default_content: Dict):
        """Create JSON file if it doesn't exist"""
        if not file_path.exists():
            self.write_json(file_path, default_content)
    
    def _default_scan_json(self) -> Dict:
        """Default scan.json structure"""
        return {
            "scan_version": "1.0",
            "last_updated": self._timestamp(),
            "tech_stack": {
                "languages": [],
                "frameworks": [],
                "databases": [],
                "devops": []
            },
            "structure_type": "unknown",
            "entry_points": []
        }
    
    def _default_ai_memory_json(self) -> Dict:
        """Default ai_memory.json structure"""
        return {
            "memory_version": "1.0",
            "last_updated": self._timestamp(),
            "learnings": {}
        }
    
    def _default_group_json(self) -> Dict:
        """Default group.json structure"""
        return {
            "groups": {}
        }
    
    def _default_search_json(self) -> Dict:
        """Default search.json structure"""
        return {
            "searches": []
        }
    
    def _default_relevance_json(self) -> Dict:
        """Default relevance.json structure"""
        return {
            "project_context": {},
            "relevant_topics": {}
        }
    
    def _default_todo_json(self) -> Dict:
        """Default todo.json structure"""
        return {
            "tasks": []
        }
    
    def _timestamp(self) -> str:
        """Get current ISO timestamp"""
        return datetime.utcnow().isoformat() + 'Z'
    
    def _get_lock(self, file_path: Path) -> Lock:
        """Get or create lock for file"""
        file_key = str(file_path)
        if file_key not in self._locks:
            self._locks[file_key] = Lock()
        return self._locks[file_key]
    
    def read_json(self, file_path: Path) -> Optional[Dict]:
        """
        Read JSON file with thread safety.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary content or None if not exists/error
        """
        if not file_path.exists():
            return None
        
        lock = self._get_lock(file_path)
        
        with lock:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                if self.debug:
                    print(f"[StorageManager] Error reading {file_path}: {e}")
                return None
    
    def write_json(self, file_path: Path, data: Dict, backup: bool = True):
        """
        Write JSON file with atomic updates and optional backup.
        
        Args:
            file_path: Path to JSON file
            data: Dictionary to write
            backup: Create backup before writing
        """
        lock = self._get_lock(file_path)
        
        with lock:
            # Create backup if file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix('.json.bak')
                shutil.copy2(file_path, backup_path)
            
            # Write to temp file first (atomic write)
            temp_path = file_path.with_suffix('.json.tmp')
            
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Atomic rename
                temp_path.replace(file_path)
                
                if self.debug:
                    print(f"[StorageManager] Wrote: {file_path}")
                    
            except Exception as e:
                if self.debug:
                    print(f"[StorageManager] Error writing {file_path}: {e}")
                
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
                
                raise
    
    def update_json(self, file_path: Path, updates: Dict, merge: bool = True):
        """
        Update JSON file with new data.
        
        Args:
            file_path: Path to JSON file
            updates: Dictionary with updates
            merge: If True, merge with existing; if False, replace
        """
        if merge:
            existing = self.read_json(file_path) or {}
            data = self._deep_merge(existing, updates)
        else:
            data = updates
        
        self.write_json(file_path, data)
    
    def _deep_merge(self, base: Dict, updates: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    # Convenience methods for specific files
    
    def read_scan_json(self, workspace_name: str, repo_name: str) -> Dict:
        """Read scan.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'scan.json'
        return self.read_json(path) or self._default_scan_json()
    
    def write_scan_json(self, workspace_name: str, repo_name: str, data: Dict):
        """Write scan.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'scan.json'
        data['last_updated'] = self._timestamp()
        self.write_json(path, data)
    
    def update_scan_json(self, workspace_name: str, repo_name: str, updates: Dict):
        """Update scan.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'scan.json'
        updates['last_updated'] = self._timestamp()
        self.update_json(path, updates, merge=True)
    
    def read_ai_memory_json(self, workspace_name: str, repo_name: str) -> Dict:
        """Read ai_memory.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'ai_memory.json'
        return self.read_json(path) or self._default_ai_memory_json()
    
    def write_ai_memory_json(self, workspace_name: str, repo_name: str, data: Dict):
        """Write ai_memory.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'ai_memory.json'
        data['last_updated'] = self._timestamp()
        self.write_json(path, data)
    
    def update_ai_memory_json(self, workspace_name: str, repo_name: str, updates: Dict):
        """Update ai_memory.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'ai_memory.json'
        updates['last_updated'] = self._timestamp()
        self.update_json(path, updates, merge=True)
    
    def read_group_json(self, workspace_name: str, repo_name: str) -> Dict:
        """Read group.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'group.json'
        return self.read_json(path) or self._default_group_json()
    
    def write_group_json(self, workspace_name: str, repo_name: str, data: Dict):
        """Write group.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'group.json'
        self.write_json(path, data)
    
    def update_group_json(self, workspace_name: str, repo_name: str, updates: Dict):
        """Update group.json for a repo"""
        path = self.get_scan_path(workspace_name, repo_name) / 'group.json'
        self.update_json(path, updates, merge=True)
    
    def read_todo_json(self, workspace_name: str, repo_name: str) -> Dict:
        """Read todo.json for a repo"""
        path = self.get_todo_path(workspace_name, repo_name) / 'todo.json'
        return self.read_json(path) or self._default_todo_json()
    
    def write_todo_json(self, workspace_name: str, repo_name: str, data: Dict):
        """Write todo.json for a repo"""
        path = self.get_todo_path(workspace_name, repo_name) / 'todo.json'
        self.write_json(path, data)
    
    def add_todo_task(self, workspace_name: str, repo_name: str, task: Dict):
        """Add a task to todo.json"""
        todo_data = self.read_todo_json(workspace_name, repo_name)
        
        # Generate ID if not provided
        if 'id' not in task:
            existing_ids = [t.get('id', 0) for t in todo_data['tasks']]
            task['id'] = str(max([int(id) for id in existing_ids if isinstance(id, (int, str))], default=0) + 1)
        
        # Add timestamp if not provided
        if 'created' not in task:
            task['created'] = self._timestamp()
        
        todo_data['tasks'].append(task)
        self.write_todo_json(workspace_name, repo_name, todo_data)
    
    def cleanup_old_backups(self, max_age_days: int = 7):
        """Remove backup files older than specified days"""
        import time
        
        max_age_seconds = max_age_days * 24 * 60 * 60
        current_time = time.time()
        
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.json.bak'):
                    file_path = Path(root) / file
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        if self.debug:
                            print(f"[StorageManager] Removed old backup: {file_path}")

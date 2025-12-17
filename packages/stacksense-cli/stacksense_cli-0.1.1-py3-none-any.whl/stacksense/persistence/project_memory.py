"""
Project Memory - The Living Brain
==================================
3-JSON system at project root that grows with developer's work.

Structure:
/project-root/
└── ai_memory/
    └── main/
        ├── repo/
        │   ├── repo_map.json      (Static: languages, frameworks, file index)
        │   ├── query_map.json     (Learning: which files do what)
        │   └── structure.json     (Live: current filesystem state)
        └── web/
            ├── searches.json      (Cached web queries)
            └── summaries.json     (Condensed insights)
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List


class ProjectMemory:
    """
    The living brain of the project.
    Creates and manages ai_memory/ at project root.
    """
    
    def __init__(self, repo_path: Path, debug: bool = False):
        self.repo_path = Path(repo_path)
        self.debug = debug
        
        # Memory location at ~/.commit-checker/ai_memory/{workspace_name}/
        workspace_name = self.repo_path.name
        user_home = Path.home()
        
        self.memory_root = user_home / '.commit-checker' / 'ai_memory' / workspace_name
        self.repo_memory = self.memory_root / 'main' / 'repo'
        self.web_memory = self.memory_root / 'main' / 'web'
        
        # JSON file paths
        self.repo_map_path = self.repo_memory / 'repo_map.json'
        self.query_map_path = self.repo_memory / 'query_map.json'
        self.structure_path = self.repo_memory / 'structure.json'
        
        self.web_searches_path = self.web_memory / 'searches.json'
        self.web_summaries_path = self.web_memory / 'summaries.json'
    
    def initialize(self) -> bool:
        """
        Create ai_memory/ folder at ~/.commit-checker/ai_memory/{workspace}/
        Returns True if newly created, False if already exists.
        """
        if self.memory_root.exists():
            if self.debug:
                print(f"[Memory] ✅ Found existing memory at {self.memory_root}")
            return False
        
        # Create directory structure
        self.repo_memory.mkdir(parents=True, exist_ok=True)
        self.web_memory.mkdir(parents=True, exist_ok=True)
        
        # Create empty JSONs
        self._init_repo_map()
        self._init_query_map()
        self._init_structure()
        
        # Inform user
        print("\n" + "=" * 80)
        print("🎉 Created AI memory at:")
        print(f"   {self.memory_root}")
        print("\n   This stores learned knowledge about your project.")
        print("   It grows as you chat and adapts to code changes.")
        print("   Located outside your workspace to keep it clean.")
        print("=" * 80 + "\n")
        
        return True
    
    def _init_repo_map(self):
        """Initialize empty repo_map.json"""
        repo_map = {
            "scan_version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "languages": [],
            "frameworks": [],
            "file_index": {},
            "structure_patterns": {},
            "entry_points": [],
            "readme_summary": ""
        }
        
        self.repo_map_path.write_text(json.dumps(repo_map, indent=2))
    
    def _init_query_map(self):
        """Initialize empty query_map.json"""
        query_map = {
            "categories": {},
            "file_purpose_map": {}
        }
        
        self.query_map_path.write_text(json.dumps(query_map, indent=2))
    
    def _init_structure(self):
        """Initialize empty structure.json"""
        structure = {
            "folders": {},
            "cross_links": {},
            "changes_detected": {
                "last_git_pull": None,
                "files_added": [],
                "files_removed": [],
                "files_modified": []
            }
        }
        
        self.structure_path.write_text(json.dumps(structure, indent=2))
    
    # ========== REPO MAP (Static Scan) ==========
    
    def load_repo_map(self) -> Dict[str, Any]:
        """Load repo_map.json (static scan)"""
        if not self.repo_map_path.exists():
            return {}
        
        return json.loads(self.repo_map_path.read_text())
    
    def save_repo_map(self, data: Dict[str, Any]):
        """Save repo_map.json (rarely changes)"""
        data['timestamp'] = datetime.now().isoformat()
        
        self.repo_map_path.write_text(json.dumps(data, indent=2))
        
        if self.debug:
            size_kb = self.repo_map_path.stat().st_size / 1024
            print(f"[Memory] 💾 Saved repo_map.json ({size_kb:.1f} KB)")
    
    # ========== QUERY MAP (Learning from Chats) ==========
    
    def load_query_map(self) -> Dict[str, Any]:
        """Load query_map.json (learned categories)"""
        if not self.query_map_path.exists():
            return {"categories": {}, "file_purpose_map": {}}
        
        return json.loads(self.query_map_path.read_text())
    
    def update_query_map(self, category: str, data: Dict[str, Any]):
        """
        Update query_map.json with new learning.
        This is called after each query refinement.
        """
        query_map = self.load_query_map()
        
        # Update or create category
        if category not in query_map['categories']:
            query_map['categories'][category] = {
                'files': [],
                'role': '',
                'functions': {},
                'last_updated': datetime.now().isoformat()
            }
        
        # Merge data
        query_map['categories'][category].update(data)
        query_map['categories'][category]['last_updated'] = datetime.now().isoformat()
        
        # Update file purpose map
        for file in data.get('files', []):
            query_map['file_purpose_map'][file] = category
        
        # Save
        self.query_map_path.write_text(json.dumps(query_map, indent=2))
        
        if self.debug:
            print(f"[Memory] 📝 Updated query_map.json - category: {category}")
    
    # ========== STRUCTURE (Live State) ==========
    
    def load_structure(self) -> Dict[str, Any]:
        """Load structure.json (current filesystem state)"""
        if not self.structure_path.exists():
            return {"folders": {}, "cross_links": {}}
        
        return json.loads(self.structure_path.read_text())
    
    def save_structure(self, data: Dict[str, Any]):
        """Save structure.json"""
        self.structure_path.write_text(json.dumps(data, indent=2))
        
        if self.debug:
            print(f"[Memory] 💾 Saved structure.json")
    
    def update_structure_incremental(self, changes: Dict[str, List[str]]):
        """
        Update structure.json based on git changes.
        Only updates affected folders.
        """
        structure = self.load_structure()
        
        # Record changes
        structure['changes_detected'] = {
            'last_git_pull': datetime.now().isoformat(),
            'files_added': changes.get('added', []),
            'files_removed': changes.get('removed', []),
            'files_modified': changes.get('modified', [])
        }
        
        # Update folders (if we have folder data)
        # This will be populated by structure analysis
        
        self.save_structure(structure)
    
    # ========== WEB SEARCH CACHE ==========
    
    def load_web_searches(self) -> List[Dict[str, Any]]:
        """Load cached web searches"""
        if not self.web_searches_path.exists():
            return []
        
        data = json.loads(self.web_searches_path.read_text())
        return data.get('searches', [])
    
    def add_web_search(self, query: str, results: List[Dict[str, Any]]):
        """
        Add web search to cache.
        Keeps last 50 searches (FIFO pruning).
        """
        searches = self.load_web_searches()
        
        # Add new search
        searches.append({
            'query': query,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
        # Prune to last 50
        if len(searches) > 50:
            searches = searches[-50:]
        
        # Save
        self.web_searches_path.write_text(json.dumps({'searches': searches}, indent=2))
    
    def find_cached_search(self, query: str, max_age_days: int = 7) -> Optional[List[Dict[str, Any]]]:
        """
        Find cached web search if:
        - Query matches >80% similarity
        - Less than max_age_days old
        """
        searches = self.load_web_searches()
        
        query_lower = query.lower()
        
        for search in reversed(searches):  # Check newest first
            # Simple similarity: check if >80% words match
            cached_query = search['query'].lower()
            
            query_words = set(query_lower.split())
            cached_words = set(cached_query.split())
            
            if len(query_words) == 0:
                continue
            
            overlap = len(query_words & cached_words)
            similarity = overlap / len(query_words)
            
            if similarity > 0.8:
                # Check age
                timestamp = datetime.fromisoformat(search['timestamp'])
                age = datetime.now() - timestamp
                
                if age < timedelta(days=max_age_days):
                    if self.debug:
                        print(f"[Memory] ♻️  Found cached search ({similarity:.0%} match, {age.days}d old)")
                    return search['results']
        
        return None
    
    # ========== UTILITIES ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics for display"""
        repo_map = self.load_repo_map()
        query_map = self.load_query_map()
        structure = self.load_structure()
        
        return {
            'location': str(self.memory_root),
            'languages': repo_map.get('languages', []),
            'frameworks': repo_map.get('frameworks', []),
            'files_indexed': len(repo_map.get('file_index', {})),
            'categories_learned': len(query_map.get('categories', {})),
            'folders_tracked': len(structure.get('folders', {})),
            'last_updated': repo_map.get('timestamp', 'never')
        }
    
    def clear(self):
        """Delete ai_memory/ folder entirely"""
        import shutil
        
        if self.memory_root.exists():
            shutil.rmtree(self.memory_root)
            
            if self.debug:
                print(f"[Memory] 🗑️  Deleted ai_memory/")

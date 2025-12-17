"""
StackSense Memory Writer Agent
Fast typing agent that writes AI learnings to memory files
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class MemoryWriterAgent:
    """
    Agent that writes AI's learnings to memory files.
    
    Handles:
    - ai_memory.json updates (what AI learned)
    - group.json updates (file groupings)
    - todo.json updates (tasks)
    - scan.json updates (tech stack changes)
    """
    
    def __init__(self, storage_manager, debug: bool = False):
        """
        Args:
            storage_manager: StorageManager instance
            debug: Enable debug logging
        """
        self.storage = storage_manager
        self.debug = debug
    
    def write_ai_learning(
        self,
        workspace_name: str,
        repo_name: str,
        topic: str,
        learning_data: Dict[str, Any]
    ):
        """
        Write AI's learning to ai_memory.json.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            topic: Topic/category (e.g., 'authentication', 'payment')
            learning_data: Dict with learning details
                {
                    'files': List[str],
                    'summary': str,
                    'key_functions': List[str],
                    'implementation': str,
                    'notes': str,
                    ...
                }
        """
        # Read current memory
        memory = self.storage.read_ai_memory_json(workspace_name, repo_name)
        
        # Add timestamp
        learning_data['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        
        # Check if topic exists
        if topic in memory['learnings']:
            # Update existing entry
            existing = memory['learnings'][topic]
            
            # Add change_log if content changed significantly
            if 'summary' in learning_data and learning_data['summary'] != existing.get('summary'):
                if 'change_log' not in existing:
                    existing['change_log'] = []
                
                existing['change_log'].append({
                    'timestamp': learning_data['last_updated'],
                    'previous_summary': existing.get('summary', ''),
                    'new_summary': learning_data['summary']
                })
            
            # Merge with existing
            existing.update(learning_data)
            memory['learnings'][topic] = existing
        else:
            # New entry
            memory['learnings'][topic] = learning_data
        
        # Write back
        self.storage.write_ai_memory_json(workspace_name, repo_name, memory)
        
        if self.debug:
            print(f"[MemoryWriter] Updated AI memory: {topic}")
    
    def write_file_grouping(
        self,
        workspace_name: str,
        repo_name: str,
        group_name: str,
        files: List[str],
        description: str = ""
    ):
        """
        Write file grouping to group.json.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            group_name: Group name (e.g., 'authentication_files')
            files: List of file paths in this group
            description: Optional description
        """
        # Read current groups
        groups_data = self.storage.read_group_json(workspace_name, repo_name)
        
        # Add or update group
        groups_data['groups'][group_name] = {
            'files': files,
            'description': description,
            'last_updated': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Write back
        self.storage.write_group_json(workspace_name, repo_name, groups_data)
        
        if self.debug:
            print(f"[MemoryWriter] Updated group: {group_name} ({len(files)} files)")
    
    def add_todo_task(
        self,
        workspace_name: str,
        repo_name: str,
        description: str,
        priority: str = 'medium',
        metadata: Optional[Dict] = None
    ):
        """
        Add task to todo.json.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            description: Task description
            priority: 'low', 'medium', or 'high'
            metadata: Optional metadata dict
        """
        task = {
            'description': description,
            'status': 'pending',
            'priority': priority,
            'created': datetime.utcnow().isoformat() + 'Z'
        }
        
        if metadata:
            task['metadata'] = metadata
        
        self.storage.add_todo_task(workspace_name, repo_name, task)
        
        if self.debug:
            print(f"[MemoryWriter] Added TODO: {description}")
    
    def complete_todo_task(
        self,
        workspace_name: str,
        repo_name: str,
        task_id: str
    ):
        """
        Mark a todo task as completed.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            task_id: Task ID to complete
        """
        todo_data = self.storage.read_todo_json(workspace_name, repo_name)
        
        for task in todo_data['tasks']:
            if task.get('id') == task_id:
                task['status'] = 'completed'
                task['completed'] = datetime.utcnow().isoformat() + 'Z'
                break
        
        self.storage.write_todo_json(workspace_name, repo_name, todo_data)
        
        if self.debug:
            print(f"[MemoryWriter] Completed task: {task_id}")
    
    def update_tech_stack(
        self,
        workspace_name: str,
        repo_name: str,
        tech_stack_updates: Dict[str, Any]
    ):
        """
        Update tech stack in scan.json.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            tech_stack_updates: Dict with updates
                {
                    'languages': [...],
                    'frameworks': [...],
                    'databases': [...],
                    'devops': [...]
                }
        """
        self.storage.update_scan_json(workspace_name, repo_name, {
            'tech_stack': tech_stack_updates
        })
        
        if self.debug:
            print(f"[MemoryWriter] Updated tech stack")
    
    def record_search_result(
        self,
        workspace_name: str,
        repo_name: str,
        query: str,
        results: List[Dict],
        used_for: str = ""
    ):
        """
        Record web search results in search.json.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            query: Search query
            results: List of search results
            used_for: What this search was used for
        """
        search_path = self.storage.get_search_path(workspace_name, repo_name)
        search_file = search_path / 'search.json'
        
        search_data = self.storage.read_json(search_file) or {'searches': []}
        
        search_entry = {
            'query': query,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'results': results,
            'used_for': used_for
        }
        
        search_data['searches'].append(search_entry)
        
        # Keep only last 20 searches
        search_data['searches'] = search_data['searches'][-20:]
        
        self.storage.write_json(search_file, search_data)
        
        if self.debug:
            print(f"[MemoryWriter] Recorded search: {query}")
    
    def update_relevance(
        self,
        workspace_name: str,
        repo_name: str,
        topic: str,
        relevance_data: Dict[str, Any]
    ):
        """
        Update relevance.json with filtered search knowledge.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            topic: Topic name
            relevance_data: Dict with relevance info
                {
                    'docs_saved': List[str],
                    'key_learnings': str,
                    'relevance_score': float
                }
        """
        relevance_path = self.storage.get_search_path(workspace_name, repo_name)
        relevance_file = relevance_path / 'relevance.json'
        
        relevance_json = self.storage.read_json(relevance_file) or {
            'project_context': {},
            'relevant_topics': {}
        }
        
        relevance_json['relevant_topics'][topic] = relevance_data
        
        self.storage.write_json(relevance_file, relevance_json)
        
        if self.debug:
            print(f"[MemoryWriter] Updated relevance: {topic}")
    
    def batch_write_from_ai_response(
        self,
        workspace_name: str,
        repo_name: str,
        ai_thoughts: Dict[str, Any]
    ):
        """
        Batch write from AI's consolidated thoughts.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            ai_thoughts: AI's thoughts dict
                {
                    'learnings': [...],
                    'groups': [...],
                    'todos': [...]
                }
        """
        # Write learnings
        for learning in ai_thoughts.get('learnings', []):
            self.write_ai_learning(
                workspace_name,
                repo_name,
                learning['topic'],
                learning['data']
            )
        
        # Write groups
        for group in ai_thoughts.get('groups', []):
            self.write_file_grouping(
                workspace_name,
                repo_name,
                group['name'],
                group['files'],
                group.get('description', '')
            )
        
        # Write todos
        for todo in ai_thoughts.get('todos', []):
            self.add_todo_task(
                workspace_name,
                repo_name,
                todo['description'],
                todo.get('priority', 'medium')
            )
        
        if self.debug:
            print(f"[MemoryWriter] Batch write complete")
    
    def update_from_query(
        self,
        workspace_name: str,
        repo_name: str,
        query: str,
        answer: str,
        files_used: List[str],
        keywords: List[str] = None
    ):
        """
        Learn from a query interaction.
        Called after every AI response to build persistent memory.
        
        IMPORTANT: Only saves if files_used is non-empty (code queries).
        General queries like "who are you?" are NOT saved.
        
        Args:
            workspace_name: Workspace name
            repo_name: Repository name
            query: User's question
            answer: AI's response
            files_used: Files that were analyzed
            keywords: Keywords extracted from query
        """
        import re
        
        # SKIP GENERAL QUERIES - only learn from code-related queries
        if not files_used:
            if self.debug:
                print(f"[MemoryWriter] Skipping general query (no files used)")
            return
        
        # Categorize the query into a topic
        topic = self._categorize_topic(query)
        
        # Extract ACTUAL learnings from the interaction
        learnings = self._extract_code_learnings(query, answer, files_used)
        
        # Build learning data - focused on CODE INSIGHTS, not Q&A summary
        learning_data = {
            'query_type': topic,
            'files_analyzed': files_used,
            'keywords': keywords or [],
            # Code insights instead of just summarized Q&A
            'learnings': learnings,
            'file_count': len(files_used),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Write the learning
        self.write_ai_learning(workspace_name, repo_name, topic, learning_data)
        
        # Also group the files together if multiple
        if len(files_used) > 1:
            group_name = f"{topic}_files"
            self.write_file_grouping(
                workspace_name, repo_name, 
                group_name, files_used,
                f"Files related to {topic}"
            )
        
        if self.debug:
            print(f"[MemoryWriter] Learned {len(learnings)} insights about: {topic}")
    
    def _categorize_topic(self, query: str) -> str:
        """
        Categorize a query into a topic name.
        Uses keyword matching to determine the main topic.
        """
        query_lower = query.lower()
        
        # Topic patterns (priority order)
        patterns = [
            ('authentication', ['auth', 'login', 'password', 'jwt', 'token', 'session']),
            ('database', ['database', 'db', 'sql', 'query', 'model', 'schema', 'migration']),
            ('api', ['api', 'endpoint', 'rest', 'request', 'response', 'route']),
            ('ui', ['ui', 'frontend', 'component', 'react', 'vue', 'html', 'css']),
            ('testing', ['test', 'spec', 'mock', 'assert', 'coverage']),
            ('configuration', ['config', 'setting', 'env', 'environment']),
            ('deployment', ['deploy', 'docker', 'kubernetes', 'ci', 'cd']),
            ('error_handling', ['error', 'exception', 'catch', 'try', 'handle']),
            ('performance', ['performance', 'optimize', 'fast', 'slow', 'cache']),
            ('architecture', ['architecture', 'structure', 'design', 'pattern', 'how does', 'overview']),
        ]
        
        for topic, keywords in patterns:
            if any(kw in query_lower for kw in keywords):
                return topic
        
        # Default: extract first noun-like word
        words = query_lower.split()
        for word in words:
            if len(word) > 4 and word not in ['about', 'where', 'what', 'which', 'there']:
                return word[:20]  # Use first significant word
        
        return 'general'
    
    def _extract_code_learnings(self, query: str, answer: str, files_used: List[str]) -> List[dict]:
        """
        Extract actual code insights from the AI's answer.
        
        Instead of just summarizing Q&A, extracts:
        - File purposes discovered
        - Function/class relationships
        - Dependencies between modules
        - Patterns identified
        """
        import re
        learnings = []
        
        if not answer:
            return learnings
        
        # 1. Extract file purpose learnings (what each file does)
        for filepath in files_used:
            filename = filepath.split('/')[-1]
            # Look for mentions of this file in the answer
            file_pattern = rf'{re.escape(filename)}[^.]*(?:is|handles|manages|contains|provides|implements)[^.]*\.'
            matches = re.findall(file_pattern, answer, re.IGNORECASE)
            if matches:
                learnings.append({
                    'type': 'file_purpose',
                    'file': filepath,
                    'insight': matches[0][:200]
                })
        
        # 2. Extract function/class mentions
        func_pattern = r'`([a-zA-Z_][a-zA-Z0-9_]*)\(\)`'
        class_pattern = r'`([A-Z][a-zA-Z0-9]*)`'
        
        functions = list(set(re.findall(func_pattern, answer)))[:5]
        classes = list(set(re.findall(class_pattern, answer)))[:5]
        
        if functions:
            learnings.append({
                'type': 'key_functions',
                'functions': functions
            })
        
        if classes:
            learnings.append({
                'type': 'key_classes',
                'classes': classes
            })
        
        # 3. Extract dependency relationships
        dep_patterns = [
            r'imports? (?:from )?`([^`]+)`',
            r'depends on `([^`]+)`',
            r'uses `([^`]+)`',
            r'calls `([^`]+)`'
        ]
        
        dependencies = []
        for pattern in dep_patterns:
            deps = re.findall(pattern, answer, re.IGNORECASE)
            dependencies.extend(deps)
        
        if dependencies:
            learnings.append({
                'type': 'dependencies',
                'modules': list(set(dependencies))[:5]
            })
        
        # 4. Extract architectural patterns
        arch_keywords = ['pattern', 'architecture', 'structure', 'flow', 'design']
        for keyword in arch_keywords:
            pattern = rf'[^.]*{keyword}[^.]*\.'
            matches = re.findall(pattern, answer, re.IGNORECASE)
            if matches:
                learnings.append({
                    'type': 'architecture',
                    'insight': matches[0][:200]
                })
                break  # Only one architecture insight
        
        # 5. If no structured learnings, fall back to key sentence extraction
        if not learnings:
            # Extract sentences that contain "is", "handles", "manages" (descriptive)
            sentences = re.split(r'[.!?]', answer)
            for sent in sentences[:10]:  # Check first 10 sentences
                sent = sent.strip()
                if len(sent) > 40 and any(verb in sent.lower() for verb in ['is a', 'handles', 'manages', 'provides', 'implements']):
                    learnings.append({
                        'type': 'key_insight',
                        'insight': sent[:200]
                    })
                    if len(learnings) >= 2:  # Max 2 fallback insights
                        break
        
        return learnings



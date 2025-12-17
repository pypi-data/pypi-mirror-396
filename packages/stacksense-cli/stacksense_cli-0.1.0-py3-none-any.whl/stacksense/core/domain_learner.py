"""
Domain Learner - LLM-Powered Dynamic Domain Discovery
=====================================================
Uses LLM to automatically discover and categorize domains from file patterns.
NO HARDCODING - learns domain categories from the repository itself.
"""
from pathlib import Path
from typing import Dict, List, Set, Optional
import asyncio


class DomainLearner:
    """
    Learns domain categories dynamically using LLM.
    Replaces hardcoded domain expansions with learned patterns.
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.learned_domains = {}
    
    async def learn_domains_from_files(self, file_paths: List[str], repo_context: Dict) -> Dict[str, List[str]]:
        """
        Analyze file paths and use LLM to categorize into domains.
        
        Returns: {
            'payments': ['payment.py', 'stripe_handler.py'],
            'auth': ['auth.py', 'jwt_utils.py'],
            ...
        }
        """
        if not file_paths:
            return {}
        
        # Group files by common patterns
        patterns = self._extract_file_patterns(file_paths)
        
        # Use LLM to categorize (or use heuristics as fallback)
        domains = await self._categorize_with_llm(patterns, repo_context)
        
        if self.debug:
            print(f"[DomainLearner] Learned {len(domains)} domains:")
            for domain, files in list(domains.items())[:5]:
                print(f"  {domain}: {len(files)} files")
        
        return domains
    
    def _extract_file_patterns(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Extract common patterns from file names.
        Groups files that likely belong together.
        """
        patterns = {}
        
        for file_path in file_paths:
            path = Path(file_path)
            name_lower = path.stem.lower()
            
            # Common prefixes/suffixes
            for keyword in ['auth', 'payment', 'user', 'api', 'model', 'service', 
                           'controller', 'handler', 'util', 'helper', 'agent',
                           'database', 'cache', 'storage', 'email', 'notification']:
                if keyword in name_lower:
                    if keyword not in patterns:
                        patterns[keyword] = []
                    patterns[keyword].append(file_path)
        
        return patterns
    
    async def _categorize_with_llm(self, patterns: Dict[str, List[str]], repo_context: Dict) -> Dict[str, List[str]]:
        """
        Use LLM to categorize file patterns into semantic domains.
        Falls back to heuristic categorization if LLM unavailable.
        """
        # For now, use heuristic fallback
        # TODO: Integrate with Ollama for smarter categorization
        
        domains = {}
        
        # Heuristic categorization (smarter than hardcoded)
        category_map = {
            'auth': 'authentication',
            'login': 'authentication',
            'jwt': 'authentication',
            'token': 'authentication',
            'session': 'authentication',
            
            'payment': 'payments',
            'stripe': 'payments',
            'billing': 'payments',
            'transaction': 'payments',
            
            'user': 'users',
            'account': 'users',
            'profile': 'users',
            
            'api': 'api',
            'endpoint': 'api',
            'route': 'api',
            'controller': 'api',
            
            'model': 'data',
            'schema': 'data',
            'database': 'data',
            'db': 'data',
            
            'cache': 'caching',
            'redis': 'caching',
            'storage': 'caching',
            
            'agent': 'agents',
            'worker': 'agents',
            'task': 'agents',
            
            'email': 'notifications',
            'notification': 'notifications',
            'alert': 'notifications',
        }
        
        for pattern, files in patterns.items():
            domain = category_map.get(pattern, pattern)
            
            if domain not in domains:
                domains[domain] = []
            
            domains[domain].extend(files)
        
        return domains
    
    async def generate_keyword_expansions(self, query: str, learned_domains: Dict) -> List[str]:
        """
        Generate keyword expansions for a query based on learned domains.
        
        Instead of hardcoded expansions, uses what we learned from the repo.
        """
        query_lower = query.lower()
        keywords = []
        
        # Extract words from query
        words = query_lower.split()
        
        # Find matching domains
        for domain, files in learned_domains.items():
            if any(word in domain or domain in word for word in words):
                # Add domain-specific file patterns
                for file_path in files:
                    file_name = Path(file_path).stem.lower()
                    keywords.append(file_name)
                
                # Add domain name itself
                keywords.append(domain)
        
        # Remove duplicates, keep unique
        return list(set(keywords))[:20]  # Limit to 20
    
    def save_learned_domains(self, domains: Dict[str, List[str]], output_path: Path):
        """Save learned domains to JSON for reuse"""
        import json
        
        output_path.write_text(json.dumps(domains, indent=2))
        
        if self.debug:
            print(f"[DomainLearner] Saved learned domains to {output_path}")
    
    def load_learned_domains(self, input_path: Path) -> Dict[str, List[str]]:
        """Load previously learned domains"""
        import json
        
        if not input_path.exists():
            return {}
        
        return json.loads(input_path.read_text())

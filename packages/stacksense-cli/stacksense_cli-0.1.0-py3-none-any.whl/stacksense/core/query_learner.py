"""
Query Learner - Categorize Queries and Build Knowledge
=======================================================
Learns which files relate to which intents (payments, auth, agents, etc.)
Builds query_map.json over time.
"""
from typing import Dict, List, Set, Optional
from pathlib import Path
import re


class QueryLearner:
    """
    Learns from user queries to categorize files and build semantic understanding.
    """
    
    # Domain keywords that map to categories
    CATEGORY_KEYWORDS = {
        'payments': ['payment', 'stripe', 'paypal', 'transaction', 'billing', 'charge', 'invoice', 'checkout'],
        'auth': ['auth', 'authentication', 'login', 'signin', 'jwt', 'token', 'session', 'password', 'oauth'],
        'users': ['user', 'account', 'profile', 'member', 'customer'],
        'agents': ['agent', 'worker', 'task', 'handler', 'router', 'spider', 'core', 'code'],
        'database': ['database', 'db', 'model', 'schema', 'migration', 'sql', 'orm', 'query'],
        'cache': ['cache', 'redis', 'memcache', 'storage', 'store', 'chroma'],
        'api': ['api', 'endpoint', 'route', 'controller', 'view', 'handler', 'rest'],
        'ai_ml': ['model', 'ai', 'ml', 'neural', 'training', 'inference', 'ollama', 'llm', 'embedding'],
        'files': ['file', 'upload', 'download', 'storage', 's3', 'blob'],
        'email': ['email', 'mail', 'smtp', 'sendgrid', 'notification'],
    }
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def categorize_query(self, query: str) -> List[str]:
        """
        Extract intent categories from a query.
        Returns list of matching categories.
        
        Example:
            "How does payment processing work?" → ['payments']
            "User authentication with JWT" → ['auth', 'users']
        """
        query_lower = query.lower()
        
        # Remove stopwords
        stopwords = {'what', 'how', 'where', 'when', 'why', 'who', 'does', 'do', 'is', 'are', 'the', 'this', 'that'}
        words = set(re.findall(r'\b\w+\b', query_lower)) - stopwords
        
        # Match against category keywords
        matched_categories = []
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            # Check if any keyword matches
            if any(keyword in words or keyword in query_lower for keyword in keywords):
                matched_categories.append(category)
        
        if self.debug:
            print(f"[QueryLearner] Query: '{query}'")
            print(f"[QueryLearner] Categories: {matched_categories}")
        
        return matched_categories if matched_categories else ['general']
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract entities from query (files, functions, classes).
        Uses simple pattern matching.
        """
        entities = {
            'files': [],
            'classes': [],
            'functions': []
        }
        
        # Look for file patterns (*.py, *.ts, etc.)
        file_pattern = r'\b\w+\.(py|js|ts|tsx|jsx|go|java|rb)\b'
        entities['files'] = re.findall(file_pattern, query, re.IGNORECASE)
        
        # Look for class-like patterns (PascalCase)
        class_pattern = r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b'
        entities['classes'] = re.findall(class_pattern, query)
        
        # Look for function-like patterns (snake_case or camelCase with ())
        func_pattern = r'\b\w+\(\s*\)'
        entities['functions'] = [f.replace('()', '') for f in re.findall(func_pattern, query)]
        
        return entities
    
    def build_learning_data(self, query: str, relevant_files: List[str], extractions: Optional[Dict] = None) -> Dict:
        """
        Build structured learning data from a query interaction.
        
        Args:
            query: User's question
            relevant_files: Files that were relevant to answering
            extractions: Optional code extractions from those files
        
        Returns:
            Learning data dict ready for query_map.json
        """
        categories = self.categorize_query(query)
        entities = self.extract_entities(query)
        
        learning_data = {
            'query': query,
            'categories': categories,
            'files': relevant_files,
            'entities': entities,
        }
        
        # Add extraction data if provided
        if extractions:
            learning_data['functions'] = {}
            learning_data['classes'] = {}
            
            for file_path, extraction in extractions.items():
                # Extract function names
                if 'functions' in extraction:
                    for func in extraction['functions']:
                        func_name = func.get('name', '')
                        if func_name:
                            learning_data['functions'][func_name] = {
                                'file': file_path,
                                'signature': func.get('signature', '')
                            }
                
                # Extract class names
                if 'classes' in extraction:
                    for cls in extraction['classes']:
                        cls_name = cls.get('name', '')
                        if cls_name:
                            learning_data['classes'][cls_name] = {
                                'file': file_path,
                                'methods': [m.get('name') for m in cls.get('methods', [])]
                            }
        
        if self.debug:
            print(f"[QueryLearner] Built learning data:")
            print(f"  Categories: {categories}")
            print(f"  Files: {len(relevant_files)}")
            print(f"  Functions: {len(learning_data.get('functions', {}))}")
        
        return learning_data
    
    def suggest_category(self, file_path: str) -> str:
        """
        Suggest a category for a file based on its name/path.
        """
        file_lower = file_path.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in file_lower for keyword in keywords):
                return category
        
        return 'general'

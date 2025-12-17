"""
Context Builder
================
Intelligent context selection for AI queries.
Chooses appropriate depth (overview/signatures/deep) based on query needs.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import re


class ContextBuilder:
    """Build intelligent context for AI queries"""
    
    def __init__(self, scan_context: Dict[str, Any], debug: bool = False):
        """
        Initialize context builder.
        
        Args:
            scan_context: Full context from scanner (with code extracts)
            debug: Enable debug output
        """
        self.scan_context = scan_context
        self.debug = debug
    
    def build_for_query(self, query: str, depth: str = "auto") -> Dict[str, Any]:
        """
        Build context appropriate for query.
        
        Args:
            query: User's question
            depth: "overview", "signatures", "deep", or "auto"
        
        Returns:
            Context dict optimized for query
        """
        # Auto-determine depth if requested
        if depth == "auto":
            depth = self._classify_query_depth(query)
        
        if self.debug:
            print(f"[ContextBuilder] Query depth: {depth}")
        
        # Extract entities mentioned in query
        entities = self._extract_entities(query)
        
        if depth == "overview":
            return self._build_overview_context(entities)
        elif depth == "signatures":
            return self._build_signature_context(entities)
        else:  # deep
            return self._build_deep_context(entities)
    
    def _classify_query_depth(self, query: str) -> str:
        """
        Classify what depth of context is needed.
        
        Returns:
            "overview", "signatures", or "deep"
        """
        query_lower = query.lower()
        
        # Deep: Needs implementation details
        deep_indicators = [
            'how does',
            'how is',
            'implementation',
            'algorithm',
            'logic',
            'code',
            'function',
            'method',
            'choices',
            'values',
            'fields',
            'specific',
        ]
        
        if any(ind in query_lower for ind in deep_indicators):
            return "deep"
        
        # Overview: Architecture/high-level questions
        overview_indicators = [
            'architecture',
            'structure',
            'overview',
            'tech stack',
            'frameworks',
            'what is',
            'describe',
        ]
        
        if any(ind in query_lower for ind in overview_indicators):
            return "overview"
        
        # Default to signatures (balance of detail and speed)
        return "signatures"
    
    def _extract_entities(self, query: str) -> Set[str]:
        """
        Extract entities (models, classes, modules) from query.
        
        Returns:
            Set of entity names
        """
        entities = set()
        
        # Common Django/code entities
        entity_patterns = [
            r'\b(User|Payment|Chat|Call|Prayer|Notification)\w*\b',
            r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b',  # CamelCase
            r'\b(user|payment|chat|call|prayer|notification)s?\b',
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities.update(m if isinstance(m, str) else m[0] for m in matches)
        
        return entities
    
    def _build_overview_context(self, entities: Set[str]) -> Dict[str, Any]:
        """Build high-level overview context"""
        
        return {
            'workspace': self.scan_context.get('workspace'),
            'total_files': self.scan_context.get('total_files'),
            'languages': self.scan_context.get('languages', {}),
            'frameworks': self.scan_context.get('frameworks', []),
            'patterns': self.scan_context.get('patterns', {}),
            'modules': self._get_module_summaries(),
            'live_readme': self.scan_context.get('live_readme', ''),
            'context_depth': 'overview'
        }
    
    def _build_signature_context(self, entities: Set[str]) -> Dict[str, Any]:
        """Build context with code signatures (classes, methods)"""
        
        context = self._build_overview_context(entities)
        context['context_depth'] = 'signatures'
        
        # Add code signatures for relevant modules
        relevant_modules = self._find_relevant_modules(entities)
        
        signatures = {}
        for module_key in relevant_modules:
            module = self.scan_context['modules'].get(module_key, {})
            
            if 'code_extracts' in module:
                for file_path, extract in module['code_extracts'].items():
                    # Python signatures
                    if 'classes' in extract:
                        for cls in extract['classes']:
                            signatures[cls['name']] = {
                                'type': 'class',
                                'file': file_path,
                                'bases': cls.get('bases', []),
                                'methods': [m['name'] for m in cls.get('methods', [])],
                                'has_choices': bool(cls.get('choices', {})),
                                'line_start': cls.get('line_start')
                            }
                    
                    if 'functions' in extract:
                        for func in extract['functions']:
                            signatures[func['name']] = {
                                'type': 'function',
                                'file': file_path,
                                'params': func.get('params', []),
                                'is_async': func.get('is_async', False)
                            }
        
        context['code_signatures'] = signatures
        return context
    
    def _build_deep_context(self, entities: Set[str]) -> Dict[str, Any]:
        """Build deep context with full code details"""
        
        context = self._build_signature_context(entities)
        context['context_depth'] = 'deep'
        
        # Add full code extracts for relevant entities
        relevant_modules = self._find_relevant_modules(entities)
        
        code_details = {}
        for module_key in relevant_modules:
            module = self.scan_context['modules'].get(module_key, {})
            
            if 'code_extracts' in module:
                for file_path, extract in module['code_extracts'].items():
                    # Include full class details
                    if 'classes' in extract:
                        for cls in extract['classes']:
                            # Check if this class matches entities
                            if cls['name'] in entities or any(e.lower() in cls['name'].lower() for e in entities):
                                code_details[cls['name']] = {
                                    'type': 'class',
                                    'file': file_path,
                                    'docstring': cls.get('docstring'),
                                    'bases': cls.get('bases', []),
                                    'methods': cls.get('methods', []),
                                    'fields': cls.get('fields', {}),
                                    'choices': cls.get('choices', {}),  # IMPORTANT!
                                    'line_range': (cls.get('line_start'), cls.get('line_end'))
                                }
        
        context['code_details'] = code_details
        return context
    
    def _find_relevant_modules(self, entities: Set[str]) -> List[str]:
        """Find modules relevant to entities"""
        
        relevant = []
        modules = self.scan_context.get('modules', {})
        
        for module_key, module_data in modules.items():
            if not isinstance(module_data, dict):
                continue
            
            # Check if module name matches entities
            module_name = module_data.get('name', '').lower()
            if any(ent.lower() in module_name for ent in entities):
                relevant.append(module_key)
                continue
            
            # Check if module files contain entities
            if 'code_extracts' in module_data:
                for extract in module_data['code_extracts'].values():
                    if 'classes' in extract:
                        class_names = {cls['name'] for cls in extract['classes']}
                        if entities & class_names:  # Intersection
                            relevant.append(module_key)
                            break
        
        return relevant
    
    def _get_module_summaries(self) -> List[Dict[str, Any]]:
        """Get simplified module summaries for overview"""
        
        summaries = []
        modules = self.scan_context.get('modules', {})
        
        for module_key, module_data in modules.items():
            if not isinstance(module_data, dict):
                continue
            
            summary = {
                'name': module_data.get('name', module_key),
                'description': module_data.get('description', ''),
                'key_features': module_data.get('key_features', []),
                'file_count': len(module_data.get('files', [])),
                'has_code_details': 'code_extracts' in module_data
            }
            summaries.append(summary)
        
        return summaries


def build_context(scan_context: Dict[str, Any], query: str, depth: str = "auto", debug: bool = False) -> Dict[str, Any]:
    """
    Convenience function to build context.
    
    Args:
        scan_context: Full context from scanner
        query: User's question
        depth: Context depth ("auto", "overview", "signatures", "deep")
        debug: Enable debug output
    
    Returns:
        Optimized context for query
    """
    builder = ContextBuilder(scan_context, debug=debug)
    return builder.build_for_query(query, depth=depth)

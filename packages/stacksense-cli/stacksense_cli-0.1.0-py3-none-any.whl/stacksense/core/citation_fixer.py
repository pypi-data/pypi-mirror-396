"""
Citation Auto-Fixer - Dynamic Post-Generation Citation Injection
================================================================
Automatically adds missing file citations to AI responses.
100% dynamic - works with ANY file types, languages, or frameworks.
"""
from typing import Dict, Any, List, Tuple
from pathlib import Path
import re


class CitationAutoFixer:
    """
    Automatically inject missing citations into AI responses.
    Fully dynamic - no hardcoded file types or patterns.
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def fix_citations(self, response: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Add missing [filename] citations automatically.
        
        Args:
            response: AI-generated response
            context: Context with code_extractions
            
        Returns:
            (fixed_response, stats)
        """
        # Extract existing citations
        existing_citations = set(re.findall(r'\[([^\]]+\.\w+)\]', response))
        
        # Build dynamic file index from context
        file_index = self._build_file_index(context)
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', response)
        fixed_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence talks about code (dynamic detection)
            is_code_reference = self._is_code_sentence(sentence_lower)
            
            if is_code_reference:
                # Find which file this sentence is about
                best_match = self._find_best_file_match(sentence_lower, file_index)
                
                if best_match and f"[{best_match}]" not in sentence:
                    # Inject citation at start
                    sentence = f"[{best_match}] {sentence}"
            
            fixed_sentences.append(sentence)
        
        fixed_response = ' '.join(fixed_sentences)
        
        # Calculate improvement stats
        new_citations = set(re.findall(r'\[([^\]]+\.\w+)\]', fixed_response))
        available_files = len(context.get('code_extractions', {}))
        
        stats = {
            'original_citations': len(existing_citations),
            'added_citations': len(new_citations - existing_citations),
            'total_citations': len(new_citations),
            'files_available': available_files,
            'citation_rate': (len(new_citations) / max(available_files, 1)) * 100
        }
        
        if self.debug:
            print(f"[CitationFixer] {stats['original_citations']} → {stats['total_citations']} citations")
            print(f"[CitationFixer] Added: {', '.join(new_citations - existing_citations)}")
        
        return fixed_response, stats
    
    def _build_file_index(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Build dynamic index of identifiers → filenames.
        No hardcoding - works with any language/framework.
        """
        file_index = {}
        code_extractions = context.get('code_extractions', {})
        
        for file_name, extraction in code_extractions.items():
            # Index by file stem (without extension)
            file_path = Path(file_name)
            file_stem = file_path.stem.lower()
            file_index[file_stem] = file_name
            
            # Index by functions (any language)
            for func in extraction.get('functions', []):
                func_name = func.get('name', '').lower()
                if func_name:
                    file_index[func_name] = file_name
            
            # Index by classes (any language)
            for cls in extraction.get('classes', []):
                cls_name = cls.get('name', '').lower()
                if cls_name:
                    file_index[cls_name] = file_name
                
                # Index by methods too
                for method in cls.get('methods', [])[:3]:
                    method_name = method.lower() if isinstance(method, str) else ''
                    if method_name:
                        file_index[method_name] = file_name
        
        return file_index
    
    def _is_code_sentence(self, sentence_lower: str) -> bool:
        """
        Detect if sentence references code.
        Dynamic - no hardcoded language keywords.
        """
        # Universal code indicators (language-agnostic)
        code_indicators = [
            # Actions
            'handles', 'processes', 'implements', 'uses', 'calls',
            'returns', 'validates', 'defines', 'creates', 'manages',
            'executes', 'performs', 'coordinates', 'routes',
            
            # Code concepts
            'function', 'method', 'class', 'module', 'component',
            'service', 'handler', 'controller', 'model', 'view',
            'interface', 'type', 'struct', 'enum',
            
            # Technical terms
            'defined in', 'implemented in', 'found in', 'located in',
            'via', 'through', 'using', 'by',
        ]
        
        return any(indicator in sentence_lower for indicator in code_indicators)
    
    def _find_best_file_match(self, sentence_lower: str, file_index: Dict[str, str]) -> str:
        """
        Find which file sentence is about.
        Scores by specificity (longer matches = more specific).
        """
        best_match = None
        best_score = 0
        
        for identifier, file_name in file_index.items():
            if identifier in sentence_lower:
                # Score by identifier length (longer = more specific)
                # e.g., "authentication_handler" beats "auth"
                score = len(identifier)
                
                if score > best_score:
                    best_score = score
                    best_match = file_name
        
        return best_match

"""
StackSense Keyword Extractor
Extracts search keywords from queries using model-size-aware prompts
"""
import re
from typing import List, Dict, Optional


class KeywordExtractor:
    """
    Extract keywords from user queries for targeted grep searching.
    
    Uses different prompting strategies based on model size:
    - Small models: Light prompt, 2 specific keywords
    - Medium/Large models: Diverse keywords with synonyms
    """
    
    def __init__(self, model, model_size: str = 'medium', debug: bool = False):
        """
        Args:
            model: AI model instance
            model_size: 'small', 'medium', or 'large'
            debug: Enable debug logging
        """
        self.model = model
        self.model_size = model_size
        self.debug = debug
    
    def extract_keywords(self, query: str, diagram_summary: str = "") -> List[str]:
        """
        Extract search keywords from query.
        
        Args:
            query: User's question
            diagram_summary: Optional diagram summary for context
            
        Returns:
            List of keywords to search for
        """
        if self.model_size == 'small':
            return self._extract_for_small_model(query, diagram_summary)
        else:
            return self._extract_for_large_model(query, diagram_summary)
    
    def _extract_for_small_model(self, query: str, diagram_summary: str) -> List[str]:
        """
        Extract keywords for small models.
        Light prompt, returns 2 specific keywords.
        """
        prompt = f"""Extract 2 specific keywords from this query for code search.

Query: "{query}"

Return ONLY the keywords, one per line. No explanations.

Keywords:"""
        
        try:
            response = self.model.generate(prompt, max_tokens=50)
            
            # Parse response
            keywords = []
            for line in response.split('\n'):
                line = line.strip()
                if line and not line.endswith(':'):
                    # Remove numbering, bullets, etc.
                    keyword = re.sub(r'^[\d\.\-\*]\s+', '', line)
                    keyword = keyword.strip('"\'')
                    if keyword:
                        keywords.append(keyword)
                        if len(keywords) >= 2:
                            break
            
            if self.debug:
                print(f"[KeywordExtractor] Small model keywords: {keywords}")
            
            return keywords if keywords else self._fallback_keywords(query)
            
        except Exception as e:
            if self.debug:
                print(f"[KeywordExtractor] Error: {e}")
            return self._fallback_keywords(query)
    
    def _extract_for_large_model(self, query: str, diagram_summary: str) -> List[str]:
        """
        Extract keywords for medium/large models.
        Diverse keywords including synonyms and related terms.
        """
        context = f"\n\nCodebase structure:\n{diagram_summary}" if diagram_summary else ""
        
        prompt = f"""You are helping search a codebase. Generate diverse search keywords for this query.

Query: "{query}"
{context}

Generate 4-6 keywords including:
1. Primary keywords from the query
2. Synonyms and related terms
3. Technical terms related to the topic
4. Common code patterns related to the query

If the query is ambiguous, use the codebase structure to suggest relevant keywords.

Return ONLY keywords, one per line. No explanations.

Keywords:"""
        
        try:
            response = self.model.generate(prompt, max_tokens=150)
            
            # Parse response
            keywords = []
            for line in response.split('\n'):
                line = line.strip()
                if line and not line.endswith(':'):
                    # Remove numbering, bullets, etc.
                    keyword = re.sub(r'^[\d\.\-\*]\s+', '', line)
                    keyword = keyword.strip('"\'')
                    if keyword and len(keyword) < 30:  # Sanity check
                        keywords.append(keyword)
                        if len(keywords) >= 6:
                            break
            
            if self.debug:
                print(f"[KeywordExtractor] Large model keywords: {keywords}")
            
            return keywords if keywords else self._fallback_keywords(query)
            
        except Exception as e:
            if self.debug:
                print(f"[KeywordExtractor] Error: {e}")
            return self._fallback_keywords(query)
    
    def _fallback_keywords(self, query: str) -> List[str]:
        """
        Fallback keyword extraction using simple heuristics.
        
        Args:
            query: User query
            
        Returns:
            List of extracted keywords
        """
        # Remove common question words
        stop_words = {
            'what', 'where', 'when', 'why', 'how', 'is', 'are', 'the', 
            'a', 'an', 'to', 'from', 'in', 'on', 'at', 'for', 'with',
            'does', 'do', 'can', 'should', 'would', 'will', 'this', 'that'
        }
        
        # Extract words
        words = re.findall(r'\w+', query.lower())
        
        # Filter stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Return top keywords (up to 4)
        return keywords[:4] if keywords else ['TODO']
    
    def expand_keywords(self, keywords: List[str]) -> List[str]:
        """
        Expand keywords with common variations.
        
        Args:
            keywords: Base keywords
            
        Returns:
            Expanded keyword list
        """
        expanded = set(keywords)
        
        for keyword in keywords:
            # Add camelCase and snake_case variations
            if '_' in keyword:
                # snake_case -> camelCase
                parts = keyword.split('_')
                camel = parts[0] + ''.join(p.capitalize() for p in parts[1:])
                expanded.add(camel)
                # Also PascalCase
                pascal = ''.join(p.capitalize() for p in parts)
                expanded.add(pascal)
            
            elif keyword[0].isupper() and any(c.isupper() for c in keyword[1:]):
                # PascalCase/camelCase -> snake_case
                snake = re.sub(r'([A-Z])', r'_\1', keyword).lower().lstrip('_')
                expanded.add(snake)
        
        return list(expanded)

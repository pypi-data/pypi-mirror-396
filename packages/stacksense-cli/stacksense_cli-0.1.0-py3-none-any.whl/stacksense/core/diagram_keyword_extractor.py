"""
AI-Powered Diagram-Aware Keyword Extraction
============================================
Uses the AI model to analyze user queries against the diagram context
to generate relevant, project-specific keywords.

NO hardcoding - fully dynamic based on what the AI sees in the diagram.
"""
from typing import List, Dict, Any, Optional


class DiagramAwareKeywordExtractor:
    """
    Extracts keywords by having the AI analyze:
    1. The user's natural language query
    2. The codebase diagram (files, classes, functions, dependencies)
    
    This allows understanding queries like "safety mechanisms" → "authentication, validation"
    based on what actually exists in the codebase.
    """
    
    def __init__(self, model, debug: bool = False):
        """
        Args:
            model: AI model with .generate(prompt) method
            debug: Enable debug output
        """
        self.model = model
        self.debug = debug
    
    def extract_keywords(
        self, 
        query: str, 
        diagram_summary: str,
        file_list: List[str] = None,
        function_list: List[str] = None,
        class_list: List[str] = None
    ) -> List[str]:
        """
        Extract relevant keywords by having AI analyze query against diagram.
        
        Args:
            query: User's natural language question
            diagram_summary: Text summary of codebase architecture
            file_list: List of files in the codebase
            function_list: List of function names
            class_list: List of class names
            
        Returns:
            List of keywords to grep for
        """
        # Build context about what's in the codebase
        codebase_context = self._build_codebase_context(
            diagram_summary, file_list, function_list, class_list
        )
        
        # Create prompt for AI to extract keywords
        prompt = self._create_keyword_prompt(query, codebase_context)
        
        # Get AI response
        try:
            response = self.model.generate(prompt)
            keywords = self._parse_keywords(response)
            
            if self.debug:
                print(f"[KeywordExtractor] Query: {query}")
                print(f"[KeywordExtractor] AI Keywords: {keywords}")
            
            return keywords
            
        except Exception as e:
            if self.debug:
                print(f"[KeywordExtractor] AI failed: {e}, using fallback")
            return self._fallback_keywords(query, file_list or [])
    
    def _build_codebase_context(
        self, 
        diagram_summary: str,
        file_list: List[str],
        function_list: List[str],
        class_list: List[str]
    ) -> str:
        """Build concise context about codebase for AI"""
        parts = []
        
        # Add diagram summary (truncated if too long)
        if diagram_summary:
            lines = diagram_summary.split('\n')[:20]
            parts.append("## Codebase Structure\n" + '\n'.join(lines))
        
        # Add key files (just names, not full paths)
        if file_list:
            key_files = [f.split('/')[-1] for f in file_list[:30]]
            parts.append(f"\n## Key Files\n{', '.join(key_files)}")
        
        # Add functions
        if function_list:
            parts.append(f"\n## Functions\n{', '.join(function_list[:20])}")
        
        # Add classes
        if class_list:
            parts.append(f"\n## Classes\n{', '.join(class_list[:20])}")
        
        return '\n'.join(parts)
    
    def _create_keyword_prompt(self, query: str, codebase_context: str) -> str:
        """Create prompt for AI keyword extraction"""
        return f"""You are analyzing a codebase to find relevant code for a user's question.

{codebase_context}

USER QUESTION: {query}

Based on the codebase structure above, what specific keywords should I search for?

INSTRUCTIONS:
1. Look at the files, classes, and functions in this codebase
2. Identify which ones are relevant to the user's question
3. Output 3-6 keywords that would find relevant code
4. Use actual names from the codebase (file names, function names, class names)
5. Include both specific terms and related concepts

OUTPUT FORMAT (one keyword per line):
keyword1
keyword2
keyword3
...

KEYWORDS:"""
    
    def _parse_keywords(self, response: str) -> List[str]:
        """Parse keywords from AI response"""
        keywords = []
        
        # Split by newlines and clean
        for line in response.strip().split('\n'):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that look like instructions
            if any(skip in line.lower() for skip in ['keyword', 'output', 'instruction', ':']):
                continue
            
            # Clean the keyword
            keyword = line.strip('- •·*').strip()
            
            # Skip if too short or too long
            if len(keyword) < 2 or len(keyword) > 50:
                continue
            
            # Skip if contains special characters (likely not a real keyword)
            if any(c in keyword for c in ['[', ']', '{', '}', '(', ')']):
                continue
            
            keywords.append(keyword.lower())
        
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for k in keywords:
            if k not in seen:
                seen.add(k)
                unique.append(k)
        
        return unique[:8]  # Max 8 keywords
    
    def _fallback_keywords(self, query: str, file_list: List[str]) -> List[str]:
        """Fallback if AI fails - extract words from query + match to files"""
        # Get words from query
        words = query.lower().split()
        stop_words = {'a', 'an', 'the', 'is', 'are', 'what', 'how', 'why', 'this', 'that', 'about', 'tell', 'me'}
        query_words = [w.strip('.,!?') for w in words if w not in stop_words and len(w) > 2]
        
        # Try to match query words to file names
        keywords = []
        for word in query_words:
            for file in file_list:
                file_lower = file.lower()
                if word in file_lower:
                    # Add the matching part as a keyword
                    keywords.append(word)
                    break
        
        # If no matches, use query words + common code terms
        if not keywords:
            keywords = query_words[:3] + ['class', 'def', 'function']
        
        return keywords[:6]


def extract_keywords_with_ai(
    model,
    query: str,
    diagram_summary: str,
    diagram_metadata: Dict[str, Any] = None,
    debug: bool = False
) -> List[str]:
    """
    Convenience function to extract keywords using AI.
    
    Args:
        model: AI model with .generate() method
        query: User's question
        diagram_summary: Codebase architecture summary
        diagram_metadata: Optional metadata with files, functions, classes
        debug: Enable debug output
        
    Returns:
        List of keywords to search for
    """
    extractor = DiagramAwareKeywordExtractor(model, debug=debug)
    
    file_list = None
    function_list = None
    class_list = None
    
    if diagram_metadata:
        # Extract lists from diagram nodes
        file_list = [node.get('id', '') for node in diagram_metadata.get('nodes', [])]
        
        # Collect all functions and classes
        function_list = []
        class_list = []
        for node in diagram_metadata.get('nodes', []):
            function_list.extend(node.get('functions', []))
            class_list.extend(node.get('classes', []))
    
    return extractor.extract_keywords(
        query=query,
        diagram_summary=diagram_summary,
        file_list=file_list,
        function_list=function_list,
        class_list=class_list
    )

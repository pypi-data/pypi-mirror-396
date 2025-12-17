"""
File Selector Agent - AI-Powered File Picking
==============================================
Uses Ollama to intelligently select which files are most relevant
for answering a query.

Smarter than keyword matching - understands context!
"""
from typing import Dict, Any, List
import json
import re
from pathlib import Path
from .agent_system import BaseAgent


class FileSelectorAgent(BaseAgent):
    """
    AI agent that selects most relevant files for a query.
    
    Example:
        Query: "What payment providers does Telios support?"
        Analysis: {intent: "find_list", concepts: ["payment", "provider"]}
        Files: ["README.md", "payments.py", "config.yml", ...]
        
        Output: ["Backend/README.md", "core/payments.py", "config/payments.yml"]
    """
    
    def __init__(self, model: str = "llama3.1:8b-instruct-q4_0", debug: bool = False):
        super().__init__(
            name="FileSelector",
            model=model,
            timeout=45,
            debug=debug
        )
    
    async def execute(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        available_files: List[str],
        max_files: int = 8,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Select most relevant files for query.
        
        Args:
            query: Original user question
            query_analysis: Output from QueryAnalyzerAgent
            available_files: List of files to choose from
            max_files: Maximum files to return
        
        Returns:
            List of file dicts with scores:
            [
                {"file": "README.md", "score": 95, "reason": "..."},
                ...
            ]
        """
        # Filter by file types from analysis
        relevant_files = self._filter_by_type(
            available_files,
            query_analysis.get('file_types', ['*'])
        )
        
        if len(relevant_files) <= max_files:
            # Small enough, return all with scores
            return [
                {
                    "file": f,
                    "score": 50,
                    "reason": "Matches file type filter"
                }
                for f in relevant_files
            ]
        
        # Too many files - need AI to pick best ones
        system_message = """You are a file selection AI for code search.

Given a user query and list of files, select the MOST RELEVANT files.

Rules:
1. README files are usually most informative
2. Config files good for "what uses" queries
3. Source code good for "how works" queries
4. Prioritize files matching query concepts

Output ONLY valid JSON array:
[
  {"file": "path/to/file", "score": 90, "reason": "why relevant"},
  ...
]

Keep it short - return only top matches."""

        # Prepare file list (with priorities)
        file_info = []
        for f in relevant_files[:50]:  # Limit to avoid token overflow
            file_info.append({
                "path": f,
                "name": Path(f).name,
                "type": Path(f).suffix
            })
        
        prompt = f"""Query: "{query}"
Intent: {query_analysis.get('intent', 'unknown')}
Concepts: {query_analysis.get('concepts', [])}

Available files:
{json.dumps(file_info, indent=2)}

Select the {max_files} MOST RELEVANT files for this query.
Return JSON array with file paths, scores, and reasons."""

        response = await self.think(prompt, system_message, temperature=0.2)
        
        try:
            selections = self._parse_json_response(response)
            
            # Ensure we have list
            if isinstance(selections, dict):
                selections = [selections]
            
            # Validate and limit
            selections = selections[:max_files]
            
            if self.debug:
                print(f"[FileSelector] Selected {len(selections)} files:")
                for sel in selections[:3]:
                    print(f"  - {sel.get('file')} (score: {sel.get('score', 0)})")
            
            return selections
        
        except Exception as e:
            if self.debug:
                print(f"[FileSelector] AI selection failed: {e}, using fallback")
            
            # Fallback to simple scoring
            return self._fallback_selection(
                relevant_files,
                query_analysis.get('concepts', []),
                max_files
            )
    
    def _filter_by_type(self, files: List[str], file_types: List[str]) -> List[str]:
        """Filter files by type patterns"""
        if '*' in file_types or not file_types:
            return files
        
        filtered = []
        
        for file in files:
            for pattern in file_types:
                # Simple pattern matching
                if pattern == Path(file).name or \
                   pattern.replace('*', '') in file or \
                   Path(file).suffix == pattern.replace('*', ''):
                    filtered.append(file)
                    break
        
        return filtered
    
    def _parse_json_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract JSON array from response"""
        # Find JSON array
        json_match = re.search(r'\[[\s\S]*\]', response)
        
        if json_match:
            return json.loads(json_match.group(0))
        
        # Try parsing whole response
        return json.loads(response)
    
    def _fallback_selection(
        self,
        files: List[str],
        concepts: List[str],
        max_files: int
    ) -> List[Dict[str, Any]]:
        """Simple rule-based selection if AI fails"""
        scored = []
        
        for file in files:
            score = 30  # Base
            
            # Boost for README
            if 'readme' in file.lower():
                score += 40
            elif file.endswith('.md'):
                score += 20
            
            # Boost for concepts in filename
            file_lower = file.lower()
            for concept in concepts:
                if concept.lower() in file_lower:
                    score += 15
            
            scored.append({
                "file": file,
                "score": score,
                "reason": "Heuristic scoring"
            })
        
        # Sort by score and limit
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:max_files]

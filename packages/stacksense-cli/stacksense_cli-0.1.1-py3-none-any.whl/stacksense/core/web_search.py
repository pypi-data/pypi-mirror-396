"""
StackSense Web Search
Simple web search using DuckDuckGo (no API key needed)
"""
import urllib.parse
import urllib.request
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """A web search result"""
    title: str
    url: str
    snippet: str


class WebSearch:
    """
    Web search using DuckDuckGo instant answers API
    No API key required, completely free
    """
    
    DDGO_API = "https://api.duckduckgo.com/"
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search the web for a query
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            # DuckDuckGo instant answer API
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            url = f"{self.DDGO_API}?{urllib.parse.urlencode(params)}"
            
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "StackSense/1.0"}
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            results = []
            
            # Abstract (main result)
            if data.get("AbstractText"):
                results.append(SearchResult(
                    title=data.get("Heading", "Result"),
                    url=data.get("AbstractURL", ""),
                    snippet=data.get("AbstractText", "")[:300]
                ))
            
            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results - 1]:
                if isinstance(topic, dict) and topic.get("Text"):
                    # Extract URL from FirstURL
                    url = topic.get("FirstURL", "")
                    # Extract title from text (first part before " - ")
                    text = topic.get("Text", "")
                    title = text.split(" - ")[0] if " - " in text else text[:50]
                    
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=text[:200]
                    ))
            
            return results[:max_results]
            
        except Exception as e:
            # Return error as a result so AI can see it
            return [SearchResult(
                title="Search Error",
                url="",
                snippet=f"Could not complete search: {str(e)}"
            )]
    
    def search_formatted(self, query: str, max_results: int = 5) -> str:
        """
        Search and return formatted string for AI context
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            Formatted string with search results
        """
        results = self.search(query, max_results)
        
        if not results:
            return f"No results found for: {query}"
        
        output = [f"## Web Search Results for: {query}\n"]
        
        for i, r in enumerate(results, 1):
            output.append(f"### {i}. {r.title}")
            if r.url:
                output.append(f"URL: {r.url}")
            output.append(f"{r.snippet}\n")
        
        return "\n".join(output)


# Global instance
_search: Optional[WebSearch] = None


def get_search() -> WebSearch:
    """Get global web search instance"""
    global _search
    if _search is None:
        _search = WebSearch()
    return _search


def web_search(query: str, max_results: int = 5) -> str:
    """Convenience function for web search"""
    return get_search().search_formatted(query, max_results)

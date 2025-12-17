"""
StackSense Web Searcher
Parallel async search across StackOverflow, GitHub, Reddit, and dev documentation
"""
import asyncio
import json
import hashlib
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import aiohttp
except ImportError:
    # Fallback to requests if aiohttp not available
    import requests
    aiohttp = None


@dataclass
class SearchResult:
    """Represents a search result from any source"""
    source: str  # 'stackoverflow', 'github', 'reddit', 'pypi', 'mdn'
    title: str
    url: str
    snippet: str
    score: float
    metadata: Dict[str, Any]


class WebSearcher:
    """Fast parallel web search engine"""
    
    # API endpoints
    STACKOVERFLOW_API = "https://api.stackexchange.com/2.3/search"
    GITHUB_API = "https://api.github.com/search/issues"
    REDDIT_API = "https://www.reddit.com/search.json"
    PYPI_API = "https://pypi.org/pypi/{package}/json"
    MDN_API = "https://developer.mozilla.org/api/v1/search"
    
    def __init__(self, cache_path: str, debug: bool = False, timeout: float = 15.0):
        """
        Initialize web searcher.
        
        Args:
            cache_path: Path to cache JSON file
            debug: Enable debug logging
            timeout: Request timeout in seconds (default: 15.0)
        """
        self.cache_path = cache_path
        self.debug = debug
        self.timeout = timeout
        self.results: List[SearchResult] = []
        self.cache: Dict[str, List[SearchResult]] = {}
        self.max_retries = 2  # Retry failed requests
        
    def _optimize_query(self, raw_query: str) -> str:
        """
        Optimize search query by extracting keywords.
        
        Args:
            raw_query: Raw user input
            
        Returns:
            Optimized search query
        """
        # Remove common filler words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'can', 'my', 'your', 'i', 'you'
        }
        
        # Extract words
        words = raw_query.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Take top 5 keywords
        optimized = ' '.join(keywords[:5])
        
        if self.debug:
            print(f"[Searcher] Optimized query: '{raw_query}' → '{optimized}'")
        
        return optimized or raw_query
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query caching"""
        return hashlib.md5(query.encode()).hexdigest()[:8]
    
    async def _search_stackoverflow(self, query: str, timeout: float = 15.0) -> List[SearchResult]:
        """
        Search StackOverflow using official API.
        
        Args:
            query: Search query
            timeout: Request timeout in seconds
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'intitle': query,
                'site': 'stackoverflow',
                'pagesize': 3
            }
            
            if aiohttp:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.STACKOVERFLOW_API,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            items = data.get('items', [])
                            
                            for item in items[:3]:  # Max 3 results
                                results.append(SearchResult(
                                    source='stackoverflow',
                                    title=item.get('title', ''),
                                    url=item.get('link', ''),
                                    snippet=item.get('body_markdown', '')[:200],
                                    score=item.get('score', 0),
                                    metadata={
                                        'answers': item.get('answer_count', 0),
                                        'views': item.get('view_count', 0)
                                    }
                                ))
            else:
                # Fallback to sync requests
                response = requests.get(self.STACKOVERFLOW_API, params=params, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    for item in items[:3]:
                        results.append(SearchResult(
                            source='stackoverflow',
                            title=item.get('title', ''),
                            url=item.get('link', ''),
                            snippet=item.get('body_markdown', '')[:200],
                            score=item.get('score', 0),
                            metadata={
                                'answers': item.get('answer_count', 0),
                                'views': item.get('view_count', 0)
                            }
                        ))
        except Exception as e:
            if self.debug:
                print(f"[Searcher] StackOverflow error: {e}")
        
        return results
    
    async def _search_github(self, query: str, timeout: float = 15.0) -> List[SearchResult]:
        """
        Search GitHub issues/PRs using unauthenticated API.
        
        Args:
            query: Search query
            timeout: Request timeout
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            params = {
                'q': query,
                'sort': 'relevance',
                'per_page': 3
            }
            
            if aiohttp:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.GITHUB_API,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            items = data.get('items', [])
                            
                            for item in items[:3]:
                                results.append(SearchResult(
                                    source='github',
                                    title=item.get('title', ''),
                                    url=item.get('html_url', ''),
                                    snippet=item.get('body', '')[:200] if item.get('body') else '',
                                    score=item.get('score', 0),
                                    metadata={
                                        'state': item.get('state', ''),
                                        'comments': item.get('comments', 0)
                                    }
                                ))
            else:
                response = requests.get(self.GITHUB_API, params=params, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    for item in items[:3]:
                        results.append(SearchResult(
                            source='github',
                            title=item.get('title', ''),
                            url=item.get('html_url', ''),
                            snippet=item.get('body', '')[:200] if item.get('body') else '',
                            score=item.get('score', 0),
                            metadata={
                                'state': item.get('state', ''),
                                'comments': item.get('comments', 0)
                            }
                        ))
        except Exception as e:
            if self.debug:
                print(f"[Searcher] GitHub error: {e}")
        
        return results
    
    async def _search_reddit(self, query: str, timeout: float = 15.0) -> List[SearchResult]:
        """
        Search Reddit using unofficial JSON API.
        
        Args:
            query: Search query
            timeout: Request timeout
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            params = {
                'q': f"{query} subreddit:programming OR subreddit:learnprogramming OR subreddit:webdev",
                'limit': 3,
                'sort': 'relevance'
            }
            
            headers = {'User-Agent': 'StackSense/1.0'}
            
            if aiohttp:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.REDDIT_API,
                        params=params,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            posts = data.get('data', {}).get('children', [])
                            
                            for post in posts[:3]:
                                post_data = post.get('data', {})
                                results.append(SearchResult(
                                    source='reddit',
                                    title=post_data.get('title', ''),
                                    url=f"https://reddit.com{post_data.get('permalink', '')}",
                                    snippet=post_data.get('selftext', '')[:200],
                                    score=post_data.get('score', 0),
                                    metadata={
                                        'subreddit': post_data.get('subreddit', ''),
                                        'comments': post_data.get('num_comments', 0)
                                    }
                                ))
            else:
                response = requests.get(self.REDDIT_API, params=params, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts[:3]:
                        post_data = post.get('data', {})
                        results.append(SearchResult(
                            source='reddit',
                            title=post_data.get('title', ''),
                            url=f"https://reddit.com{post_data.get('permalink', '')}",
                            snippet=post_data.get('selftext', '')[:200],
                            score=post_data.get('score', 0),
                            metadata={
                                'subreddit': post_data.get('subreddit', ''),
                                'comments': post_data.get('num_comments', 0)
                            }
                        ))
        except Exception as e:
            if self.debug:
                print(f"[Searcher] Reddit error: {e}")
        
        return results
    
    async def _search_mdn(self, query: str, timeout: float = 15.0) -> List[SearchResult]:
        """
        Search MDN Web Docs using official API.
        
        Args:
            query: Search query
            timeout: Request timeout
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            params = {'q': query}
            
            if aiohttp:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.MDN_API,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            documents = data.get('documents', [])
                            
                            for doc in documents[:3]:
                                results.append(SearchResult(
                                    source='mdn',
                                    title=doc.get('title', ''),
                                    url=f"https://developer.mozilla.org{doc.get('mdn_url', '')}",
                                    snippet=doc.get('summary', '')[:200],
                                    score=doc.get('score', 0),
                                    metadata={
                                        'locale': doc.get('locale', 'en-US')
                                    }
                                ))
            else:
                response = requests.get(self.MDN_API, params=params, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get('documents', [])
                    
                    for doc in documents[:3]:
                        results.append(SearchResult(
                            source='mdn',
                            title=doc.get('title', ''),
                            url=f"https://developer.mozilla.org{doc.get('mdn_url', '')}",
                            snippet=doc.get('summary', '')[:200],
                            score=doc.get('score', 0),
                            metadata={
                                'locale': doc.get('locale', 'en-US')
                            }
                        ))
        except Exception as e:
            if self.debug:
                print(f"[Searcher] MDN error: {e}")
        
        return results
    
    async def search(self, query: str, sources: Optional[List[str]] = None) -> List[SearchResult]:
        """
        Perform parallel search across multiple sources.
        
        Args:
            query: Raw search query
            sources: List of sources to search (default: all)
            
        Returns:
            Combined and ranked search results
        """
        # Check cache first
        query_hash = self._hash_query(query)
        if query_hash in self.cache:
            if self.debug:
                print(f"[Searcher] Cache hit for query: {query}")
            return self.cache[query_hash]
        
        # Optimize query
        optimized_query = self._optimize_query(query)
        
        # Determine which sources to search
        all_sources = ['stackoverflow', 'github', 'reddit', 'mdn']
        if sources:
            search_sources = [s for s in sources if s in all_sources]
        else:
            search_sources = all_sources
        
        if self.debug:
            print(f"[Searcher] Searching {search_sources} for: {optimized_query}")
        
        # Create search tasks
        tasks = []
        if 'stackoverflow' in search_sources:
            tasks.append(self._search_stackoverflow(optimized_query))
        if 'github' in search_sources:
            tasks.append(self._search_github(optimized_query))
        if 'reddit' in search_sources:
            tasks.append(self._search_reddit(optimized_query))
        if 'mdn' in search_sources:
            tasks.append(self._search_mdn(optimized_query))
        
        # Execute searches in parallel with progress tracking
        if self.debug:
            print(f"[Searcher] Starting parallel search across {len(tasks)} sources")
        
        results_lists = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            try:
                result_list = await task
                if isinstance(result_list, list) and result_list:
                    results_lists.append(result_list)
                    
                    # Show results as they arrive
                    if self.debug and result_list:
                        source = result_list[0].source if result_list else 'unknown'
                        print(f"[Searcher] ✓ {source}: {len(result_list)} results")
            except Exception as e:
                if self.debug:
                    print(f"[Searcher] Source failed: {e}")
                results_lists.append([])

        
        # Combine results
        all_results = []
        for results_list in results_lists:
            if isinstance(results_list, list):
                all_results.extend(results_list)
        
        # Rank results by source priority and score
        source_priority = {'stackoverflow': 4, 'mdn': 3, 'github': 2, 'reddit': 1}
        all_results.sort(
            key=lambda r: (source_priority.get(r.source, 0), r.score),
            reverse=True
        )
        
        # Limit to top 5 results total
        final_results = all_results[:5]
        
        # Cache results
        self.cache[query_hash] = final_results
        self.results = final_results
        
        # Save to cache file
        self._save_cache()
        
        if self.debug:
            print(f"[Searcher] Found {len(final_results)} total results")
        
        return final_results
    
    def _save_cache(self):
        """Save search results to JSON cache"""
        if not self.cache_path:
            # No cache path provided, skip caching
            return
        
        try:
            cache_data = {}
            for query_hash, results in self.cache.items():
                cache_data[query_hash] = [
                    {
                        'source': r.source,
                        'title': r.title,
                        'url': r.url,
                        'snippet': r.snippet,
                        'score': r.score,
                        'metadata': r.metadata
                    }
                    for r in results
                ]
            
            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            if self.debug:
                print(f"[Searcher] Cache saved to {self.cache_path}")
        except Exception as e:
            if self.debug:
                print(f"[Searcher] Failed to save cache: {e}")

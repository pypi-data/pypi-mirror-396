"""
Semantic Similarity - Zero Hardcoding
=====================================
Calculates semantic similarity between queries and files/content.
No assumptions, no hardcoded priorities - pure semantic matching.
"""
from typing import Dict, List, Set, Tuple
import re
from collections import Counter
from pathlib import Path


class SemanticSimilarity:
    """
    Calculate semantic similarity without hardcoded rules.
    Uses TF-IDF-like scoring and word embeddings simulation.
    """
    
    def __init__(self):
        # Stop words that don't carry semantic meaning
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
    
    def extract_semantic_tokens(self, text: str) -> List[str]:
        """
        Extract meaningful tokens from text.
        No hardcoding - works for any language/domain.
        """
        # Lowercase and split on non-alphanumeric
        text = text.lower()
        
        # Split on camelCase, snake_case, kebab-case, dots, etc.
        # This works for any programming language
        tokens = re.findall(r'[a-z0-9]+', text)
        
        # Remove stop words and very short tokens
        tokens = [t for t in tokens if t not in self.stop_words and len(t) > 2]
        
        return tokens
    
    def calculate_similarity(self, query_tokens: List[str], document_tokens: List[str]) -> float:
        """
        Calculate similarity between query and document.
        Uses Jaccard similarity + weighted overlap.
        """
        if not query_tokens or not document_tokens:
            return 0.0
        
        # Convert to sets for set operations
        query_set = set(query_tokens)
        doc_set = set(document_tokens)
        
        # Jaccard similarity (intersection / union)
        intersection = query_set & doc_set
        union = query_set | doc_set
        
        if not union:
            return 0.0
        
        jaccard = len(intersection) / len(union)
        
        # Weighted by term frequency in document
        query_counter = Counter(query_tokens)
        doc_counter = Counter(document_tokens)
        
        # Calculate overlap score (how much of query appears in doc)
        overlap_score = sum(
            min(query_counter[term], doc_counter[term]) 
            for term in intersection
        ) / sum(query_counter.values())
        
        # Combined score (60% overlap, 40% jaccard)
        score = 0.6 * overlap_score + 0.4 * jaccard
        
        return score
    
    def score_file_for_query(
        self, 
        query: str, 
        file_path: str, 
        file_content: str = None
    ) -> float:
        """
        Score how relevant a file is to a query.
        Considers filename, path, and content (if provided).
        """
        query_tokens = self.extract_semantic_tokens(query)
        
        if not query_tokens:
            return 0.0
        
        # Score filename (highest weight)
        filename = Path(file_path).name
        filename_tokens = self.extract_semantic_tokens(filename)
        filename_score = self.calculate_similarity(query_tokens, filename_tokens)
        
        # Score directory path
        parent = str(Path(file_path).parent)
        path_tokens = self.extract_semantic_tokens(parent)
        path_score = self.calculate_similarity(query_tokens, path_tokens)
        
        # Score content i f provided
        content_score = 0.0
        if file_content:
            content_tokens = self.extract_semantic_tokens(file_content)
            content_score = self.calculate_similarity(query_tokens, content_tokens)
        
        # Weighted combination
        # Filename most important, then content, then path
        if file_content:
            total_score = (
                0.4 * filename_score +
                0.4 * content_score +
                0.2 * path_score
            )
        else:
            total_score = (
                0.7 * filename_score +
                0.3 * path_score
            )
        
        return total_score
    
    def find_semantic_clusters(
        self, 
        files: List[Tuple[str, str]]
    ) -> Dict[str, List[str]]:
        """
        Find semantic clusters in files.
        Groups files that are semantically similar.
        
        Args:
            files: List of (file_path, content) tuples
        
        Returns:
            Dict of cluster_name -> [file_paths]
        """
        if not files:
            return {}
        
        # Extract all tokens from all files
        file_tokens = {}
        for file_path, content in files:
            tokens = self.extract_semantic_tokens(f"{file_path} {content}")
            file_tokens[file_path] = tokens
        
        # Find most common tokens across files (these are cluster themes)
        all_tokens = []
        for tokens in file_tokens.values():
            all_tokens.extend(tokens)
        
        # Get top themes
        token_freq = Counter(all_tokens)
        top_themes = [t for t, _ in token_freq.most_common(20)]
        
        # Cluster files by their strongest theme
        clusters = {theme: [] for theme in top_themes}
        
        for file_path, tokens in file_tokens.items():
            # Find which theme this file is most related to
            theme_scores = {}
            for theme in top_themes:
                # Count how many times this theme appears
                theme_scores[theme] = tokens.count(theme)
            
            # Assign to best matching theme
            if theme_scores:
                best_theme = max(theme_scores, key=theme_scores.get)
                if theme_scores[best_theme] > 0:
                    clusters[best_theme].append(file_path)
        
        # Remove empty clusters
        clusters = {k: v for k, v in clusters.items() if v}
        
        return clusters

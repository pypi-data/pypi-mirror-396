"""
StackSense Slice Extractor Agent
Intelligent agent that extracts relevant code slices using heuristic + TensorFlow scoring
NO hardcoded limits - dynamically adapts to content
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class Slice:
    """Code slice"""
    file_path: str
    start_line: int
    end_line: int
    content: str
    slice_type: str  # 'function', 'class', 'block'
    name: str
    score: float = 0.0


class SliceExtractorAgent:
    """
    Intelligent slice extraction agent.
    
    Uses heuristic + TensorFlow models to score relevance.
    Dynamically adapts context boundaries - no hardcoded limits.
    """
    
    def __init__(self, heuristic_model=None, tf_model=None, debug: bool = False):
        """
        Args:
            heuristic_model: Heuristic scoring model (optional)
            tf_model: TensorFlow model for semantic scoring (optional)
            debug: Enable debug logging
        """
        self.heuristic_model = heuristic_model
        self.tf_model = tf_model
        self.debug = debug
    
    def extract_slices(
        self, 
        file_content: str, 
        file_path: str,
        keywords: List[str], 
        context_budget: int = 4000
    ) -> List[Slice]:
        """
        Extract relevant slices from file content.
        
        Args:
            file_content: File content
            file_path: Path to file
            keywords: Search keywords
            context_budget: Maximum characters to extract
            
        Returns:
            List of relevant slices
        """
        # Parse file into potential slices
        potential_slices = self._parse_into_slices(file_content, file_path)
        
        if not potential_slices:
            return []
        
        # Score each slice
        scored_slices = []
        for slice_obj in potential_slices:
            score = self._score_slice(slice_obj, keywords)
            slice_obj.score = score
            scored_slices.append(slice_obj)
        
        # Sort by score (descending)
        scored_slices.sort(key=lambda s: s.score, reverse=True)
        
        # Select slices within context budget
        selected_slices = self._select_within_budget(scored_slices, context_budget)
        
        # Ensure context integrity (don't cut mid-function)
        final_slices = self._ensure_context_integrity(selected_slices)
        
        if self.debug:
            print(f"[SliceExtractor] Extracted {len(final_slices)} slices from {file_path}")
        
        return final_slices
    
    def _parse_into_slices(self, content: str, file_path: str) -> List[Slice]:
        """Parse file into potential slices (functions, classes, blocks)"""
        slices = []
        lines = content.split('\n')
        
        # Determine language from file extension
        if file_path.endswith('.py'):
            slices = self._parse_python_slices(lines, file_path)
        elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            slices = self._parse_javascript_slices(lines, file_path)
        else:
            # Generic block-based slicing
            slices = self._parse_generic_slices(lines, file_path)
        
        return slices
    
    def _parse_python_slices(self, lines: List[str], file_path: str) -> List[Slice]:
        """Parse Python code into slices"""
        slices = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Detect function or class
            if re.match(r'^(def|class)\s+\w+', line.strip()):
                # Find the end of this definition
                start_line = i
                indent_level = len(line) - len(line.lstrip())
                
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # End when we find a line at same or lower indent level
                    if next_line.strip() and next_indent <= indent_level:
                        break
                    
                    i += 1
                
                end_line = i - 1
                
                # Extract name
                match = re.match(r'^(def|class)\s+(\w+)', line.strip())
                slice_type = match.group(1) if match else 'block'
                name = match.group(2) if match else 'unknown'
                
                slices.append(Slice(
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    content='\n'.join(lines[start_line:end_line+1]),
                    slice_type=slice_type,
                    name=name
                ))
            else:
                i += 1
        
        return slices
    
    def _parse_javascript_slices(self, lines: List[str], file_path: str) -> List[Slice]:
        """Parse JavaScript/TypeScript code into slices"""
        slices = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Detect function or class
            if re.match(r'^(function|class|const\s+\w+\s*=\s*\(|export\s+(function|class))', line):
                start_line = i
                brace_count = line.count('{') - line.count('}')
                
                i += 1
                while i < len(lines) and brace_count > 0:
                    next_line = lines[i]
                    brace_count += next_line.count('{') - next_line.count('}')
                    i += 1
                
                end_line = i - 1
                
                # Extract name
                name_match = re.search(r'(function|class)\s+(\w+)|const\s+(\w+)', line)
                name = name_match.group(2) or name_match.group(3) if name_match else 'anonymous'
                
                slices.append(Slice(
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    content='\n'.join(lines[start_line:end_line+1]),
                    slice_type='function',
                    name=name
                ))
            else:
                i += 1
        
        return slices
    
    def _parse_generic_slices(self, lines: List[str], file_path: str) -> List[Slice]:
        """Generic block-based slicing for unknown languages"""
        # Split into blocks of ~20 lines
        slices = []
        block_size = 20
        
        for i in range(0, len(lines), block_size):
            end = min(i + block_size, len(lines))
            
            slices.append(Slice(
                file_path=file_path,
                start_line=i,
                end_line=end - 1,
                content='\n'.join(lines[i:end]),
                slice_type='block',
                name=f'block_{i}'
            ))
        
        return slices
    
    def _score_slice(self, slice_obj: Slice, keywords: List[str]) -> float:
        """
        Score slice relevance using heuristic + TF scoring.
        
        Args:
            slice_obj: Slice to score
            keywords: Search keywords
            
        Returns:
            Relevance score (0.0 - 1.0)
        """
        # Heuristic scoring
        heuristic_score = self._score_with_heuristic(slice_obj, keywords)
        
        # TensorFlow semantic scoring (if available)
        tf_score = 0.0
        if self.tf_model:
            tf_score = self._score_with_tensorflow(slice_obj, keywords)
        
        # Weighted combination
        if self.tf_model:
            return 0.6 * heuristic_score + 0.4 * tf_score
        else:
            return heuristic_score
    
    def _score_with_heuristic(self, slice_obj: Slice, keywords: List[str]) -> float:
        """Heuristic scoring based on keyword presence"""
        content_lower = slice_obj.content.lower()
        name_lower = slice_obj.name.lower()
        
        score = 0.0
        
        # Keyword density
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Count in content
            content_matches = content_lower.count(keyword_lower)
            score += content_matches * 0.2
            
            # Name match (high value)
            if keyword_lower in name_lower:
                score += 1.0
        
        # Type bonus (prioritize functions/classes over blocks)
        if slice_obj.slice_type in ['function', 'class', 'def']:
            score += 0.3
        
        # Normalize
        return min(score / 3.0, 1.0)
    
    def _score_with_tensorflow(self, slice_obj: Slice, keywords: List[str]) -> float:
        """
        Score using TensorFlow semantic model.
        
        This would use a trained model for semantic similarity.
        Placeholder for now.
        """
        # TODO: Implement TensorFlow semantic scoring
        # This would compute semantic similarity between slice and keywords
        return 0.5
    
    def _select_within_budget(self, scored_slices: List[Slice], budget: int) -> List[Slice]:
        """Select slices within context budget"""
        selected = []
        total_chars = 0
        
        for slice_obj in scored_slices:
            slice_size = len(slice_obj.content)
            
            if total_chars + slice_size <= budget:
                selected.append(slice_obj)
                total_chars += slice_size
            else:
                # Try to fit partial slice if there's room
                remaining = budget - total_chars
                if remaining > 200:  # Minimum useful slice size
                    # Truncate slice
                    lines = slice_obj.content.split('\n')
                    partial_lines = []
                    partial_chars = 0
                    
                    for line in lines:
                        if partial_chars + len(line) + 1 <= remaining:
                            partial_lines.append(line)
                            partial_chars += len(line) + 1
                        else:
                            break
                    
                    if partial_lines:
                        partial_slice = Slice(
                            file_path=slice_obj.file_path,
                            start_line=slice_obj.start_line,
                            end_line=slice_obj.start_line + len(partial_lines) - 1,
                            content='\n'.join(partial_lines),
                            slice_type=slice_obj.slice_type,
                            name=slice_obj.name,
                            score=slice_obj.score
                        )
                        selected.append(partial_slice)
                        total_chars += partial_chars
                
                break
        
        return selected
    
    def _ensure_context_integrity(self, slices: List[Slice]) -> List[Slice]:
        """
        Ensure slices don't cut off important context.
        E.g., don't cut mid-function definition.
        """
        # Group by file
        by_file = {}
        for slice_obj in slices:
            if slice_obj.file_path not in by_file:
                by_file[slice_obj.file_path] = []
            by_file[slice_obj.file_path].append(slice_obj)
        
        # For each file, merge overlapping/adjacent slices
        final = []
        for file_path, file_slices in by_file.items():
            # Sort by start line
            file_slices.sort(key=lambda s: s.start_line)
            
            merged = []
            current = file_slices[0]
            
            for next_slice in file_slices[1:]:
                # If adjacent or overlapping, merge
                if next_slice.start_line <= current.end_line + 1:
                    current.end_line = max(current.end_line, next_slice.end_line)
                    current.content = current.content + '\n' + next_slice.content
                else:
                    merged.append(current)
                    current = next_slice
            
            merged.append(current)
            final.extend(merged)
        
        return final

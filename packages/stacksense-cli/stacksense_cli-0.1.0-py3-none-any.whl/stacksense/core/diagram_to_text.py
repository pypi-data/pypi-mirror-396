"""
StackSense Diagram to Text Converter
Converts dependency diagrams to AI-readable text summaries
"""
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import asdict

from .diagram_builder import Diagram, Cluster


class DiagramToText:
    """
    Converts diagrams to concise AI-readable text.
    
    Different verbosity levels for different model sizes:
    - small: minimal, just structure
    - medium: includes key files and connections
    - large: full detail with all metadata
    """
    
    def __init__(self, verbosity: str = 'medium'):
        """
        Args:
            verbosity: 'small', 'medium', or 'large'
        """
        self.verbosity = verbosity
    
    def convert(self, diagram: Diagram, repo_name: str = "repository") -> str:
        """
        Convert diagram to text.
        
        Args:
            diagram: Diagram object
            repo_name: Name of repository
            
        Returns:
            AI-readable text summary
        """
        lines = [f"# {repo_name} Architecture Map\n"]
        
        # Overview
        lines.append(self._format_overview(diagram))
        
        # Entry points
        if diagram.metadata.get('entry_points'):
            lines.append(self._format_entry_points(diagram.metadata['entry_points']))
        
        # Languages
        if diagram.metadata.get('languages'):
            lines.append(self._format_languages(diagram.metadata['languages']))
        
        # Clusters (subsystems)
        if diagram.clusters:
            lines.append(self._format_clusters(diagram))
        
        # Hub files (highly connected)
        if diagram.metadata.get('hub_files'):
            lines.append(self._format_hub_files(diagram.metadata['hub_files'], diagram))
        
        return '\n'.join(lines)
    
    def _format_overview(self, diagram: Diagram) -> str:
        """Format overview section"""
        total_files = diagram.metadata.get('total_files', len(diagram.nodes))
        total_deps = len(diagram.edges)
        total_clusters = len(diagram.clusters)
        
        return f"""## Overview
- Files: {total_files}
- Dependencies: {total_deps}
- Subsystems: {total_clusters}
"""
    
    def _format_entry_points(self, entry_points: List[str]) -> str:
        """Format entry points section"""
        lines = ["## Entry Points"]
        
        for ep in entry_points[:5]:
            lines.append(f"- {ep}")
        
        return '\n'.join(lines) + '\n'
    
    def _format_languages(self, languages: List[str]) -> str:
        """Format languages section"""
        lang_str = ', '.join(languages)
        return f"## Languages\n{lang_str}\n"
    
    def _format_clusters(self, diagram: Diagram) -> str:
        """Format clusters (subsystems) section"""
        lines = ["## Subsystems\n"]
        
        max_clusters = {
            'small': 3,
            'medium': 5,
            'large': 10
        }.get(self.verbosity, 5)
        
        for cluster in diagram.clusters[:max_clusters]:
            lines.append(f"### {cluster.name}")
            lines.append(f"- Purpose: {cluster.purpose}")
            lines.append(f"- Files: {len(cluster.files)}")
            
            if self.verbosity in ['medium', 'large']:
                # Show key files
                key_files = cluster.files[:3]
                lines.append(f"- Key files:")
                for file in key_files:
                    lines.append(f"  - {file}")
                    
                    if self.verbosity == 'large':
                        # Show what this file imports
                        imports = self._get_file_imports(file, diagram)
                        if imports:
                            import_str = ', '.join(imports[:2])
                            lines.append(f"    → imports: {import_str}")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_hub_files(self, hub_files: List[str], diagram: Diagram) -> str:
        """Format hub files (central components)"""
        lines = ["## Key Components (Highly Connected)\n"]
        
        max_hubs = {
            'small': 3,
            'medium': 5,
            'large': 10
        }.get(self.verbosity, 5)
        
        for file in hub_files[:max_hubs]:
            connection_count = len(self._get_file_imports(file, diagram))
            lines.append(f"- {file}: {connection_count} connections")
        
        return '\n'.join(lines) + '\n'
    
    def _get_file_imports(self, file_path: str, diagram: Diagram) -> List[str]:
        """Get imports for a specific file"""
        imports = []
        for edge in diagram.edges:
            if edge['from'] == file_path:
                imports.append(edge['to'])
        return imports
    
    def convert_for_model_size(self, diagram: Diagram, repo_name: str, model_size: str) -> str:
        """
        Convert diagram with verbosity based on model size.
        
        Args:
            diagram: Diagram object
            repo_name: Repository name
            model_size: 'small', 'medium', or 'large'
            
        Returns:
            AI-readable text
        """
        old_verbosity = self.verbosity
        self.verbosity = model_size
        result = self.convert(diagram, repo_name)
        self.verbosity = old_verbosity
        return result

"""
Context Formatter
==================
Format extracted code into human-readable markdown for optimal AI comprehension.
AI models respond better to narrative prose than raw JSON.
"""
from typing import Dict, Any, List
import json


class ContextFormatter:
    """Transform structured context into AI-optimized markdown"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def format_for_model(self, context: Dict[str, Any], query: str = "") -> str:
        """
        Convert structured context into narrative markdown.
        
        Args:
            context: Context from context_builder
            query: User's question (for relevance hints)
        
        Returns:
            Markdown-formatted context string
        """
        sections = []
        
        # Header
        sections.append("# CODEBASE ANALYSIS\n")
        
        # 1. Tech Stack (concise)
        if context.get('frameworks'):
            sections.append(self._format_frameworks(context['frameworks']))
        
        # 2. Code Details (if deep context)
        if context.get('code_details'):
            sections.append(self._format_code_details(context['code_details']))
        
        # 3. Code Signatures (if signature context)
        elif context.get('code_signatures'):
            sections.append(self._format_signatures(context['code_signatures']))
        
        # 4. Module Overview
        if context.get('modules'):
            sections.append(self._format_modules(context['modules']))
        
        # 5. README (if available)
        if context.get('live_readme'):
            readme = context['live_readme']
            if len(readme) > 500:
                readme = readme[:500] + "..."
            sections.append(f"## Project Overview\n\n{readme}\n")
        
        formatted = "\n\n".join(sections)
        
        if self.debug:
            print(f"[Formatter] Generated {len(formatted)} chars of context")
        
        return formatted
    
    def _format_frameworks(self, frameworks: List[str]) -> str:
        """Format tech stack"""
        
        if not frameworks:
            return ""
        
        return f"**Tech Stack:** {', '.join(frameworks)}\n"
    
    def _format_code_details(self, code_details: Dict[str, Any]) -> str:
        """
        Format deep code details with CHOICES, fields, methods.
        This is the CRITICAL part for accuracy!
        """
        if not code_details:
            return ""
        
        output = ["## EXTRACTED CODE DETAILS\n"]
        
        for entity_name, details in code_details.items():
            entity_type = details.get('type', 'unknown')
            file_path = details.get('file', 'unknown')
            
            output.append(f"### {entity_name} ({entity_type})")
            output.append(f"**Source:** `{file_path}`\n")
            
            # CHOICES (Django models) - HIGHEST PRIORITY
            choices = details.get('choices', {})
            if choices:
                output.append("**CHOICES (Exact Values):**")
                for choice_name, choice_values in choices.items():
                    output.append(f"\n`{choice_name}`:")
                    
                    if isinstance(choice_values, list):
                        for choice_tuple in choice_values:
                            if isinstance(choice_tuple, (list, tuple)) and len(choice_tuple) >= 2:
                                code = choice_tuple[0]
                                label = choice_tuple[1]
                                output.append(f"  - `{code}`: {label}")
                    
                    output.append("")  # Spacing
            
            # Fields
            fields = details.get('fields', {})
            if fields:
                output.append("**Fields:**")
                for field_name, field_info in fields.items():
                    field_type = field_info.get('type', 'unknown')
                    output.append(f"  - `{field_name}`: {field_type}")
                    
                    # Show choices reference
                    if 'choices_ref' in field_info:
                        output.append(f"    (uses {field_info['choices_ref']})")
                
                output.append("")
            
            # Methods
            methods = details.get('methods', [])
            if methods:
                method_names = [m.get('name', 'unknown') if isinstance(m, dict) else m for m in methods]
                output.append(f"**Methods:** {', '.join(method_names[:10])}")
                if len(method_names) > 10:
                    output.append(f"  ... and {len(method_names) - 10} more")
                output.append("")
            
            # Docstring
            docstring = details.get('docstring')
            if docstring:
                # Limit docstring length
                if len(docstring) > 200:
                    docstring = docstring[:200] + "..."
                output.append(f"**Description:** {docstring}\n")
        
        return "\n".join(output)
    
    def _format_signatures(self, signatures: Dict[str, Any]) -> str:
        """Format code signatures (classes/functions overview)"""
        
        if not signatures:
            return ""
        
        output = ["## CODE STRUCTURE\n"]
        
        # Group by type
        classes = {name: sig for name, sig in signatures.items() if sig.get('type') == 'class'}
        functions = {name: sig for name, sig in signatures.items() if sig.get('type') == 'function'}
        
        if classes:
            output.append("**Classes:**")
            for name, sig in list(classes.items())[:20]:  # Limit to 20
                file = sig.get('file', '').split('/')[-1]  # Just filename
                methods = sig.get('methods', [])
                method_count = len(methods) if methods else 0
                output.append(f"  - `{name}` ({file}) - {method_count} methods")
            
            if len(classes) > 20:
                output.append(f"  ... and {len(classes) - 20} more classes")
            output.append("")
        
        if functions:
            output.append("**Functions:**")
            for name, sig in list(functions.items())[:15]:  # Limit to 15
                file = sig.get('file', '').split('/')[-1]
                params = sig.get('params', [])
                output.append(f"  - `{name}({', '.join(params[:3])})` ({file})")
            
            if len(functions) > 15:
                output.append(f"  ... and {len(functions) - 15} more functions")
            output.append("")
        
        return "\n".join(output)
    
    def _format_modules(self, modules: List[Dict[str, Any]]) -> str:
        """Format module summaries"""
        
        if not modules:
            return ""
        
        output = ["## MODULES\n"]
        
        for module in modules[:10]:  # Limit to 10 modules
            if isinstance(module, dict):
                name = module.get('name', 'Unknown')
                desc = module.get('description', '')
                features = module.get('key_features', [])
                
                output.append(f"**{name}**")
                if desc:
                    # Limit description
                    if len(desc) > 150:
                        desc = desc[:150] + "..."
                    output.append(f"  {desc}")
                
                if features:
                    output.append(f"  Key features: {', '.join(features[:3])}")
                
                output.append("")
        
        if len(modules) > 10:
            output.append(f"... and {len(modules) - 10} more modules")
        
        return "\n".join(output)


def format_context(context: Dict[str, Any], query: str = "", debug: bool = False) -> str:
    """
    Convenience function to format context.
    
    Args:
        context: Context dictionary
        query: User query
        debug: Enable debug output
    
    Returns:
        Formatted markdown string
    """
    formatter = ContextFormatter(debug=debug)
    return formatter.format_for_model(context, query)

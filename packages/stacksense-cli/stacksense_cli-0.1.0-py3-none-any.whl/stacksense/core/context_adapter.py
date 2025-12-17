"""
Context Adapter - Converts AdaptiveScanner output to ConversationalChat format
==============================================================================
Bridges the gap between new AdaptiveScanner and existing chat system.
"""
from typing import Dict, Any
from pathlib import Path


def adapt_shallow_scan_to_context(shallow_scan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert AdaptiveScanner shallow_scan output to the format expected by 
    ConversationalChatModel.
    
    Old format (from RepoScanner):
    {
        'modules': {...},
        'frameworks': [...],
        'languages': [...],
        'readme': '...'
    }
    
    New format (from AdaptiveScanner):
    {
        'file_index': {...},
        'frameworks': [...],
        'languages': [...],
        'readme_hints': '...',
        'entry_points': [...]
    }
    """
    
    # Extract basic info
    languages = shallow_scan.get('languages', [])
    frameworks = shallow_scan.get('frameworks', [])
    file_index = shallow_scan.get('file_index', {})
    readme = shallow_scan.get('readme_hints', '')
    entry_points = shallow_scan.get('entry_points', [])
    
    # Build modules dict from file index
    # Group files by directory to create "modules"
    modules = {}
    
    for file_path, metadata in file_index.items():
        # Get parent directory as module name
        parent = metadata.get('parent', '')
        
        if not parent or parent == '.':
            parent = 'root'
        
        # Group files by their parent directory
        if parent not in modules:
            modules[parent] = {
                'files': [],
                'description': f"Module: {parent}",
                'type': 'package'
            }
        
        modules[parent]['files'].append(file_path)
    
    # Create a PROMINENT tech stack summary at the top level
    tech_stack_summary = {
        'languages': languages,
        'frameworks': frameworks,
        'databases': [f for f in frameworks if any(db in f.lower() for db in ['redis', 'postgres', 'mongo', 'mysql', 'chroma', 'pinecone', 'faiss'])],
        'web_frameworks': [f for f in frameworks if any(w in f.lower() for w in ['fastapi', 'django', 'flask', 'express', 'next'])],
        'ai_ml': [f for f in frameworks if any(ai in f.lower() for ai in ['ollama', 'openai', 'anthropic', 'tensorflow', 'pytorch'])],
        'task_queues': [f for f in frameworks if any(tq in f.lower() for tq in ['celery', 'rq'])],
        'infrastructure': [f for f in frameworks if any(infra in f.lower() for infra in ['docker', 'kubernetes'])],
    }
    
    # Build framework description for context
    framework_desc = []
    if tech_stack_summary['web_frameworks']:
        framework_desc.append(f"Web: {', '.join(tech_stack_summary['web_frameworks'])}")
    if tech_stack_summary['databases']:
        framework_desc.append(f"Databases/Cache: {', '.join(tech_stack_summary['databases'])}")
    if tech_stack_summary['ai_ml']:
        framework_desc.append(f"AI/ML: {', '.join(tech_stack_summary['ai_ml'])}")
    if tech_stack_summary['task_queues']:
        framework_desc.append(f"Task Queues: {', '.join(tech_stack_summary['task_queues'])}")
    if tech_stack_summary['infrastructure']:
        framework_desc.append(f"Infrastructure: {', '.join(tech_stack_summary['infrastructure'])}")
    
    # Build prominent file listing for AI to reference
    # This helps AI cite specific files in responses
    prominent_files = []
    relevant_files = shallow_scan.get('relevant_files', [])
    
    if relevant_files:
        # Group by language/extension
        
        py_files = [f for f in relevant_files if f.endswith('.py')][:5]
        ts_files = [f for f in relevant_files if f.endswith(('.ts', '.tsx'))][:5]
        js_files = [f for f in relevant_files if f.endswith(('.js', '.jsx'))][:3]
        
        if py_files:
            prominent_files.append({
                'language': 'Python',
                'files': [{'path': f, 'name': Path(f).name} for f in py_files]
            })
        
        if ts_files:
            prominent_files.append({
                'language': 'TypeScript',
                'files': [{'path': f, 'name': Path(f).name} for f in ts_files]
            })
        
        if js_files:
            prominent_files.append({
                'language': 'JavaScript',
                'files': [{'path': f, 'name': Path(f).name} for f in js_files]
            })
    
    # Extract CODE CONTENT from query-specific extractions
    # THIS IS CRITICAL - gives AI actual content to reference!
    code_extractions = {}
    query_extractions = shallow_scan.get('query_specific_extractions', {})
    
    if query_extractions:
        for file_path, extraction_data in query_extractions.items():
            extraction = extraction_data.get('extraction', {})
            file_name = Path(file_path).name
            file_type = extraction.get('file_type', '')
            
            # DYNAMIC: Handle different file types appropriately
            code_extractions[file_name] = {
                'file': file_path,
                'type': file_type
            }
            
            # For markdown files - extract sections and preview
            if file_type in ['.md', '.markdown']:
                code_extractions[file_name]['content_type'] = 'documentation'
                code_extractions[file_name]['preview'] = extraction.get('preview', '')[:500]
                
                # Include sections for AI to reference
                sections = extraction.get('sections', {})
                if sections:
                    # LEVEL 1 FIX: Include ALL sections (no positional limit)
                    # Per-section truncation (800 chars) prevents context bloat
                    code_extractions[file_name]['sections'] = {}
                    for section_name, section_content in sections.items():
                        # Truncate long sections (keeps context manageable)
                        code_extractions[file_name]['sections'][section_name] = section_content[:800]
                    
                    # TODO (LEVEL 2): Implement semantic ranking using embeddings
                    # - Use Ollama's nomic-embed-text for free embeddings
                    # - Rank sections by cosine similarity to query
                    # - Select top N most relevant sections
                    # This would be more efficient than sending all sections
                
                # Include headings
                headings = extraction.get('headings', [])
                if headings:
                    # LEVEL 1 FIX: Include ALL headings (no limit)
                    code_extractions[file_name]['headings'] = [h.get('text', '') for h in headings]
            
            # For code files (Python/JS/TS) - extract functions and classes
            elif file_type in ['.py', '.js', '.jsx', '.ts', '.tsx']:
                code_extractions[file_name]['content_type'] = 'code'
                code_extractions[file_name]['functions'] = []
                code_extractions[file_name]['classes'] = []
                
                # LEVEL 1 FIX: Extract ALL functions (no limit)
                # Increased docstring limit to 300 chars for better context
                for func in extraction.get('functions', []):
                    code_extractions[file_name]['functions'].append({
                        'name': func.get('name', ''),
                        'signature': func.get('signature', ''),
                       'docstring': func.get('docstring', '')[:300] if func.get('docstring') else ''
                    })
                
                # LEVEL 1 FIX: Extract ALL classes (no limit)
                # Increased docstring limit to 300 chars for better context
                for cls in extraction.get('classes', []):
                    code_extractions[file_name]['classes'].append({
                        'name': cls.get('name', ''),
                        'methods': [m.get('name', '') for m in cls.get('methods', [])][:5],
                        'docstring': cls.get('docstring', '')[:300] if cls.get('docstring') else ''
                    })
                
                # Extract interfaces (for TypeScript)
                interfaces = extraction.get('interfaces', [])
                if interfaces:
                    # LEVEL 1 FIX: Include ALL interfaces (no limit)
                    code_extractions[file_name]['interfaces'] = [i.get('name', '') for i in interfaces]
            
            # For HTML files - extract structure
            elif file_type in ['.html', '.htm']:
                code_extractions[file_name]['content_type'] = 'markup'
                code_extractions[file_name]['title'] = extraction.get('title', '')
                code_extractions[file_name]['headings'] = [h.get('text', '') for h in extraction.get('headings', [])[:5]]
            
            # For config files - extract keys and preview
            elif file_type in ['.json', '.yaml', '.yml', '.toml']:
                code_extractions[file_name]['content_type'] = 'config'
                code_extractions[file_name]['keys'] = extraction.get('keys', [])[:10]
                code_extractions[file_name]['preview'] = extraction.get('preview', '')[:300]
            
            # Generic fallback for other files
            else:
                code_extractions[file_name]['content_type'] = 'text'
                code_extractions[file_name]['preview'] = extraction.get('preview', '')[:500]

    
    # Create adapted context with FRAMEWORKS FIRST
    adapted = {
        # Put frameworks at the top level for visibility
        'frameworks': frameworks,
        'languages': languages,
        
        # Add detailed tech stack
        'tech_stack': tech_stack_summary,
        'tech_stack_description': '; '.join(framework_desc) if framework_desc else 'No frameworks detected',
        
        # PROMINENTLY display relevant files for AI to cite
        'relevant_files_summary': prominent_files,
        
        # CRITICAL: Include actual code extractions!
        'code_extractions': code_extractions,
        
        # Modules
        'modules': modules,
        
        # README
        'readme': readme,
        
        # Additional metadata
        'entry_points': entry_points,
        
        # Keep original for reference
        '_original_scan': shallow_scan
    }
    
    return adapted

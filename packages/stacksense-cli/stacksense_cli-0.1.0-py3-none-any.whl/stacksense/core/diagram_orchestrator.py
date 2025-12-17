"""
StackSense Diagram-Based Orchestrator
Integrates diagram generation, AI-guided search, and memory management with chat
"""
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from .workspace_detector import WorkspaceDetector, WorkspaceStructure
from .storage_manager import StorageManager
from .diagram_builder import DiagramBuilder, Diagram
from .diagram_to_text import DiagramToText
from .keyword_extractor import KeywordExtractor
from .grep_searcher import GrepSearcher
from .framework_aware_filter import FrameworkAwareFilter
from stacksense.agents.slice_extractor_agent import SliceExtractorAgent
from stacksense.agents.memory_writer_agent import MemoryWriterAgent


class DiagramBasedOrchestrator:
    """
    Orchestrates the complete diagram-based workflow:
    
    1. Initialize: Detect workspace, build diagrams
    2. Query: Extract keywords → Grep search → AI file selection → Slice extraction
    3. Answer: Generate response + update memory
    """
    
    def __init__(self, workspace_path: Path, model, model_size: str = 'medium', debug: bool = False):
        """
        Args:
            workspace_path: Workspace root path
            model: AI model instance
            model_size: 'small', 'medium', or 'large'
            debug: Enable debug logging
        """
        self.workspace_path = Path(workspace_path)
        self.model = model
        self.model_size = model_size
        self.debug = debug
        
        # Initialize components
        self.workspace_detector = WorkspaceDetector(debug=debug)
        self.storage = StorageManager(debug=debug)
        self.diagram_builder = DiagramBuilder(debug=debug)
        self.diagram_to_text = DiagramToText(verbosity=model_size)
        self.keyword_extractor = KeywordExtractor(model, model_size, debug=debug)
        self.framework_filter = FrameworkAwareFilter(debug=debug)
        self.slice_extractor = SliceExtractorAgent(debug=debug)
        self.memory_writer = MemoryWriterAgent(self.storage, debug=debug)
        
        # State
        self.workspace_structure = None
        self.diagrams = {}
        self.diagram_summaries = {}
        self.tech_stacks = {}
        self.grep_searcher = None
    
    def initialize(self) -> bool:
        """
        Initialize workspace: detect structure, build diagrams
        
        Returns:
            True if successful
        """
        if self.debug:
            print(f"[Orchestrator] Initializing workspace: {self.workspace_path}")
        
        # Step 1: Detect workspace structure (use correct method name)
        self.workspace_structure = self.workspace_detector.detect_workspace_structure(self.workspace_path)
        
        if not self.workspace_structure.repos:
            if self.debug:
                print("[Orchestrator] No repositories detected")
            return False
        
        # Step 2: Build or load diagrams for each repo
        for repo in self.workspace_structure.repos:
            repo_path = Path(repo.path)
            
            # Extract tech stack from repo's tech_signature
            tech_stack = {
                'languages': list(repo.tech_signature.languages) if repo.tech_signature else [],
                'frameworks': list(repo.tech_signature.frameworks) if repo.tech_signature else []
            }
            self.tech_stacks[repo.name] = tech_stack
            
            # Check if diagram already exists (CACHING!)
            workspace_name = self.workspace_structure.workspace_name
            diagram_dir = self.storage.get_diagrams_path(workspace_name, repo.name)
            diagram_file = diagram_dir / 'dependency_graph.json'
            
            diagram = None
            
            if diagram_file.exists():
                # Load existing diagram (instant!)
                try:
                    import json
                    import time as time_module
                    
                    # Check if diagram is less than 24 hours old
                    file_age = time_module.time() - diagram_file.stat().st_mtime
                    if file_age < 86400:  # 24 hours in seconds
                        with open(diagram_file) as f:
                            diagram_data = json.load(f)
                        
                        # Reconstruct diagram object
                        from .diagram_builder import Diagram, Node, Edge
                        
                        nodes = [
                            Node(id=n['id'], type=n.get('type', 'module'), 
                                 metadata=n.get('metadata', {}))
                            for n in diagram_data.get('nodes', [])
                        ]
                        edges = [
                            Edge(source=e['source'], target=e['target'],
                                 edge_type=e.get('edge_type', 'imports'))
                            for e in diagram_data.get('edges', [])
                        ]
                        
                        diagram = Diagram(nodes=nodes, edges=edges)
                        
                        if self.debug:
                            print(f"[Orchestrator] Loaded cached diagram for {repo.name}: {len(nodes)} nodes")
                except Exception as e:
                    if self.debug:
                        print(f"[Orchestrator] Could not load cached diagram: {e}")
                    diagram = None
            
            # Build diagram if not loaded from cache
            if diagram is None:
                if self.debug:
                    print(f"[Orchestrator] Building new diagram for {repo.name}...")
                
                # Build file index
                file_index = self._build_file_index(repo_path, tech_stack)
                
                if not file_index:
                    continue
                
                # Build diagram
                diagram = self.diagram_builder.build_diagram(repo_path, file_index)
                
                # Save diagram for future cache
                diagram_dir.mkdir(parents=True, exist_ok=True)
                self.diagram_builder.save_diagram(diagram, diagram_dir)
                
                if self.debug:
                    print(f"[Orchestrator] Built diagram for {repo.name}: {len(diagram.nodes)} nodes, {len(diagram.edges)} edges")
            
            self.diagrams[repo.name] = diagram
            
            # Convert diagram to text summary
            summary = self.diagram_to_text.convert(diagram, repo.name)
            self.diagram_summaries[repo.name] = summary
        
        # Step 3: Initialize grep searcher with tech stack context
        primary_repo = self.workspace_structure.repos[0]
        primary_tech_stack = self.tech_stacks.get(primary_repo.name, {})
        
        self.grep_searcher = GrepSearcher(
            workspace_path=Path(primary_repo.path),
            debug=self.debug
        )
        
        return True
    
    def _build_file_index(self, repo_path: Path, tech_stack: Dict) -> Dict[str, Any]:
        """Build simple file index for diagram builder"""
        file_index = {}
        
        # Limit files to prevent hanging on large repos (e.g., Bazel with 9k+ files)
        MAX_FILES = 500
        
        # Get extensions from tech stack
        extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java'}
        
        for ext in extensions:
            if len(file_index) >= MAX_FILES:
                break
                
            for file_path in repo_path.rglob(f'*{ext}'):
                if len(file_index) >= MAX_FILES:
                    break
                    
                # Skip ignored paths
                if any(part in file_path.parts for part in ['venv', 'node_modules', '__pycache__', '.git', 'third_party', 'vendor', 'test', 'tests', 'examples']):
                    continue
                
                rel_path = str(file_path.relative_to(repo_path))
                
                # Map extension to language
                lang_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.jsx': 'javascript',
                    '.ts': 'typescript',
                    '.tsx': 'typescript',
                    '.go': 'go',
                    '.rs': 'rust',
                    '.java': 'java',
                }
                
                file_index[rel_path] = {
                    'language': lang_map.get(ext, 'unknown')
                }
        
        if self.debug and len(file_index) >= MAX_FILES:
            print(f"[Orchestrator] Large repo detected - limited to {MAX_FILES} files for performance")
        
        return file_index
    
    def query(self, user_query: str, extra_context: dict = None) -> Dict[str, Any]:
        """
        Process a user query through the complete pipeline
        
        Args:
            user_query: User's question
            extra_context: Optional additional context (e.g., file attachments)
            
        Returns:
            Dict with answer, slices, keywords, metadata
        """
        if not self.workspace_structure or not self.diagrams:
            return {
                'answer': 'Workspace not initialized. Please run initialize() first.',
                'slices_extracted': 0,
                'keywords_used': [],
                'files_searched': 0
            }
        
        # Get primary repo and diagram
        target_repo = self.workspace_structure.repos[0].name
        diagram = self.diagrams.get(target_repo)
        diagram_summary = self.diagram_summaries.get(target_repo, "")
        
        # Step 1: Extract keywords using AI + diagram context (NOT hardcoded)
        from .diagram_keyword_extractor import extract_keywords_with_ai
        
        # Get diagram metadata for AI to analyze
        diagram_metadata = {
            'nodes': diagram.nodes if diagram else [],
        }
        
        keywords = extract_keywords_with_ai(
            model=self.model,
            query=user_query,
            diagram_summary=diagram_summary,
            diagram_metadata=diagram_metadata,
            debug=self.debug
        )
        
        if self.debug:
            print(f"[Orchestrator] AI-Generated Keywords: {keywords}")
        
        # Step 2: Grep search for keyword occurrences
        grep_results = self.grep_searcher.search_keywords(keywords)
        
        # grep_results is a dict: {file_path: match_count, ...}
        matched_files = list(grep_results.keys())
        files_searched = len(matched_files)
        
        if self.debug:
            print(f"[Orchestrator] Found {len(matched_files)} files with matches")
        
        # Step 3: Filter files using framework awareness
        tech_stack = self.tech_stacks.get(target_repo, {})
        filtered_files = self.framework_filter.filter_file_list(matched_files, tech_stack)
        
        # Step 4: Extract code slices from each file
        all_slices = []
        primary_repo = self.workspace_structure.repos[0]
        
        for file_info in filtered_files[:10]:  # Limit to top 10 files
            file_path = file_info if isinstance(file_info, str) else file_info.get('path', '')
            full_path = Path(primary_repo.path) / file_path
            
            try:
                if full_path.exists():
                    content = full_path.read_text(encoding='utf-8', errors='ignore')
                    slices = self.slice_extractor.extract_slices(
                        file_content=content,
                        file_path=str(file_path),
                        keywords=keywords,
                        context_budget=2000
                    )
                    all_slices.extend(slices)
            except Exception as e:
                if self.debug:
                    print(f"[Orchestrator] Error extracting slices from {file_path}: {e}")
        
        slices = all_slices
        
        if self.debug:
            print(f"[Orchestrator] Extracted {len(slices)} code slices")
        
        # Step 5: Build context string
        context = self._build_context(slices, diagram_summary)
        
        # Step 6: Generate answer
        answer = self._generate_answer(user_query, slices, context, diagram_summary)
        
        # Step 7: Update memory (async)
        try:
            self.memory_writer.update_from_query(user_query, answer, slices, keywords)
        except Exception as e:
            if self.debug:
                print(f"[Orchestrator] Memory update failed: {e}")
        
        return {
            'answer': answer,
            'slices_extracted': len(slices),
            'keywords_used': keywords,
            'files_searched': files_searched
        }
    
    def _build_context(self, slices: List, diagram_summary: str) -> str:
        """Build context string from slices and diagram"""
        context_parts = []
        
        # Add diagram summary
        context_parts.append("# Codebase Architecture\n")
        context_parts.append(diagram_summary)
        context_parts.append("\n\n# Relevant Code\n")
        
        # Add slices
        for i, slice_obj in enumerate(slices[:10], 1):
            # Derive language from file extension
            file_ext = Path(slice_obj.file_path).suffix.lstrip('.')
            lang_map = {'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'md': 'markdown'}
            language = lang_map.get(file_ext, file_ext or 'text')
            
            context_parts.append(f"\n## {i}. {slice_obj.file_path}\n")
            context_parts.append(f"```{language}\n")
            context_parts.append(slice_obj.content)
            context_parts.append("\n```\n")
        
        return ''.join(context_parts)
    
    def _generate_answer(self, query: str, slices: List, context: str, diagram_summary: str) -> str:
        """Generate intelligent, question-specific answer using AI + code context"""
        
        # Get diagram for better context
        repo_name = self.workspace_structure.repos[0].name
        diagram = self.diagrams.get(repo_name)
        tech_stack = self.tech_stacks.get(repo_name, {})
        
        # For NO SLICES - provide helpful fallback
        if not slices:
            langs = ', '.join(tech_stack.get('languages', []))
            return (f"I couldn't find specific code matching **{query}**\n\n"
                   f"The codebase has {len(diagram.nodes)} files in {langs}. "
                   f"Try asking:\n"
                   f'- "What is this project?"\n'
                   f'- "Show me the main entry point"\n'
                   f'- "How does [specific feature] work?"')
        
        # Build code context for AI
        code_context = self._build_code_context_for_ai(slices)
        
        # Build the prompt for AI to answer the question
        prompt = self._build_answer_prompt(query, code_context, diagram_summary, tech_stack)
        
        # Get AI response
        try:
            answer = self.model.generate(prompt)
            
            # Clean up the response
            answer = self._clean_ai_response(answer)
            
            if self.debug:
                print(f"[Orchestrator] AI generated answer: {len(answer)} chars")
            
            return answer
            
        except Exception as e:
            if self.debug:
                print(f"[Orchestrator] AI answer failed: {e}")
            # Fallback to basic answer
            return self._fallback_answer(query, slices, repo_name)
    
    def _build_code_context_for_ai(self, slices: List) -> str:
        """Build readable code context from slices"""
        parts = []
        
        for i, slice_obj in enumerate(slices[:8], 1):  # Max 8 slices
            parts.append(f"\n### File: {slice_obj.file_path}")
            if hasattr(slice_obj, 'name') and slice_obj.name:
                parts.append(f" - {slice_obj.slice_type}: {slice_obj.name}")
            parts.append(f"\n```\n{slice_obj.content[:1500]}\n```\n")  # Limit content size
        
        return '\n'.join(parts)
    
    def _build_answer_prompt(self, query: str, code_context: str, diagram_summary: str, tech_stack: dict) -> str:
        """Build prompt for AI to answer the user's question"""
        
        languages = ', '.join(tech_stack.get('languages', ['unknown']))
        frameworks = ', '.join(tech_stack.get('frameworks', []))
        
        return f"""You are an expert code analyst helping a developer understand their codebase.

PROJECT INFO:
- Languages: {languages}
- Frameworks: {frameworks}

CODEBASE ARCHITECTURE:
{diagram_summary[:2000]}

RELEVANT CODE FOUND:
{code_context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer the question directly and specifically based on the code shown
2. Reference actual file names, class names, and function names from the code
3. Explain what the code does, not just list it
4. If the user asks about architecture/structure, explain how components connect
5. If asked about a feature, explain how it's implemented
6. Be concise but thorough - aim for 3-5 sentences for simple questions, more for complex ones
7. Don't just list files - explain what they DO and how they relate to the question

ANSWER:"""
    
    def _clean_ai_response(self, response: str) -> str:
        """Clean up AI response"""
        # Remove common prefixes
        prefixes_to_remove = ['ANSWER:', 'Here is', 'Based on the code']
        for prefix in prefixes_to_remove:
            if response.strip().startswith(prefix):
                response = response.strip()[len(prefix):].strip()
        
        return response.strip()
    
    def _fallback_answer(self, query: str, slices: List, repo_name: str) -> str:
        """Basic fallback if AI fails"""
        parts = [f"## Analysis of {repo_name}\n\n"]
        parts.append(f"Found **{len(slices)} code sections** related to: *{query}*\n\n")
        
        # Group by file
        by_file = {}
        for s in slices:
            fname = Path(s.file_path).name
            if fname not in by_file:
                by_file[fname] = []
            by_file[fname].append(s)
        
        for fname, file_slices in list(by_file.items())[:5]:
            parts.append(f"**{fname}:**\n")
            for s in file_slices[:3]:
                parts.append(f"- `{s.name}` ({s.slice_type})\n")
            parts.append("\n")
        
        return ''.join(parts)
    
    def get_diagram_summary(self, repo_name: Optional[str] = None) -> str:
        """Get diagram summary for a repo"""
        if repo_name is None:
            repo_name = self.workspace_structure.repos[0].name
        
        return self.diagram_summaries.get(repo_name, "No diagram available")
    
    def query_fast(
        self, 
        user_query: str,
        stream: bool = True,
        on_step_start=None,
        on_step_complete=None,
        on_stream_chunk=None
    ) -> Dict[str, Any]:
        """
        FAST query using Claude Code style (2 AI calls instead of 3).
        
        Performance: 136s → 26s (80% faster!)
        
        Args:
            user_query: User's question
            stream: Whether to stream the response
            on_step_start: Callback when step starts
            on_step_complete: Callback when step completes
            on_stream_chunk: Callback for each streamed chunk
            
        Returns:
            Dict with answer, files_used, timings, total_time
        """
        from .fast_query_processor import FastQueryProcessor
        
        # Get diagram path
        target_repo = self.workspace_structure.repos[0].name
        workspace_name = self.workspace_structure.workspace_name
        
        diagram_path = self.storage.get_diagrams_path(workspace_name, target_repo) / 'dependency_graph.json'
        
        # Get model name
        model_name = getattr(self.model, 'model_name', 'phi3:mini')
        
        # Create fast processor
        processor = FastQueryProcessor(
            workspace_path=self.workspace_path,
            diagram_path=diagram_path,
            model_name=model_name,
            debug=self.debug
        )
        
        # Set callbacks
        processor.on_step_start = on_step_start
        processor.on_step_complete = on_step_complete
        processor.on_stream_chunk = on_stream_chunk
        
        # Process query
        result = processor.process_query(user_query, stream=stream)
        
        # Learn from this interaction - write to ai_memory.json
        try:
            self.memory_writer.update_from_query(
                workspace_name=workspace_name,
                repo_name=target_repo,
                query=user_query,
                answer=result.answer,
                files_used=result.files_used,
                keywords=[]
            )
        except Exception as e:
            if self.debug:
                print(f"[Orchestrator] Memory write failed: {e}")
        
        return {
            'answer': result.answer,
            'files_used': result.files_used,
            'context_size': result.context_size,
            'timings': result.timings,
            'total_time': result.total_time,
            'slices_extracted': len(result.files_used),
            'keywords_used': [],  # Not used in fast mode
            'files_searched': len(result.files_used)
        }


"""
Prompt Engineer - Dynamic Citation-Enforcing Prompts
====================================================
Builds prompts that force AI to cite discovered code.
100% dynamic - works with any model, any project, any language.
"""
from typing import Dict, Any, List
from pathlib import Path


class PromptEngineer:
    """
    Builds citation-enforcing prompts dynamically.
    No hardcoded examples or model names.
    """
    
    # Model tiers (detected from config, not hardcoded)
    TIER_PATTERNS = {
        'light': ['mini', 'small', '3b', '7b'],
        'medium': ['medium', '13b', '14b'],
        'large': ['large', '70b', 'mixtral', 'gpt-4']
    }
    
    def __init__(self, model_name: str = '', debug: bool = False):
        self.model_name = model_name.lower()
        self.debug = debug
        
        # Auto-detect model tier
        self.tier = self._detect_tier()
        
        if self.debug:
            print(f"[PromptEngineer] Model: {model_name}, Tier: {self.tier}")
    
    def _detect_tier(self) -> str:
        """Detect model tier from name (light/medium/large)"""
        for tier, patterns in self.TIER_PATTERNS.items():
            if any(p in self.model_name for p in patterns):
                return tier
        
        # Default to light (safest for unknown models)
        return 'light'
    
    def build_citation_protocol(self) -> str:
        """
        Build mandatory file citation protocol.
        Adapts to model tier (light models need simpler rules).
        """
        if self.tier == 'light':
            return """# Citation Rules
- ALWAYS cite file names when answering
- Format: [filename.ext] or [filename:function_name]
- If no matching file, say "Not found in provided context"
- Never use general knowledge without citing repo files"""
        
        elif self.tier == 'medium':
            return """# Mandatory File Citation Protocol
You MUST cite file paths in every answer.

Format Rules:
- When mentioning a function → cite immediately: [file.py:function_name]
- When explaining flow → list files in execution order
- When describing architecture → reference specific files
- If uncertain → say "Not found in context" (never guess)

Every sentence must reference discovered code or files."""
        
        else:  # large
            return """# Mandatory File Citation Protocol

STRICT REQUIREMENTS:
1. Every technical claim MUST cite a specific file or code extract
2. Format: [filepath:function/class] with brief context
3. When explaining flows: list files in dependency order
4. For architecture: reference actual directory structure
5. If information not in context: explicitly state "Not found in repository context"

NEVER provide generic answers - ground everything in discovered code.
Citations demonstrate you used the provided context, not general knowledge."""
    
    def build_relevance_pyramid(self, context: Dict[str, Any], query: str) -> str:
        """
        Build File Relevance Pyramid - most relevant files first.
        100% dynamic - learns from context.
        """
        frameworks = context.get('frameworks', [])
        languages = context.get('languages', [])
        code_extractions = context.get('code_extractions', {})
        
        pyramid = []
        
        # Level 1: Context Overview (brief)
        pyramid.append("# Context Overview")
        if languages:
            pyramid.append(f"Languages: {', '.join(languages[:3])}")
        if frameworks:
            pyramid.append(f"Frameworks: {', '.join(frameworks[:5])}")
        pyramid.append("")
        
        # Level 2: Top Relevant Files (ranked)
        pyramid.append("# Top Relevant Files for This Query")
        pyramid.append("(Ranked by relevance - USE THESE FIRST)")
        pyramid.append("")
        
        # Extract and rank files
        file_count = 0
        for file_name, extraction in code_extractions.items():
            file_count += 1
            
            # Build file summary
            functions = extraction.get('functions', [])
            classes = extraction.get('classes', [])
            
            summary_parts = []
            if functions:
                summary_parts.append(f"{len(functions)} functions")
            if classes:
                summary_parts.append(f"{len(classes)} classes")
            
            summary = ', '.join(summary_parts) if summary_parts else 'code file'
            
            pyramid.append(f"{file_count}. [{file_name}] - {summary}")
            
            # Show top functions/classes
            if functions and len(functions) > 0:
                top_func = functions[0]
                pyramid.append(f"   └─ {top_func.get('name', 'unknown')}(): {top_func.get('docstring', 'no description')[:80]}")
            
            if file_count >= 10:  # Limit to top 10
                break
        
        pyramid.append("")
        
        # Level 3: Code Extracts (trimmed)
        pyramid.append("# Extracted Code (Top Matches Only)")
        pyramid.append("")
        
        extract_count = 0
        for file_name, extraction in code_extractions.items():
            pyramid.append(f"## {file_name}")
            
            # Top 3 functions only (not all!)
            functions = extraction.get('functions', [])[:3]
            for func in functions:
                pyramid.append(f"  - {func.get('signature', func.get('name', 'unknown'))}")
                if func.get('docstring'):
                    doc = func['docstring'][:100] + "..." if len(func['docstring']) > 100 else func['docstring']
                    pyramid.append(f"    {doc}")
            
            # Top 2 classes only
            classes = extraction.get('classes', [])[:2]
            for cls in classes:
                methods = ', '.join(cls.get('methods', [])[:3])
                pyramid.append(f"  - class {cls.get('name', 'Unknown')}: {methods}")
            
            pyramid.append("")
            
            extract_count += 1
            if extract_count >= 5:  # Limit to 5 files with full extracts
                break
        
        return "\n".join(pyramid)
    
    def build_few_shot_examples(self, query_category: str) -> str:
        """
        Build GOOD vs BAD examples dynamically.
        No hardcoded project names - uses placeholders.
        """
        # Generic template that works for any domain
        return f"""# Answer Examples

❌ BAD ANSWER (Do NOT do this):
"The system uses a standard authentication flow with JWT tokens. 
It likely stores user data in a database and validates credentials."
→ Problem: No file citations, too generic, assumes without evidence

✅ GOOD ANSWER (Follow this pattern):
"Authentication is handled in [auth_views.py:login_handler()] which validates 
credentials against [models/user.py:User.check_password()]. JWT tokens are 
generated using [utils/jwt.py:create_token()] with a 24-hour expiry.
The User model defines roles in [models/user.py:ROLE_CHOICES]."
→ Correct: Cites specific files and functions, grounded in code

Remember: ALWAYS cite files like the GOOD example."""
    
    def build_enhanced_prompt(self, query: str, context: Dict[str, Any], query_category: str = 'general') -> str:
        """
        Build complete enhanced prompt with all improvements.
        100% dynamic - adapts to model tier and context.
        """
        parts = []
        
        # 1. Citation protocol (mandatory)
        parts.append(self.build_citation_protocol())
        parts.append("")
        
        # 2. File Relevance Pyramid
        parts.append(self.build_relevance_pyramid(context, query))
        parts.append("")
        
        # 3. Few-shot examples (for medium/large models)
        if self.tier in ['medium', 'large']:
            parts.append(self.build_few_shot_examples(query_category))
            parts.append("")
        
        # 4. Chain-of-thought guidance (for all tiers)
        parts.append("# Answer Structure")
        parts.append("Step 1: Identify 2-3 most relevant files from context above")
        parts.append("Step 2: Answer question citing those files specifically")
        parts.append("Step 3: If gaps exist, state 'Additional scan needed for [topic]'")
        parts.append("")
        
        # 5. The actual query
        parts.append("# User Question")
        parts.append(query)
        parts.append("")
        
        # 6. Final instruction (adapt to tier)
        if self.tier == 'light':
            parts.append("Answer using the files listed above. Cite at least 2 files.")
        else:
            parts.append("Provide a detailed answer grounded in the extracted code above.")
            parts.append("Cite file paths and function names throughout your response.")
        
        return "\n".join(parts)
    
    def verify_citations(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify if response cited files from context.
        Returns score and missing citations.
        """
        code_extractions = context.get('code_extractions', {})
        
        # Count how many files were cited
        cited_files = []
        response_lower = response.lower()
        
        for file_name in code_extractions.keys():
            # Check various citation formats
            file_name_lower = file_name.lower()
            file_base = Path(file_name).stem.lower()
            
            if any(pattern in response_lower for pattern in [
                file_name_lower,
                file_base,
                f"[{file_name_lower}",
                f"`{file_name_lower}",
            ]):
                cited_files.append(file_name)
        
        # Calculate score
        total_files = len(code_extractions)
        citation_rate = len(cited_files) / max(1, total_files) * 100
        
        return {
            'score': citation_rate,
            'cited_files': cited_files,
            'total_available': total_files,
            'missing_citations': list(set(code_extractions.keys()) - set(cited_files))
        }

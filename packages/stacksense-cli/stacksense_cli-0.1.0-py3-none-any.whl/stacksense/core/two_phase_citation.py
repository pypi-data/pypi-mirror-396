"""
Two-Phase Citation System
=========================
Phase 1: File selection (simple task for small models)
Phase 2: Answer generation (compact context, fewer files)

This splits the complex task into manageable chunks.
"""
from typing import Dict, Any, List
from pathlib import Path
import re


class TwoPhaseCitationSystem:
    """
    Two-phase approach to boost citation accuracy on small models.
    
    Phase 1: Select 3-5 most relevant files (simple selection task)
    Phase 2: Answer using ONLY those files (reduced context)
    """
    
    def __init__(self, model_name: str = 'phi3:mini', debug: bool = False):
        self.model_name = model_name
        self.debug = debug
        
        # Detect model size for dynamic prompting
        self.model_size = self._detect_model_size(model_name)
        
        if self.debug:
            print(f"[TwoPhase] Model: {model_name}, Size: {self.model_size}")
    
    def _detect_model_size(self, model_name: str) -> str:
        """
        Detect model size from name.
        Returns: 'small' (<7B), 'medium' (7-14B), 'large' (>14B)
        """
        name_lower = model_name.lower()
        
        # Small models (< 7B)
        if any(x in name_lower for x in ['mini', '3b', '4b']):
            return 'small'
        
        # Large models (> 14B)
        elif any(x in name_lower for x in ['13b', '14b', '20b', '30b', '70b', 'mixtral', 'gpt']):
            return 'large'
        
        # Medium models (7-14B)
        elif any(x in name_lower for x in ['7b', '8b', '9b']):
            return 'medium'
        
        # Default to medium for unknown
        return 'medium'
    
    def build_file_selection_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """
        Phase 1: Simple prompt to select relevant files.
        Same for all model sizes (task is already simple).
        """
        # Get available files
        code_extractions = context.get('code_extractions', {})
        
        if not code_extractions:
            return ""
        
        # Build simple numbered list
        file_list = []
        for i, (file_name, extraction) in enumerate(code_extractions.items(), 1):
            functions = extraction.get('functions', [])
            classes = extraction.get('classes', [])
            
            desc_parts = []
            if functions:
                desc_parts.append(f"{len(functions)} functions")
            if classes:
                desc_parts.append(f"{len(classes)} classes")
            
            desc = ', '.join(desc_parts) if desc_parts else 'code file'
            file_list.append(f"{i}. {file_name} - {desc}")
        
        prompt = f"""You have these files:

{chr(10).join(file_list)}

Question: {query}

Task: Pick the 3-5 MOST relevant files to answer this question.
Output ONLY the numbers, comma-separated.

Example: 1,3,5

Your answer:"""
        
        return prompt
    
    def parse_file_selection(self, response: str, available_files: List[str]) -> List[str]:
        """Parse file selection response and return selected file names"""
        # Extract numbers
        numbers = re.findall(r'\d+', response)
        
        selected_files = []
        for num_str in numbers:
            try:
                index = int(num_str) - 1  # Convert to 0-indexed
                if 0 <= index < len(available_files):
                    selected_files.append(available_files[index])
            except ValueError:
                continue
        
        # Limit to 5 files max
        return selected_files[:5]
    
    def build_compact_context(self, selected_files: List[str], full_context: Dict[str, Any]) -> str:
        """
        Build COMPACT context with only selected files.
        Names only, no verbose docstrings.
        """
        code_extractions = full_context.get('code_extractions', {})
        
        output = []
        
        for file_name in selected_files:
            if file_name not in code_extractions:
                continue
            
            extraction = code_extractions[file_name]
            output.append(f"\n[{file_name}]:")
            
            # Just list function names
            functions = extraction.get('functions', [])
            if functions:
                func_names = [f['name'] for f in functions[:3]]  # Top 3 only
                output.append(f"  Functions: {', '.join(func_names)}")
            
            # Just list class names
            classes = extraction.get('classes', [])
            if classes:
                class_names = [c['name'] for c in classes[:2]]  # Top 2 only
                output.append(f"  Classes: {', '.join(class_names)}")
        
        return "\n".join(output)
    
    def build_mcp_answer_prompt(self, query: str, selected_files: List[str], compact_context: str) -> str:
        """
        Phase 2: Build Mandatory Citation Protocol (MCP) prompt.
        ADAPTS to model size - stricter for larger models!
        """
        file_list = ', '.join(selected_files)
        
        if self.model_size == 'small':
            # Light prompt for small models (already working at 100%)
            return f"""MANDATORY CITATION PROTOCOL (MCP):

YOU MUST CITE FILES IN EVERY SENTENCE.

Files you MUST reference:
{file_list}

Code details:
{compact_context}

Question: {query}

RULES:
1. START with: "Based on [filename], ..."
2. Use [filename] when referencing code
3. Cite at least 1 file per sentence
4. If unsure, say "Not found in provided files"

Example:
✅ GOOD: "Authentication is handled in [auth_views.py] using the login() function"
❌ BAD: "The system uses authentication" (no file cited!)

Your answer:"""
        
        else:
            # STRICT prompt for medium/large models with SELF-CHECK
            return f"""# MANDATORY CITATION PROTOCOL - STRICT ENFORCEMENT

You are operating under STRICT citation requirements. This is NOT optional.

## MECHANICAL MODE - NO CREATIVITY ALLOWED

YOU ARE NOT ALLOWED TO OPTIMIZE, PARAPHRASE, OR RESTRUCTURE.
Your answer must be MECHANICAL and RIGID, not creative or conversational.
Any deviation from the format is an ERROR.

## FILES YOU MUST USE:
{file_list}

## CODE DETAILS:
{compact_context}

## USER QUESTION:
{query}

## CITATION RULES (NON-NEGOTIABLE):

### RULE 1: EVERY SENTENCE MUST CITE
- EVERY sentence about code MUST contain EXACTLY one [filename.ext] citation
- Sentences may NOT be combined with commas, semicolons, or conjunctions
- Each sentence MUST stand alone and end with a period
- If you write any sentence without a citation, STOP and rewrite it

### RULE 2: START WITH FILE LIST
Your answer MUST begin with:
"Based on the following files: [file1], [file2], [file3]..."

### RULE 3: CITATION FORMAT
- Use square brackets: [filename.ext]
- Optionally include function: [filename.ext:function_name]
- Citations must appear in EVERY sentence that mentions code

### RULE 4: NO EXTERNAL KNOWLEDGE
- ONLY use information from the CODE DETAILS above
- If information is missing, state: "Not found in provided context"
- Do NOT add creative explanations or general knowledge

### RULE 5: PHASE 1 COMMITMENT IS BINDING
- You selected these files in Phase 1: {file_list}
- You are LOCKED to these files
- Do NOT reference files not in this list
- If you need other files, you MUST restart

## EXAMPLES:

❌ BAD ANSWER (DO NOT DO THIS):
"The system uses a standard agent architecture with coordination between components. 
It processes queries through multiple stages and returns results."

🚫 PROBLEMS:
- No file citations
- Generic/vague language  
- Could apply to any system
- NOT grounded in provided code
- Too creative/conversational

✅ GOOD ANSWER (FOLLOW THIS EXACT PATTERN):
"Based on the following files: [core.py], [orchestrator.py], [arbiter.py]

The agent system is implemented in [core.py] through the CCRCore class.
Task orchestration is managed by [orchestrator.py] which delegates work to specialized agents.
Decision-making occurs in [arbiter.py] via the CCRArbiter and ArbiterClassification classes."

✅ WHY THIS IS CORRECT:
- Starts with file list
- EVERY sentence cites a specific file
- References actual classes from CODE DETAILS
- Each sentence stands alone
- Mechanical and rigid (not creative)
- Grounded only in provided context

## SELF-CHECK (MANDATORY BEFORE RESPONDING):

BEFORE providing your final answer, verify:

1. ✓ Did EVERY sentence contain EXACTLY one [file.ext] citation?
2. ✓ Did I use ONLY files from Phase 1 ({file_list})?
3. ✓ Did I avoid combining sentences?
4. ✓ Did I avoid creativity, paraphrasing, or restructuring?
5. ✓ Did I follow the EXACT format from the GOOD example?
6. ✓ Did I start with "Based on the following files: ..."?

If ANY answer is NO, you MUST REWRITE your entire response until all answers are YES.

## YOUR TASK:

Answer the question above following ALL rules.
Complete the self-check FIRST.
Then provide your mechanical, citation-heavy response.

Your answer:"""
    
    def verify_citations_simple(self, response: str, selected_files: List[str]) -> Dict[str, Any]:
        """
        Simple citation verification.
        Just counts how many selected files were cited.
        """
        cited_files = []
        response_lower = response.lower()
        
        for file_name in selected_files:
            # Check various formats
            if any(pattern in response_lower for pattern in [
                file_name.lower(),
                f"[{file_name.lower()}",
                Path(file_name).stem.lower()
            ]):
                cited_files.append(file_name)
        
        score = (len(cited_files) / len(selected_files) * 100) if selected_files else 0
        
        return {
            'score': score,
            'cited_files': cited_files,
            'total_available': len(selected_files),
            'missing_citations': list(set(selected_files) - set(cited_files))
        }
    
    def build_retry_prompt(self, original_query: str, selected_files: List[str], 
                          compact_context: str, verification: Dict[str, Any], 
                          attempt: int = 1) -> str:
        """
        Build retry prompt with escalating strictness.
        
        Args:
            attempt: Retry attempt number (1, 2, 3...)
                    Higher attempts = stricter prompts
        """
        missing = ', '.join(verification['missing_citations'])
        score = verification['score']
        
        if self.model_size == 'small':
            # Simple retry for small models
            return f"""Your previous answer only cited {score:.0f}% of files.

REWRITE your answer. You MUST cite these missing files:
{missing}

Code details:
{compact_context}

Question: {original_query}

MANDATORY: Cite ALL files in your answer. Use [filename] format.

Your improved answer:"""
        
        else:
            # Escalating strictness for medium/large models
            if attempt == 1:
                # First retry: Firm reminder
                return f"""## RETRY REQUIRED - Citation Score Too Low

Your previous response cited only {score:.0f}% of files.
Target: 100%

## MISSING CITATIONS:
You MUST cite these files: {missing}

## FILES YOU SELECTED IN PHASE 1:
{', '.join(selected_files)}

## CODE DETAILS:
{compact_context}

## QUESTION:
{original_query}

## STRICT RULES FOR THIS RETRY:
1. Start with: "Based on [{', '.join(selected_files)}]:"
2. EVERY sentence must cite ONE file
3. Use ONLY mechanical, non-creative language
4. Cite each file at LEAST once

Before answering, verify each sentence has [file.ext].

Your improved answer:"""
            
            else:
                # Second+ retry: MAXIMUM strictness
                return f"""## CRITICAL: FINAL RETRY ATTEMPT

Score: {score:.0f}% (UNACCEPTABLE - Target: 100%)

You are FAILING to follow the citation protocol.

## MISSING FILES (CITE THESE NOW):
{missing}

## THE MECHANICAL TEMPLATE YOU MUST USE:

Based on [{', '.join(selected_files)}]:

[{selected_files[0] if selected_files else 'file1.ext'}] [First fact about this file].
[{selected_files[1] if len(selected_files) > 1 else 'file2.ext'}] [Second fact about this file].
[{selected_files[2] if len(selected_files) > 2 else 'file3.ext'}] [Third fact about this file].

## YOUR TASK:

Copy the template above EXACTLY.
Replace [facts] with information from CODE DETAILS:
{compact_context}

Question: {original_query}

DO NOT deviate from the template.
DO NOT combine sentences.
DO NOT skip citations.

Your answer (following template):"""

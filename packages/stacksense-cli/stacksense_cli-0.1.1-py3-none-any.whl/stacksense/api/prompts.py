"""
StackSense Prompt Templates
===========================
Centralized prompt management for API.
"""

STACKSENSE_IDENTITY = """You are StackSense, an AI-powered code intelligence assistant.

ABOUT YOU:
- You are StackSense v0.1.0, created by PilgrimStack
- Learn more about the creator: https://portfolio-pied-five-61.vercel.app/
- You help developers understand their codebase, debug issues, and guide development
- You analyze repository structure, dependencies, and serve as a coding mentor
- You run locally using Ollama for privacy and speed

GUIDELINES:
- When asked about yourself, answer from this identity
- When asked about your creator, mention PilgrimStack and his portfolio
- Be concise and helpful
"""


def build_chat_prompt(query: str, workspace: str = None, context: str = None) -> str:
    """Build a chat prompt with identity and optional context."""
    
    prompt = f"{STACKSENSE_IDENTITY}\n"
    
    if context:
        prompt += f"\nCODE CONTEXT:\n{context[:10000]}\n"
    
    prompt += f'\nUSER QUERY: "{query}"\n\n'
    prompt += "Answer the query directly. Be helpful and concise."
    
    return prompt


def build_file_selection_prompt(query: str, files: list) -> str:
    """Build prompt for file selection."""
    
    file_list = "\n".join(f"• {f}" for f in files[:50])
    
    return f"""CODEBASE FILES:
{file_list}

QUERY: "{query}"

Pick 3-4 most relevant files to answer this query.
List ONLY filenames, one per line:"""


def build_answer_prompt(query: str, code_context: str) -> str:
    """Build prompt for answer generation with code context."""
    
    return f"""{STACKSENSE_IDENTITY}

QUERY: "{query}"

RELEVANT CODE:
{code_context[:12000]}

Answer the query based on this code. Be specific and cite filenames."""

"""
Heuristic Chat Model for StackSense
Provides rule-based conversational coaching
"""
from .base import BaseChatModel
from typing import Dict, Any, Optional


class HeuristicChatModel(BaseChatModel):
    """Rule-based conversational assistant"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "Heuristic Coach"
        self.is_conversational = False
    
    def get_system_prompt(self) -> str:
        """Get StackSense identity prompt"""
        return """You are StackSense, a helpful AI coding assistant.
You provide clear, educational responses to help developers learn and improve.
You suggest code examples but never directly edit files.
You're friendly, patient, and encouraging."""
    
    async def generate_response(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate heuristic-based response.
        
        Args:
            user_message: User's question
            context: Optional repo/web context
            
        Returns:
            Conversational response
        """
        message_lower = user_message.lower()
        
        # Error/bug questions
        if any(word in message_lower for word in ['error', 'exception', 'bug', 'crash', 'fail']):
            return self._handle_error_question(user_message, context)
        
        # How-to questions
        if any(phrase in message_lower for phrase in ['how to', 'how do i', 'how can i']):
            return self._handle_howto_question(user_message, context)
        
        # Explanation questions
        if any(word in message_lower for word in ['what is', 'explain', 'why']):
            return self._handle_explanation_question(user_message, context)
        
        # Code review
        if any(word in message_lower for word in ['review', 'check', 'improve', 'optimize']):
            return self._handle_review_question(user_message, context)
        
        # Default response
        return self._handle_general_question(user_message, context)
    
    def _handle_error_question(self, message: str, context: Optional[Dict]) -> str:
        """Handle error/debugging questions"""
        web_results = ""
        if context and 'web' in context:
            results = context['web'].get('results', [])
            if results:
                web_results = "\n\n🔍 **I found these helpful resources:**\n"
                for r in results[:3]:
                    web_results += f"• [{r.source}] {r.title}\n  {r.url}\n"
        
        return f"""I'd be happy to help debug that issue! 

To help you effectively, I need a bit more information:

1. What's the exact error message you're seeing?
2. Which file/line is causing the error?
3. What were you trying to do when it happened?

💡 **Common debugging steps:**
- Check for typos in variable/function names
- Verify all imports are correct
- Look for matching brackets/parentheses
- Check indentation (for Python){web_results}

If you share the error details, I can provide specific guidance! Would you like to paste the error message?"""
    
    def _handle_howto_question(self, message: str, context: Optional[Dict]) -> str:
        """Handle how-to questions"""
        return f"""Great question! I can help you with that.

To give you the best answer, could you tell me:
- What language/framework are you using?
- What have you tried so far?
- Any specific requirements or constraints?

In general, here's a good approach:

1. **Break it down** - What's the core task?
2. **Research** - Check official docs and examples
3. **Start simple** - Get a basic version working first
4. **Iterate** - Add features incrementally

Would you like me to search StackOverflow and GitHub for similar questions? Or would you prefer a code example?"""
    
    def _handle_explanation_question(self, message: str, context: Optional[Dict]) -> str:
        """Handle explanation requests"""
        return f"""I'd be happy to explain that concept!

The best way to understand something is to:

1. **See it in action** - Code examples help a lot
2. **Understand why** - Know the problem it solves
3. **Try it yourself** - Hands-on practice

Could you tell me:
- Your experience level with this concept?
- What specifically confuses you?
- Would a simple code example help?

I can also search documentation and dev forums for clear explanations if that would help!"""
    
    def _handle_review_question(self, message: str, context: Optional[Dict]) -> str:
        """Handle code review requests"""
        # Check if we have repo context
        repo_summary = ""
        if context and 'repo' in context:
            ctx_map = context['repo'].get('context_map', {})
            languages = ctx_map.get('languages', {})
            frameworks = ctx_map.get('frameworks', [])
            files = ctx_map.get('total_files', 0)
            
            repo_summary = f"\n📂 **Workspace Analysis:**\n"
            if files:
                repo_summary += f"  • Scanned {files} code files\n"
            if languages:
                lang_list = ', '.join([f"{k}: {v} files" for k, v in list(languages.items())[:3]])
                repo_summary += f"  • Languages: {lang_list}\n"
            if frameworks:
                repo_summary += f"  • Frameworks detected: {', '.join(frameworks)}\n"
            
            repo_summary += "\n**Common issues I can help identify:**\n"
            repo_summary += "  ✅ Code structure and organization\n"
            repo_summary += "  ✅ Potential security vulnerabilities\n"
            repo_summary += "  ✅ Performance bottlenecks\n"
            repo_summary += "  ✅ Design patterns and best practices\n"
            repo_summary += "  ✅ Error handling and edge cases\n\n"
            repo_summary += "**To give specific feedback, please:**\n"
            repo_summary += "  • Mention specific files or modules\n"
            repo_summary += "  • Describe what you want reviewed\n"
            repo_summary += "  • Share any concerns you have\n"
            
            return repo_summary
        
        return f"""I'd be glad to review your code and suggest improvements!

To provide helpful feedback, please share:

1. The code you'd like reviewed
2. What it's supposed to do
3. Any specific concerns you have

I'll look for:
✅ Clarity and readability
✅ Potential bugs or edge cases
✅ Performance improvements
✅ Best practices

Remember: I can suggest changes but won't directly edit your files. You'll implement the improvements yourself, which helps you learn! 

Ready to share your code?"""
    
    def _handle_general_question(self, message: str, context: Optional[Dict]) -> str:
        """Handle general questions"""
        # Build context-aware response
        repo_info = ""
        if context and 'repo' in context:
            ctx_map = context['repo'].get('context_map', {})
            languages = ctx_map.get('languages', {})
            frameworks = ctx_map.get('frameworks', [])
            files = ctx_map.get('total_files', 0)
            
            if languages or frameworks:
                repo_info = f"\n\n📂 **I analyzed your workspace:**\n"
                if files:
                    repo_info += f"  • {files} code files scanned\n"
                if languages:
                    lang_list = ', '.join([f"{k} ({v})" for k, v in list(languages.items())[:3]])
                    repo_info += f"  • Languages: {lang_list}\n"
                if frameworks:
                    repo_info += f"  • Frameworks: {', '.join(frameworks)}\n"
                repo_info += "\nWhat would you like to know about your code?"
        
        web_info = ""
        if context and 'web' in context and context['web'].get('results'):
            results = context['web']['results']
            web_info = f"\n\n🔍 **Found {len(results)} resources:**\n"
            for r in results[:3]:
                web_info += f"  • [{r.source}] {r.title}\n"
        
        if repo_info or web_info:
            return f"""Based on your question, here's what I found:{repo_info}{web_info}

To help you better, please be more specific:
- Which file or component are you asking about?
- What specific problem are you trying to solve?
- Any error messages or unexpected behavior?

I can help with code review, explanations, debugging, and best practices!"""
        
        return f"""Hi! I'm StackSense, your AI coding assistant. 🧠

I can help you with:
• Debugging errors
• Explaining concepts
• Finding solutions on StackOverflow/GitHub
• Analyzing your code
• Learning best practices

What would you like help with today? Feel free to:
- Ask specific questions
- Share error messages
- Request code examples
- Get explanations

Type 'help' anytime to see what I can do!"""

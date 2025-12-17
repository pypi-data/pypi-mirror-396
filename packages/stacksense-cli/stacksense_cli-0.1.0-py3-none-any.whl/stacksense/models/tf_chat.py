"""
TensorFlow Chat Model - Conversational wrapper for TensorFlow suggestions
Wraps the existing TensorFlow model with conversational responses
"""
from .base import BaseChatModel
from typing import Dict, Any, Optional


class TensorFlowChatModel(BaseChatModel):
    """Conversational wrapper for TensorFlow commit suggestions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TensorFlow Coach"
        self.is_conversational = False
        self.tf_available = False
        
        # Try to import TensorFlow model
        try:
            from commit_checker.tensorflow_model import is_model_available
            self.tf_available = is_model_available()
        except Exception:
            self.tf_available = False
    
    def get_system_prompt(self) -> str:
        """StackSense identity for TensorFlow mode"""
        return """You are StackSense with TensorFlow-powered suggestions.
You help developers write better commit messages and understand coding practices."""
    
    async def generate_response(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate conversational response with TensorFlow suggestions"""
        
        if not self.tf_available:
            return self._tf_not_available_response()
        
        message_lower = user_message.lower()
        
        # Commit message related
        if any(word in message_lower for word in ['commit', 'message', 'git']):
            return self._handle_commit_question(user_message, context)
        
        # Code explanation
        if any(word in message_lower for word in ['explain', 'what is', 'understand']):
            return self._handle_explanation(user_message, context)
        
        # Suggestions/improvements
        if any(word in message_lower for word in ['suggest', 'improve', 'better', 'how to']):
            return self._handle_suggestion(user_message, context)
        
        # General help
        return self._handle_general(user_message, context)
    
    def _tf_not_available_response(self) -> str:
        """Response when TensorFlow is not available"""
        return """I'd love to help, but the TensorFlow model isn't currently loaded.

**To use TensorFlow-powered suggestions:**
1. The model downloads automatically on first use
2. Requires ~50MB download
3. Works offline after download

Would you like me to help with something else? I can still:
- Answer coding questions
- Search StackOverflow and GitHub
- Explain concepts
- Give general guidance

Or switch to another AI model with: `commit-checker --setup-ai`"""
    
    def _handle_commit_question(self, message: str, context: Optional[Dict]) -> str:
        """Handle commit-message related questions"""
        return """I can help you write better commit messages!

**Good commit message practices:**

✅ **DO:**
- Use imperative mood ("Add feature" not "Added feature")
- Keep subject line under 50 chars
- Explain WHY, not just WHAT
- Reference issues/tickets when relevant

❌ **DON'T:**
- "Fixed stuff"
- "WIP"
- "asdfgh"
- Vague descriptions

**Try:**
```bash
commit-checker --suggest "your draft message"
```

**Example:**
- Draft: "fixed bug"
- Better: "fix: prevent null pointer in user authentication"

Want me to review a specific commit message?"""
    
    def _handle_explanation(self, message: str, context: Optional[Dict]) -> str:
        """Handle explanation requests"""
        web_results = ""
        if context and 'web' in context:
            results = context['web'].get('results', [])
            if results:
                web_results = "\n\n**I found these resources:**\n"
                for r in results[:3]:
                    web_results += f"• [{r.source}] {r.title}\n  {r.url}\n"
        
        return f"""I'd be happy to explain that concept!

To give you the best explanation:
- What's your experience level?
- Is there a specific part that's confusing?
- Would a code example help?

**Learning approach I recommend:**
1. **See it in action** - Code examples
2. **Understand why** - The problem it solves
3. **Try it yourself** - Hands-on practice
4. **Build something** - Apply the knowledge
{web_results}

What specifically would you like me to explain?"""
    
    def _handle_suggestion(self, message: str, context: Optional[Dict]) -> str:
        """Handle suggestion requests"""
        repo_context = ""
        if context and 'repo' in context:
            ctx_map = context['repo'].get('context_map', {})
            langs = ctx_map.get('languages', {})
            if langs:
                lang_list = ', '.join(list(langs.keys())[:3])
                repo_context = f"\n\nI see you're working with: {lang_list}"
        
        return f"""Great! I can help with suggestions.{repo_context}

**To get specific help:**
- Share the code you want to improve
- Describe what you're trying to achieve
- Mention any concerns or constraints

**I can suggest:**
✅ Better code structure
✅ Performance improvements
✅ Best practices for your language
✅ Clearer variable/function names
✅ Error handling patterns

**Remember:** I'll suggest improvements, but you'll implement them. This helps you learn!

Ready to share your code?"""
    
    def _handle_general(self, message: str, context: Optional[Dict]) -> str:
        """Handle general questions"""
        return """Hi! I'm StackSense with TensorFlow-powered suggestions. 🧠

**I can help you with:**
• Writing better commit messages
• Code best practices
• Explaining programming concepts
• Finding solutions online
• Improving your code

**What would you like help with?**

Examples:
- "How do I write a good commit message?"
- "Explain async/await in JavaScript"
- "Review my Python function"
- "Best way to handle errors in React?"

Just ask me anything!"""

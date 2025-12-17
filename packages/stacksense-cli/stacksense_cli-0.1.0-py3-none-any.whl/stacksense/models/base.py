"""
Base model interface for StackSense chat models
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseChatModel(ABC):
    """Base interface for all StackSense chat models"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = "base"
        self.is_conversational = False  # True for Ollama/Together, False for TF/Heuristic
    
    @abstractmethod
    async def generate_response(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response to the user's message.
        
        Args:
            user_message: The user's input
            context: Optional context including repo scan and web search results
            
        Returns:
            The model's response as a string
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines StackSense's identity.
        
        Returns:
            System prompt string
        """
        pass
    
    def should_search_web(self, user_message: str) -> bool:
        """
        Determine if web search is needed based on the message.
        
        Args:
            user_message: The user's question
            
        Returns:
            True if web search should be triggered
        """
        # Default heuristic: search for errors, APIs, libraries, frameworks
        search_keywords = [
            'error', 'exception', 'bug', 'issue', 'problem',
            'how to', 'how do i', 'what is', 'why',
            'library', 'framework', 'api', 'package',
            'install', 'setup', 'configure'
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in search_keywords)
    
    def should_scan_repo(self, user_message: str) -> bool:
        """
        Determine if we should scan the repository for this query.
        
        Args:
            user_message: User's question
            
        Returns:
            True if repo scan would be helpful
        """
        message_lower = user_message.lower()
        
        # Keywords that suggest needing repo context
        repo_keywords = [
            'code', 'file', 'function', 'class', 'repo', 'repository',
            'project', 'workspace', 'codebase', 'review', 'check',
            'analyze', 'scan', 'find', 'locate', 'search', 'module',
            'package', 'directory', 'structure', 'architecture', 'design',
            'implement', 'refactor', 'improve', 'optimize', 'bug',
            'error in', 'issue in', 'problem with', 'my code', 'this code',
            'performance', 'security', 'vulnerability', 'weakness', 'bottleneck'
        ]
        
        return any(keyword in message_lower for keyword in repo_keywords)


class StreamingChatModel(BaseChatModel):
    """Base class for models that support streaming responses"""
    
    @abstractmethod
    async def generate_response_stream(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Generate a streaming response.
        
        Yields:
            Response chunks as they arrive
        """
        pass

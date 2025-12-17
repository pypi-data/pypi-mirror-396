"""
Context Health Meter - Prevent Hallucinations
==============================================
Tracks context window usage and auto-summarizes when approaching limits.
"""
from typing import Dict, Any, List
from datetime import datetime


class ContextHealthMeter:
    """
    Monitors context window usage to prevent hallucinations.
    Displays health status and auto-compresses when needed.
    """
    
    # Context limits for common models (approx tokens)
    MODEL_LIMITS = {
        'phi3:mini': 4096,
        'phi3:medium': 4096,
        'llama2': 4096,
        'llama2:13b': 4096,
        'llama2:70b': 4096,
        'mistral': 8192,
        'mixtral': 32768,
        'gpt-3.5-turbo': 16385,
        'gpt-4': 8192,
        'gpt-4-32k': 32768,
        'default': 4096
    }
    
    # Compression thresholds
    WARNING_THRESHOLD = 0.70  # 70% - show warning
    COMPRESS_THRESHOLD = 0.85  # 85% - auto-compress
    
    def __init__(self, model_name: str = 'default', debug: bool = False):
        self.model_name = model_name
        self.debug = debug
        
        # Get model limit
        self.max_tokens = self.MODEL_LIMITS.get(model_name, self.MODEL_LIMITS['default'])
        
        # Tracking
        self.conversation_history = []
        self.current_tokens = 0
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens from text.
        Rule of thumb: ~4 characters per token for English.
        """
        return max(1, len(text) // 4)
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        tokens = self.estimate_tokens(content)
        
        self.conversation_history.append({
            'role': role,
            'content': content,
            'tokens': tokens,
            'timestamp': datetime.now().isoformat()
        })
        
        self.current_tokens += tokens
        
        if self.debug:
            usage_pct = self.get_usage_percentage()
            print(f"[ContextHealth] Added {tokens} tokens ({usage_pct:.0f}% used)")
    
    def get_usage_percentage(self) -> float:
        """Get current usage as percentage"""
        return (self.current_tokens / self.max_tokens) * 100
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status with emoji and recommendation.
        """
        usage_pct = self.get_usage_percentage()
        
        if usage_pct < self.WARNING_THRESHOLD * 100:
            status = 'fresh'
            emoji = '✅'
            color = 'green'
            action = None
        elif usage_pct < self.COMPRESS_THRESHOLD * 100:
            status = 'warming'
            emoji = '🔸'
            color = 'yellow'
            action = 'Consider summarizing soon'
        else:
            status = 'saturated'
            emoji = '🔴'
            color = 'red'
            action = 'Auto-summarizing now'
        
        return {
            'status': status,
            'emoji': emoji,
            'color': color,
            'usage_pct': usage_pct,
            'tokens_used': self.current_tokens,
            'tokens_max': self.max_tokens,
            'action': action,
            'message_count': len(self.conversation_history)
        }
    
    def display_health(self) -> str:
        """Return formatted health display string"""
        health = self.get_health_status()
        
        return f"💬 Context: {health['status'].title()} {health['emoji']} ({health['usage_pct']:.0f}%)"
    
    def should_compress(self) -> bool:
        """Check if compression is needed"""
        return self.get_usage_percentage() >= (self.COMPRESS_THRESHOLD * 100)
    
    def compress_history(self) -> Dict[str, Any]:
        """
        Compress conversation history when approaching limit.
        Returns compressed summary and statistics.
        """
        if not self.conversation_history:
            return {'summary': '', 'tokens_saved': 0}
        
        # Separate into user queries and AI responses
        queries = [msg for msg in self.conversation_history if msg['role'] == 'user']
        responses = [msg for msg in self.conversation_history if msg['role'] == 'assistant']
        
        # Build summary
        summary_parts = []
        
        # Summarize user queries
        if queries:
            query_topics = [q['content'][:100] for q in queries[:5]]  # First 5 queries
            summary_parts.append(f"User asked about: {'; '.join(query_topics)}")
        
        # Key points from responses
        if responses:
            # Extract key facts (lines starting with **, -, etc.)
            key_points = []
            for resp in responses:
                lines = resp['content'].split('\n')
                for line in lines[:10]:  # First 10 lines of each response
                    if line.strip().startswith(('**', '-', '•', '1.', '2.')):
                        key_points.append(line.strip())
            
            if key_points:
                summary_parts.append(f"Key points discussed: {'; '.join(key_points[:10])}")
        
        summary = '\n'.join(summary_parts)
        
        # Calculate tokens saved
        old_tokens = self.current_tokens
        new_tokens = self.estimate_tokens(summary)
        tokens_saved = old_tokens - new_tokens
        
        # Reset with compressed summary
        self.conversation_history = [{
            'role': 'system',
            'content': f"[Compressed conversation summary]: {summary}",
            'tokens': new_tokens,
            'timestamp': datetime.now().isoformat()
        }]
        
        self.current_tokens = new_tokens
        
        if self.debug:
            print(f"[ContextHealth] Compressed: {old_tokens} → {new_tokens} tokens (saved {tokens_saved})")
        
        return {
            'summary': summary,
            'tokens_saved': tokens_saved,
            'old_tokens': old_tokens,
            'new_tokens': new_tokens,
            'compression_ratio': (tokens_saved / old_tokens * 100) if old_tokens > 0 else 0
        }
    
    def reset(self):
        """Reset context to fresh state"""
        self.conversation_history = []
        self.current_tokens = 0
        
        if self.debug:
            print("[ContextHealth] Reset to fresh state")

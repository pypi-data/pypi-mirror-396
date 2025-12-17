"""
StackSense UI Utilities
Provides animations and progress indicators for better UX
"""
import sys
import time
import threading
from typing import Optional


class Spinner:
    """Animated spinner for long-running operations"""
    
    # Different spinner styles
    DOTS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    BOUNCING = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    SIMPLE = ['|', '/', '-', '\\']
    
    def __init__(self, message: str = "Loading...", style: str = 'dots'):
        """
        Initialize spinner.
        
        Args:
            message: Message to display
            style: 'dots', 'bouncing', or 'simple'
        """
        self.message = message
        self.frames = {
            'dots': self.DOTS,
            'bouncing': self.BOUNCING,
            'simple': self.SIMPLE
        }.get(style, self.DOTS)
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def _spin(self):
        """Internal spinner loop"""
        idx = 0
        while self._running:
            frame = self.frames[idx % len(self.frames)]
            sys.stdout.write(f'\r{frame} {self.message}')
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1
    
    def start(self):
        """Start the spinner"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
    
    def stop(self, final_message: Optional[str] = None):
        """
        Stop the spinner.
        
        Args:
            final_message: Optional message to display after stopping
        """
        if self._running:
            self._running = False
            if self._thread:
                self._thread.join(timeout=0.5)
            
            # Clear the line
            sys.stdout.write('\r' + ' ' * (len(self.message) + 5) + '\r')
            
            if final_message:
                print(final_message)
            
            sys.stdout.flush()
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


def print_progress(message: str, status: str = 'info'):
    """
    Print a progress message with emoji indicator.
    
    Args:
        message: Message to print
        status: 'info', 'success', 'warning', 'error', 'searching'
    """
    emoji = {
        'info': '📌',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'searching': '🔍',
        'thinking': '🤖',
        'scanning': '📂'
    }.get(status, '•')
    
    print(f"{emoji} {message}")


def print_search_result(source: str, title: str, url: str, index: int):
    """
    Print a search result as it arrives.
    
    Args:
        source: Source name (stackoverflow, github, etc)
        title: Result title
        url: Result URL
        index: Result index
    """
    source_emoji = {
        'stackoverflow': '📚',
        'github': '🐙',
        'reddit': '🤖',
        'mdn': '📘'
    }.get(source.lower(), '🔗')
    
    print(f"   {index}. {source_emoji} [{source.upper()}] {title[:60]}...")
    if url:
        print(f"      ↳ {url}")

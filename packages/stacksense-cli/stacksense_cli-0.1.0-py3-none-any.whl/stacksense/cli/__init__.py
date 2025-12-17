"""
StackSense CLI Package
======================
Command-line interface and chat functionality.
"""

from .cli import main as cli_main
from .chat import StackSenseChat, start_chat
from .rich_chat import RichChatUI

__all__ = ['cli_main', 'StackSenseChat', 'start_chat', 'RichChatUI']

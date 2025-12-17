"""
StackSense - AI-Powered Code Intelligence
==========================================
Created by PilgrimStack
https://portfolio-pied-five-61.vercel.app/

A local AI assistant for understanding codebases,
debugging issues, and guiding development.
"""

__version__ = "0.1.0"
__author__ = "PilgrimStack"

# Lazy imports to avoid circular dependencies
def get_scanner():
    from .core.repo_scanner import RepoScanner
    return RepoScanner

def get_chat():
    from .cli.chat import Chat, start_chat
    return Chat, start_chat

def get_diagram_builder():
    from .core.diagram_builder import DiagramBuilder
    return DiagramBuilder

def get_orchestrator():
    from .core.diagram_orchestrator import DiagramBasedOrchestrator
    return DiagramBasedOrchestrator

__all__ = [
    '__version__',
    '__author__',
    'get_scanner',
    'get_chat',
    'get_diagram_builder',
    'get_orchestrator',
]

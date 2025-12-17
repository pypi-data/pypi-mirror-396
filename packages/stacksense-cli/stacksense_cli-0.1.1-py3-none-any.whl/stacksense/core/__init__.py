"""
StackSense Core Package
=======================
Core modules for code intelligence.
"""

from .diagram_builder import DiagramBuilder
from .diagram_orchestrator import DiagramBasedOrchestrator
from .fast_query_processor import FastQueryProcessor
from .repo_scanner import RepoScanner
from .workspace_detector import WorkspaceDetector
from .storage_manager import StorageManager
from .model_manager import ModelManager

__all__ = [
    'DiagramBuilder',
    'DiagramBasedOrchestrator',
    'FastQueryProcessor',
    'RepoScanner',
    'WorkspaceDetector',
    'StorageManager',
    'ModelManager',
]


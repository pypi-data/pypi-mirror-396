"""
COOLBOOY__version__ = "1.2.1"PT - COOLBOOY-Multi-Provider AI Assistant

A powerful command-line AI assistant that supports multiple AI providers
including OpenAI, Anthropic, Google, and custom APIs.
"""

__version__ = "1.2.1"
__author__ = "COOLBOOY Contributors"
__license__ = "MIT"
__description__ = "COOLBOOY-Multi-Provider AI Assistant for developers and power users"

from .core.config import Config, config
from .core.ai_interface import AIInterface, ai_interface
from .core.manager import COOLBOOYManager, manager

__all__ = [
    "Config", "config",
    "AIInterface", "ai_interface",
    "COOLBOOYManager", "manager",
    "__version__", "__description__"
]

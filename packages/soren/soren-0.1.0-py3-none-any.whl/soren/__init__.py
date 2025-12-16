"""
Soren - AI Evaluation Framework CLI
"""
__version__ = "0.1.0"

# Expose main components for easy importing
from .client import SorenClient
from .config import SorenConfig
from .cli import main

__all__ = [
    "__version__",
    "SorenClient",
    "SorenConfig",
    "main",
]

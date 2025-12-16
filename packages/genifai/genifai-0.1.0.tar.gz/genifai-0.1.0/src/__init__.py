"""Genifai - AI-powered test case generator

This package provides both CLI and Python API.
"""

__version__ = "0.1.0"

# Public API
from .client import GenifaiClient
from .config import Config

__all__ = [
    "GenifaiClient",
    "Config",
]
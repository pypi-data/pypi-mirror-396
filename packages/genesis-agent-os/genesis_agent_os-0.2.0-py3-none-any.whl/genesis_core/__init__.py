"""
The Genesis Framework - Main Package.

This package provides the core functionality for the Genesis Framework,
including the main Genesis SDK class for creating and managing AI agents.
"""

# Import the main Genesis class to make it available at the top level
from .genesis_core.sdk import Genesis

__version__ = "0.1.0"
__author__ = "Genesis Framework"
__all__ = ["Genesis"]
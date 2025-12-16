"""
GoMask CLI - Configuration as Code for Synthetic Data Generation and Masking

This package provides command-line tools for managing GoMask routines through
YAML configuration files, enabling version control and CI/CD integration.
"""

__version__ = "1.0.0"
__author__ = "GoMask Team"
__email__ = "support@gomask.ai"

from gomask.cli import main

__all__ = ["main"]
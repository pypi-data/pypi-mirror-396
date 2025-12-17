"""Logger initialization module.

This module provides easy access to the enhanced logging utilities.
"""

from .enhanced_logger import (
    ColoredFormatter,
    Colors,
    EnhancedLogger,
    get_logger,
)

__version__ = "2025.12.13"
__all__ = ["ColoredFormatter", "Colors", "EnhancedLogger", "get_logger"]

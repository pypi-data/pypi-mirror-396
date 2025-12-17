"""Logger initialization module.

This module provides easy access to the enhanced logging utilities.
"""

from .enhanced_logger import (
    ColoredFormatter,
    Colors,
    EnhancedLogger,
    get_available_timezones,
    get_logger,
    is_valid_timezone,
)

# Set automatically from git tag during Github UI Release creation.
__version__ = "2025.12.14"

__all__ = [
    "ColoredFormatter",
    "Colors",
    "EnhancedLogger",
    "get_logger",
    "get_available_timezones",
    "is_valid_timezone",
]

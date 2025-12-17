"""Tests for the package __init__.py module."""

import pytest


class TestPackageImports:
    """Tests for package-level imports and exports."""

    def test_import_colors(self):
        """Test that Colors can be imported from src."""
        from src import Colors

        assert Colors is not None
        assert hasattr(Colors, "RESET")

    def test_import_colored_formatter(self):
        """Test that ColoredFormatter can be imported from src."""
        from src import ColoredFormatter

        assert ColoredFormatter is not None

    def test_import_enhanced_logger(self):
        """Test that EnhancedLogger can be imported from src."""
        from src import EnhancedLogger

        assert EnhancedLogger is not None

    def test_import_get_logger(self):
        """Test that get_logger can be imported from src."""
        from src import get_logger

        assert callable(get_logger)

    def test_import_get_available_timezones(self):
        """Test that get_available_timezones can be imported from src."""
        from src import get_available_timezones

        assert callable(get_available_timezones)

    def test_import_is_valid_timezone(self):
        """Test that is_valid_timezone can be imported from src."""
        from src import is_valid_timezone

        assert callable(is_valid_timezone)

    def test_package_version(self):
        """Test that __version__ is defined."""
        from src import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        # Version should match expected pattern.
        assert "." in __version__ or __version__.startswith("20")

    def test_package_all_exports(self):
        """Test that __all__ contains expected exports."""
        from src import __all__

        expected_exports = [
            "ColoredFormatter",
            "Colors",
            "EnhancedLogger",
            "get_logger",
            "get_available_timezones",
            "is_valid_timezone",
        ]
        for export in expected_exports:
            assert export in __all__

    def test_all_exports_are_importable(self):
        """Test that all items in __all__ can be imported."""
        import src

        for name in src.__all__:
            assert hasattr(src, name)
            obj = getattr(src, name)
            assert obj is not None

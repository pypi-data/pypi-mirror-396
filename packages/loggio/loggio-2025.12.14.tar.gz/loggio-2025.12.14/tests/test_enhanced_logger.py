"""Comprehensive test suite for enhanced_logger module."""

import json
import logging
import os
import tempfile
from datetime import datetime
from io import StringIO
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from src.enhanced_logger import (
    ColoredFormatter,
    Colors,
    EnhancedLogger,
    get_available_timezones,
    get_logger,
    is_valid_timezone,
)


# Fixtures for test setup and teardown.
@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the EnhancedLogger singleton before each test."""
    # Reset singleton state before test.
    EnhancedLogger._instance = None
    EnhancedLogger._initialized = False

    # Reset global logger instance.
    import src.enhanced_logger

    src.enhanced_logger._logger_instance = None

    yield

    # Cleanup after test.
    EnhancedLogger._instance = None
    EnhancedLogger._initialized = False
    src.enhanced_logger._logger_instance = None


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing file output."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup.
    if os.path.exists(temp_path):
        os.remove(temp_path)


class TestColors:
    """Tests for the Colors class constants."""

    def test_reset_color(self):
        """Test RESET color code exists."""
        assert Colors.RESET == "\033[0m"

    def test_bold_color(self):
        """Test BOLD color code exists."""
        assert Colors.BOLD == "\033[1m"

    def test_basic_colors(self):
        """Test basic foreground colors exist."""
        assert Colors.BLACK == "\033[30m"
        assert Colors.RED == "\033[31m"
        assert Colors.GREEN == "\033[32m"
        assert Colors.YELLOW == "\033[33m"
        assert Colors.BLUE == "\033[34m"
        assert Colors.MAGENTA == "\033[35m"
        assert Colors.CYAN == "\033[36m"
        assert Colors.WHITE == "\033[37m"

    def test_bright_colors(self):
        """Test bright foreground colors exist."""
        assert Colors.BRIGHT_BLACK == "\033[90m"
        assert Colors.BRIGHT_RED == "\033[91m"
        assert Colors.BRIGHT_GREEN == "\033[92m"
        assert Colors.BRIGHT_YELLOW == "\033[93m"
        assert Colors.BRIGHT_BLUE == "\033[94m"
        assert Colors.BRIGHT_MAGENTA == "\033[95m"
        assert Colors.BRIGHT_CYAN == "\033[96m"
        assert Colors.BRIGHT_WHITE == "\033[97m"

    def test_background_colors(self):
        """Test background colors exist."""
        assert Colors.BG_BLACK == "\033[40m"
        assert Colors.BG_RED == "\033[41m"
        assert Colors.BG_GREEN == "\033[42m"
        assert Colors.BG_YELLOW == "\033[43m"
        assert Colors.BG_BLUE == "\033[44m"
        assert Colors.BG_MAGENTA == "\033[45m"
        assert Colors.BG_CYAN == "\033[46m"
        assert Colors.BG_WHITE == "\033[47m"


class TestColoredFormatter:
    """Tests for the ColoredFormatter class."""

    def test_init_defaults(self):
        """Test ColoredFormatter initialization with defaults."""
        formatter = ColoredFormatter()
        assert formatter.use_colors is True
        assert formatter.timezone is None

    def test_init_with_colors_disabled(self):
        """Test ColoredFormatter initialization with colors disabled."""
        formatter = ColoredFormatter(use_colors=False)
        assert formatter.use_colors is False

    def test_init_with_timezone_string(self):
        """Test ColoredFormatter initialization with timezone string."""
        formatter = ColoredFormatter(timezone="UTC")
        assert formatter.timezone == "UTC"

    def test_init_with_timezone_zoneinfo(self):
        """Test ColoredFormatter initialization with ZoneInfo object."""
        tz = ZoneInfo("America/New_York")
        formatter = ColoredFormatter(timezone=tz)
        assert formatter.timezone == tz

    def test_converter_with_string_timezone(self):
        """Test converter method with string timezone."""
        formatter = ColoredFormatter(timezone="UTC")
        timestamp = 1702500000  # A fixed timestamp.
        result = formatter.converter(timestamp)
        # Result should be a time.struct_time.
        assert hasattr(result, "tm_year")
        assert hasattr(result, "tm_mon")

    def test_converter_with_zoneinfo_timezone(self):
        """Test converter method with ZoneInfo timezone."""
        tz = ZoneInfo("Europe/London")
        formatter = ColoredFormatter(timezone=tz)
        timestamp = 1702500000
        result = formatter.converter(timestamp)
        assert hasattr(result, "tm_year")

    def test_converter_without_timezone(self):
        """Test converter method without timezone falls back to default."""
        formatter = ColoredFormatter(timezone=None)
        timestamp = 1702500000
        result = formatter.converter(timestamp)
        assert hasattr(result, "tm_year")

    def test_format_time_with_string_timezone_and_datefmt(self):
        """Test formatTime with string timezone and custom date format."""
        formatter = ColoredFormatter(timezone="UTC")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")
        # Should be formatted string.
        assert "-" in result
        assert ":" in result

    def test_format_time_with_zoneinfo_timezone_no_datefmt(self):
        """Test formatTime with ZoneInfo timezone and no date format (uses ISO)."""
        tz = ZoneInfo("Asia/Tokyo")
        formatter = ColoredFormatter(timezone=tz)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.formatTime(record)
        # Should be ISO format.
        assert "T" in result or "-" in result

    def test_format_time_without_timezone(self):
        """Test formatTime without timezone falls back to default."""
        formatter = ColoredFormatter(timezone=None)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.formatTime(record)
        assert result is not None

    def test_format_time_with_invalid_timezone(self, capsys):
        """Test formatTime with invalid timezone falls back to local time."""
        formatter = ColoredFormatter(timezone="Invalid/Timezone")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.formatTime(record)
        captured = capsys.readouterr()
        # Should print warning to stderr.
        assert "WARNING" in captured.err or result is not None
        # Timezone should be reset to None.
        assert formatter.timezone is None

    def test_format_with_colors_enabled(self):
        """Test format method with colors enabled."""
        fmt = "%(levelname)s:[%(asctime)s]%(filename)s:%(lineno)d:%(message)s"
        formatter = ColoredFormatter(fmt=fmt, use_colors=True)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        # Should contain color codes.
        assert "\033[" in result

    def test_format_with_colors_disabled(self):
        """Test format method with colors disabled."""
        fmt = "%(levelname)s:%(message)s"
        formatter = ColoredFormatter(fmt=fmt, use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        # Should not contain color codes.
        assert "\033[" not in result
        assert "test message" in result

    def test_format_all_log_levels(self):
        """Test format method with all log levels."""
        fmt = "%(levelname)s:%(message)s"
        formatter = ColoredFormatter(fmt=fmt, use_colors=True)

        levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]

        for level in levels:
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="test.py",
                lineno=1,
                msg="test",
                args=(),
                exc_info=None,
            )
            result = formatter.format(record)
            # All levels should produce output with color codes.
            assert "\033[" in result

    def test_format_unknown_log_level(self):
        """Test format method with an unknown log level."""
        fmt = "%(levelname)s:%(message)s"
        formatter = ColoredFormatter(fmt=fmt, use_colors=True)
        record = logging.LogRecord(
            name="test",
            level=99,  # Unknown level.
            pathname="test.py",
            lineno=1,
            msg="test",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        # Should still produce output.
        assert "test" in result

    def test_level_colors_mapping(self):
        """Test that LEVEL_COLORS mapping contains expected levels."""
        assert logging.DEBUG in ColoredFormatter.LEVEL_COLORS
        assert logging.INFO in ColoredFormatter.LEVEL_COLORS
        assert logging.WARNING in ColoredFormatter.LEVEL_COLORS
        assert logging.ERROR in ColoredFormatter.LEVEL_COLORS
        assert logging.CRITICAL in ColoredFormatter.LEVEL_COLORS


class TestEnhancedLoggerSingleton:
    """Tests for EnhancedLogger singleton pattern."""

    def test_singleton_returns_same_instance(self):
        """Test that multiple instantiations return the same instance."""
        logger1 = EnhancedLogger(name="test1", terminal=False, fileout_path=None)
        logger2 = EnhancedLogger(name="test2", terminal=False, fileout_path=None)
        assert logger1 is logger2

    def test_singleton_initialization_only_once(self):
        """Test that initialization only happens once."""
        logger1 = EnhancedLogger(
            name="first", level="DEBUG", terminal=False, fileout_path=None
        )
        logger2 = EnhancedLogger(
            name="second", level="WARNING", terminal=False, fileout_path=None
        )
        # Second call should not reinitialize.
        assert logger2.name == "first"
        assert logger2.level == "DEBUG"


class TestEnhancedLoggerInit:
    """Tests for EnhancedLogger initialization."""

    def test_init_defaults(self):
        """Test EnhancedLogger initialization with defaults."""
        # Use terminal=False to avoid handler issues in tests.
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        assert logger.name is None
        assert logger.level == "INFO"
        assert logger.terminal is False
        assert logger.json_format is False
        assert logger.truncate_length == 5000
        assert logger.truncate is True
        assert logger.use_colors is True
        assert logger.timezone is None

    def test_init_with_custom_parameters(self, temp_log_file):
        """Test EnhancedLogger initialization with custom parameters."""
        logger = EnhancedLogger(
            name="custom",
            level="DEBUG",
            terminal=True,
            fileout_path=temp_log_file,
            json_format=True,
            truncate_length=1000,
            truncate=False,
            use_colors=False,
            timezone="UTC",
        )
        assert logger.name == "custom"
        assert logger.level == "DEBUG"
        assert logger.terminal is True
        assert logger.fileout_path == temp_log_file
        assert logger.json_format is True
        assert logger.truncate_length == 1000
        assert logger.truncate is False
        assert logger.use_colors is False
        assert logger.timezone == "UTC"

    def test_init_creates_file_handler(self, temp_log_file):
        """Test that initialization creates file handler when path provided."""
        logger = EnhancedLogger(terminal=False, fileout_path=temp_log_file)
        # Should have one file handler.
        assert len(logger.logger.handlers) == 1
        assert isinstance(logger.logger.handlers[0], logging.FileHandler)

    def test_init_creates_terminal_handler(self):
        """Test that initialization creates terminal handler when enabled."""
        logger = EnhancedLogger(terminal=True, fileout_path=None)
        # Should have one stream handler.
        assert len(logger.logger.handlers) == 1
        assert isinstance(logger.logger.handlers[0], logging.StreamHandler)

    def test_init_creates_both_handlers(self, temp_log_file):
        """Test that initialization creates both handlers when both enabled."""
        logger = EnhancedLogger(terminal=True, fileout_path=temp_log_file)
        # Should have two handlers.
        assert len(logger.logger.handlers) == 2

    def test_init_sets_propagate_false(self):
        """Test that logger.propagate is set to False."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        assert logger.logger.propagate is False


class TestEnhancedLoggerReconfigure:
    """Tests for EnhancedLogger reconfigure method."""

    def test_reconfigure_level(self, temp_log_file):
        """Test reconfiguring log level."""
        logger = EnhancedLogger(
            level="INFO", terminal=False, fileout_path=temp_log_file
        )
        logger.reconfigure(level="DEBUG")
        assert logger.level == "DEBUG"
        assert logger.logger.level == logging.DEBUG

    def test_reconfigure_terminal(self, temp_log_file):
        """Test reconfiguring terminal output."""
        logger = EnhancedLogger(terminal=False, fileout_path=temp_log_file)
        logger.reconfigure(terminal=True)
        assert logger.terminal is True
        # Should now have both handlers.
        assert len(logger.logger.handlers) == 2

    def test_reconfigure_fileout_path(self, temp_log_file):
        """Test reconfiguring file output path."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        logger.reconfigure(fileout_path=temp_log_file)
        assert logger.fileout_path == temp_log_file

    def test_reconfigure_json_format(self):
        """Test reconfiguring JSON format."""
        logger = EnhancedLogger(json_format=False, terminal=False, fileout_path=None)
        logger.reconfigure(json_format=True)
        assert logger.json_format is True

    def test_reconfigure_truncate_length(self):
        """Test reconfiguring truncate length."""
        logger = EnhancedLogger(truncate_length=5000, terminal=False, fileout_path=None)
        logger.reconfigure(truncate_length=1000)
        assert logger.truncate_length == 1000

    def test_reconfigure_truncate(self):
        """Test reconfiguring truncate setting."""
        logger = EnhancedLogger(truncate=True, terminal=False, fileout_path=None)
        logger.reconfigure(truncate=False)
        assert logger.truncate is False

    def test_reconfigure_use_colors(self):
        """Test reconfiguring use_colors setting."""
        logger = EnhancedLogger(use_colors=True, terminal=False, fileout_path=None)
        logger.reconfigure(use_colors=False)
        assert logger.use_colors is False

    def test_reconfigure_timezone(self):
        """Test reconfiguring timezone setting."""
        logger = EnhancedLogger(timezone=None, terminal=False, fileout_path=None)
        logger.reconfigure(timezone="UTC")
        assert logger.timezone == "UTC"

    def test_reconfigure_name(self):
        """Test reconfiguring name setting."""
        logger = EnhancedLogger(name="old", terminal=False, fileout_path=None)
        logger.reconfigure(name="new")
        assert logger.name == "new"

    def test_reconfigure_preserves_unset_parameters(self):
        """Test that reconfigure preserves parameters not explicitly set."""
        logger = EnhancedLogger(
            name="test",
            level="DEBUG",
            truncate_length=2000,
            terminal=False,
            fileout_path=None,
        )
        logger.reconfigure(level="WARNING")
        # Only level should change.
        assert logger.level == "WARNING"
        assert logger.name == "test"
        assert logger.truncate_length == 2000


class TestEnhancedLoggerFormatMessage:
    """Tests for EnhancedLogger _format_message method."""

    def test_format_simple_message(self):
        """Test formatting a simple message without args."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        result = logger._format_message("Hello World")
        assert result == "Hello World"

    def test_format_message_with_args(self):
        """Test formatting message with format string args."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        result = logger._format_message("Value: %s, Count: %d", ("test", 42))
        assert result == "Value: test, Count: 42"

    def test_format_message_with_user_context(self):
        """Test formatting message with user context."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        user_context = {"uid": "user123", "email": "test@example.com"}
        result = logger._format_message("Action completed", user_context=user_context)
        assert result == "user123: Action completed"

    def test_format_message_user_context_without_uid(self):
        """Test formatting message with user context without uid key."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        user_context = {"email": "test@example.com"}
        result = logger._format_message("Action completed", user_context=user_context)
        # Should not prepend anything since no uid.
        assert result == "Action completed"

    def test_format_message_with_json_format(self):
        """Test formatting message with JSON format enabled."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        data = {"key": "value", "nested": {"inner": 123}}
        result = logger._format_message("Data: %s", (data,), json_format=True)
        assert '"key": "value"' in result
        assert '"nested"' in result

    def test_format_message_json_format_error(self):
        """Test formatting message when JSON formatting fails."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)

        # Create an object that can't be easily JSON serialized.
        class NonSerializable:
            pass

        obj = NonSerializable()
        # The default=str in json.dumps should handle this.
        result = logger._format_message("Data: %s", (obj,), json_format=True)
        assert "Data:" in result

    def test_format_message_json_format_exception(self):
        """Test formatting message when json.dumps raises an exception."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        data = {"key": "value"}

        # Mock json.dumps to raise a TypeError.
        with patch(
            "src.enhanced_logger.json.dumps", side_effect=TypeError("Mock JSON error")
        ):
            result = logger._format_message("Data: %s", (data,), json_format=True)
            assert "JSON FORMAT ERROR" in result
            assert "Mock JSON error" in result

    def test_format_message_json_format_value_error(self):
        """Test formatting message when json.dumps raises ValueError."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        data = {"key": "value"}

        # Mock json.dumps to raise a ValueError.
        with patch(
            "src.enhanced_logger.json.dumps",
            side_effect=ValueError("Value error in JSON"),
        ):
            result = logger._format_message("Data: %s", (data,), json_format=True)
            assert "JSON FORMAT ERROR" in result
            assert "Value error in JSON" in result

    def test_format_message_format_string_error(self):
        """Test formatting message when format string fails."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        # Mismatched format specifiers.
        result = logger._format_message("Value: %d", ("not_a_number",))
        assert "FORMAT ERROR" in result
        assert "not_a_number" in result

    def test_format_message_truncation_enabled(self):
        """Test formatting message with truncation enabled."""
        logger = EnhancedLogger(
            truncate=True, truncate_length=20, terminal=False, fileout_path=None
        )
        long_message = "A" * 100
        result = logger._format_message(long_message)
        assert "TRUNCATED" in result
        assert len(result) < 100 + 50  # Allow for truncation message.

    def test_format_message_truncation_disabled(self):
        """Test formatting message with truncation disabled."""
        logger = EnhancedLogger(
            truncate=False, truncate_length=20, terminal=False, fileout_path=None
        )
        long_message = "A" * 100
        result = logger._format_message(long_message)
        assert "TRUNCATED" not in result
        assert result == long_message

    def test_format_message_truncation_override(self):
        """Test formatting message with truncation parameter override."""
        logger = EnhancedLogger(
            truncate=True, truncate_length=5000, terminal=False, fileout_path=None
        )
        long_message = "A" * 100
        # Override with function parameter.
        result = logger._format_message(long_message, truncate=False)
        assert "TRUNCATED" not in result

    def test_format_message_truncate_length_override(self):
        """Test formatting message with truncate_length parameter override."""
        logger = EnhancedLogger(
            truncate=True, truncate_length=5000, terminal=False, fileout_path=None
        )
        long_message = "A" * 100
        # Override with function parameter.
        result = logger._format_message(long_message, truncate_length=10)
        assert "TRUNCATED" in result


class TestEnhancedLoggerLoggingMethods:
    """Tests for EnhancedLogger logging methods."""

    def test_debug_method(self, temp_log_file):
        """Test debug logging method."""
        logger = EnhancedLogger(
            level="DEBUG", terminal=False, fileout_path=temp_log_file
        )
        logger.debug("Debug message")
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "Debug message" in content

    def test_info_method(self, temp_log_file):
        """Test info logging method."""
        logger = EnhancedLogger(
            level="INFO", terminal=False, fileout_path=temp_log_file
        )
        logger.info("Info message")
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "Info message" in content

    def test_warning_method(self, temp_log_file):
        """Test warning logging method."""
        logger = EnhancedLogger(
            level="WARNING", terminal=False, fileout_path=temp_log_file
        )
        logger.warning("Warning message")
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "Warning message" in content

    def test_error_method(self, temp_log_file):
        """Test error logging method."""
        logger = EnhancedLogger(
            level="ERROR", terminal=False, fileout_path=temp_log_file
        )
        logger.error("Error message")
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "Error message" in content

    def test_critical_method(self, temp_log_file):
        """Test critical logging method."""
        logger = EnhancedLogger(
            level="CRITICAL", terminal=False, fileout_path=temp_log_file
        )
        logger.critical("Critical message")
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "Critical message" in content

    def test_logging_with_format_args(self, temp_log_file):
        """Test logging with format string arguments."""
        logger = EnhancedLogger(
            level="INFO", terminal=False, fileout_path=temp_log_file
        )
        logger.info("Value: %s, Count: %d", "test", 42)
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "Value: test, Count: 42" in content

    def test_logging_with_user_context(self, temp_log_file):
        """Test logging with user context."""
        logger = EnhancedLogger(
            level="INFO", terminal=False, fileout_path=temp_log_file
        )
        logger.info("Action", user_context={"uid": "user123"})
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "user123: Action" in content

    def test_logging_with_json_format(self, temp_log_file):
        """Test logging with JSON format."""
        logger = EnhancedLogger(
            level="INFO", terminal=False, fileout_path=temp_log_file
        )
        data = {"key": "value"}
        logger.info("Data: %s", data, json_format=True)
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert '"key": "value"' in content

    def test_logging_with_truncate_override(self, temp_log_file):
        """Test logging with truncate parameter override."""
        logger = EnhancedLogger(
            level="INFO",
            truncate=True,
            truncate_length=10,
            terminal=False,
            fileout_path=temp_log_file,
        )
        logger.info("Short message that would be truncated", truncate=False)
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "TRUNCATED" not in content

    def test_logging_with_truncate_length_override(self, temp_log_file):
        """Test logging with truncate_length parameter override."""
        logger = EnhancedLogger(
            level="INFO",
            truncate=True,
            truncate_length=10000,
            terminal=False,
            fileout_path=temp_log_file,
        )
        logger.info("A" * 100, truncate_length=10)
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "TRUNCATED" in content


class TestEnhancedLoggerGetMethods:
    """Tests for EnhancedLogger getter methods."""

    def test_get_logger(self):
        """Test get_logger method returns the underlying logger."""
        logger = EnhancedLogger(terminal=False, fileout_path=None)
        underlying = logger.get_logger()
        assert isinstance(underlying, logging.Logger)
        assert underlying is logger.logger

    def test_get_level(self):
        """Test get_level method returns current log level."""
        logger = EnhancedLogger(level="WARNING", terminal=False, fileout_path=None)
        level = logger.get_level()
        assert level == logging.WARNING

    def test_get_level_name(self):
        """Test get_level_name method returns level name string."""
        logger = EnhancedLogger(level="ERROR", terminal=False, fileout_path=None)
        level_name = logger.get_level_name()
        assert level_name == "ERROR"


class TestGetLoggerFunction:
    """Tests for the get_logger module function."""

    def test_get_logger_creates_instance(self):
        """Test get_logger creates a new instance on first call."""
        logger = get_logger(terminal=False, fileout_path=None)
        assert isinstance(logger, EnhancedLogger)

    def test_get_logger_returns_singleton(self):
        """Test get_logger returns the same instance on subsequent calls."""
        logger1 = get_logger(terminal=False, fileout_path=None)
        logger2 = get_logger(terminal=False, fileout_path=None)
        assert logger1 is logger2

    def test_get_logger_with_parameters(self):
        """Test get_logger with custom parameters."""
        logger = get_logger(
            name="test_logger",
            level="DEBUG",
            terminal=False,
            json_format=True,
            truncate_length=1000,
            truncate=False,
            use_colors=False,
            fileout_path=None,
            timezone="UTC",
        )
        assert logger.name == "test_logger"
        assert logger.level == "DEBUG"
        assert logger.json_format is True
        assert logger.truncate_length == 1000
        assert logger.truncate is False
        assert logger.use_colors is False
        assert logger.timezone == "UTC"

    def test_get_logger_reconfigures_on_subsequent_calls(self):
        """Test get_logger reconfigures on subsequent calls."""
        logger1 = get_logger(level="INFO", terminal=False, fileout_path=None)
        logger2 = get_logger(level="DEBUG", terminal=False, fileout_path=None)
        # Second call should reconfigure.
        assert logger2.level == "DEBUG"
        assert logger1 is logger2


class TestTimezoneUtilities:
    """Tests for timezone utility functions."""

    def test_get_available_timezones(self):
        """Test get_available_timezones returns a set of timezones."""
        timezones = get_available_timezones()
        assert isinstance(timezones, set)
        assert len(timezones) > 0
        # Check for some common timezones.
        assert "UTC" in timezones
        assert "America/New_York" in timezones
        assert "Europe/London" in timezones

    def test_is_valid_timezone_with_valid(self):
        """Test is_valid_timezone returns True for valid timezone."""
        assert is_valid_timezone("UTC") is True
        assert is_valid_timezone("America/New_York") is True
        assert is_valid_timezone("Europe/London") is True
        assert is_valid_timezone("Asia/Tokyo") is True

    def test_is_valid_timezone_with_invalid(self):
        """Test is_valid_timezone returns False for invalid timezone."""
        assert is_valid_timezone("Invalid/Timezone") is False
        assert is_valid_timezone("Not_A_Timezone") is False
        assert is_valid_timezone("") is False


class TestLoggerWithTimezone:
    """Tests for logger with timezone configuration."""

    def test_logger_with_utc_timezone(self, temp_log_file):
        """Test logger with UTC timezone."""
        logger = EnhancedLogger(
            level="INFO",
            timezone="UTC",
            terminal=False,
            fileout_path=temp_log_file,
        )
        logger.info("Test message")
        with open(temp_log_file, "r") as f:
            content = f.read()
        # Should contain UTC timezone indicator.
        assert "UTC" in content or "+0000" in content

    def test_logger_with_specific_timezone(self, temp_log_file):
        """Test logger with specific timezone."""
        logger = EnhancedLogger(
            level="INFO",
            timezone="America/New_York",
            terminal=False,
            fileout_path=temp_log_file,
        )
        logger.info("Test message")
        with open(temp_log_file, "r") as f:
            content = f.read()
        # Should contain timezone info.
        assert "Test message" in content


class TestLoggerFileOutput:
    """Tests for logger file output functionality."""

    def test_logs_written_to_file(self, temp_log_file):
        """Test that logs are written to file."""
        logger = EnhancedLogger(
            level="INFO",
            terminal=False,
            fileout_path=temp_log_file,
        )
        logger.info("File output test")
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "File output test" in content

    def test_multiple_logs_appended(self, temp_log_file):
        """Test that multiple logs are appended to file."""
        logger = EnhancedLogger(
            level="INFO",
            terminal=False,
            fileout_path=temp_log_file,
        )
        logger.info("First message")
        logger.info("Second message")
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "First message" in content
        assert "Second message" in content

    def test_file_contains_timestamp(self, temp_log_file):
        """Test that log file contains timestamp."""
        logger = EnhancedLogger(
            level="INFO",
            terminal=False,
            fileout_path=temp_log_file,
        )
        logger.info("Timestamp test")
        with open(temp_log_file, "r") as f:
            content = f.read()
        # Should contain date-like pattern.
        import re

        # Pattern for date like YYYY-MM-DD or time like HH:MM:SS.
        assert re.search(r"\d{4}-\d{2}-\d{2}", content) or re.search(
            r"\d{2}:\d{2}:\d{2}", content
        )

    def test_file_contains_level(self, temp_log_file):
        """Test that log file contains log level."""
        logger = EnhancedLogger(
            level="INFO",
            terminal=False,
            fileout_path=temp_log_file,
        )
        logger.info("Level test")
        with open(temp_log_file, "r") as f:
            content = f.read()
        assert "INFO" in content


class TestLoggerTerminalOutput:
    """Tests for logger terminal output functionality."""

    def test_terminal_output_with_colors(self, capsys):
        """Test terminal output includes colors when enabled."""
        logger = EnhancedLogger(
            level="INFO",
            terminal=True,
            fileout_path=None,
            use_colors=True,
        )
        logger.info("Colored output test")
        captured = capsys.readouterr()
        # Should contain ANSI color codes.
        assert "\033[" in captured.err

    def test_terminal_output_without_colors(self, capsys):
        """Test terminal output without colors when disabled."""
        logger = EnhancedLogger(
            level="INFO",
            terminal=True,
            fileout_path=None,
            use_colors=False,
        )
        logger.info("No color output test")
        captured = capsys.readouterr()
        # Should not contain ANSI color codes.
        assert "\033[" not in captured.err
        assert "No color output test" in captured.err

"""Enhanced logging module with authentication support."""

import json
import logging
from typing import Any, ClassVar, Dict, Optional, Tuple


# ANSI color codes for colored terminal output
class Colors:
    """ANSI color codes for terminal colored output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages based on their level."""

    # Color mapping for different log levels
    LEVEL_COLORS = {
        logging.DEBUG: Colors.BRIGHT_BLUE,
        logging.INFO: Colors.BRIGHT_GREEN,
        logging.WARNING: Colors.BRIGHT_YELLOW,
        logging.ERROR: Colors.BRIGHT_RED,
        logging.CRITICAL: f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}",
    }

    def __init__(self, fmt=None, datefmt=None, style="%", use_colors=True):
        """Initialize the ColoredFormatter.

        Args:
            fmt: Format string for the log message.
            datefmt: Format string for the date/time.
            style: Style of the format string (%, {, or $).
            use_colors: Whether to use colors in log messages.
        """
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors

    def format(self, record):
        """Format the log record with appropriate colors.

        Args:
            record: The log record to format.

        Returns:
            Formatted log message with color codes if enabled.
        """
        # Save the original format
        original_format = self._style._fmt

        if self.use_colors:
            # Get the color for the current log level
            level_color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)

            # Colorize the level name
            record.levelname = f"{level_color}{record.levelname}{Colors.RESET}"

            # Colorize the filename and line number
            file_info = f"{Colors.CYAN}%(filename)s:%(lineno)d{Colors.RESET}"
            self._style._fmt = original_format.replace(
                "%(filename)s:%(lineno)d", file_info
            )

            # Add bold to timestamp
            time_info = f"{Colors.BOLD}%(asctime)s{Colors.RESET}"
            self._style._fmt = self._style._fmt.replace("%(asctime)s", time_info)

        # Format the record
        result = super().format(record)

        # Restore the original format
        self._style._fmt = original_format

        return result


class EnhancedLogger:
    """Enhanced logging mechanism with authentication context.

    Implemented as a singleton to ensure only one logger instance exists
    across the whole program.

    Stacklevel 2 is used to show the source of the log call and not the logger
    method itself.

    Example usage:
        ```python
        logger = get_logger(name="my_module")
        logger.info("Processing started.")

        # With user context
        user_info = {"uid": "user123", "email": "user@example.com"}
        logger.info("User action completed successfully.", user_info)

        # With format strings
        logger.info("Processing item %s with priority %d", item_id, priority)

        # Format strings with user context
        logger.info("User %s completed action %s", username, action, user_info)

        # With JSON formatting of args
        complex_data = {"results": [1, 2, 3], "metadata": {"source": "API"}}
        logger.info("Received data", complex_data, json_format=True)

        or

        logger.info("Received data %s", complex_data, json_format=True)

        # With truncation explicitly set to False for long messages
        logger.info("Very long message that should not be truncated", truncate=False)

        # In FastAPI endpoints with dependency injection
        @app.get("/endpoint")
        async def endpoint(logger: EnhancedLogger = Depends(get_authenticated_logger)):
            logger.info("Processing authenticated request.")
            return {"status": "success"}
        ```

    Features:
    - Includes timestamp in logs
    - Includes user ID if authenticated
    - Shows file name and line number of the log call
    - Can be used both with and without authentication context
    - Supports format strings with %s, %d, etc.
    - Optional JSON formatting for complex data structures
    - Automatic truncation of long messages with option to disable
    - Colored terminal output for better readability
    - Singleton implementation to ensure only one logger instance exists
    """

    # Class variable to store the singleton instance
    _instance: ClassVar[Optional["EnhancedLogger"]] = None
    _initialized: ClassVar[bool] = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of EnhancedLogger exists."""
        if cls._instance is None:
            cls._instance = super(EnhancedLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        name: str = None,
        level: str = "INFO",
        terminal: bool = True,
        fileout_path: str = "logs/app.log",
        json_format: bool = False,
        truncate_length: int = 5000,
        truncate: bool = True,
        use_colors: bool = True,
    ) -> None:
        """Initialize enhanced logging mechanism.

        Args:
            name: Name of the logger. Default is None.
            level: Logging level. Defaults to "INFO".
            fileout_path: Path to output logs.
            terminal: Output log to terminal. Defaults to True.
            json_format: Whether to format args as JSON. Default is False.
            truncate_length: Maximum length for log messages before truncation.
                Default is 5000.
            truncate: Whether to enable automatic truncation. Default is True.
            use_colors: Whether to use colors in terminal output. Default is True.
        """
        # Skip initialization if already initialized.
        if self._initialized:
            return

        self.name = name
        self.level = level
        self.terminal = terminal
        self.fileout_path = fileout_path
        self.json_format = json_format
        self.truncate_length = truncate_length
        self.truncate = truncate
        self.use_colors = use_colors

        self.logger = logging.getLogger(self.name)
        self.logger.propagate = False  # Deduplicate default logging.
        self.logger.setLevel(self.level)

        # Format includes timestamp, level, filename, line number, and message
        # User ID will be included in the message when available.
        base_format = "%(levelname)s:[%(asctime)s]%(filename)s:%(lineno)d:%(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        # Clear existing handlers to avoid duplicates.
        if self.logger.handlers:
            self.logger.handlers.clear()

        if self.fileout_path:
            # Regular formatter for file output (no colors)
            file_formatter = logging.Formatter(base_format, datefmt=date_format)
            file_handler = logging.FileHandler(self.fileout_path, "a")
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        if self.terminal:
            # Colored formatter for terminal output
            terminal_formatter = ColoredFormatter(
                fmt=base_format, datefmt=date_format, use_colors=self.use_colors
            )
            terminal_handler = logging.StreamHandler()
            terminal_handler.setFormatter(terminal_formatter)
            self.logger.addHandler(terminal_handler)

        # Mark as initialized
        self._initialized = True

    def reconfigure(
        self,
        name: str = None,
        level: str = None,
        terminal: bool = None,
        fileout_path: str = None,
        json_format: bool = None,
        truncate_length: int = None,
        truncate: bool = None,
        use_colors: bool = None,
    ) -> None:
        """Reconfigure the logger instance.

        Args:
            name: Name of the logger. Default is None.
            level: Logging level. Defaults to None (unchanged).
            fileout_path: Path to output logs.
            terminal: Output log to terminal. Defaults to None (unchanged).
            json_format: Whether to format args as JSON. Default is None (unchanged).
            truncate_length: Maximum length for log messages before truncation.
            truncate: Whether to enable automatic truncation. Default is None (unchanged).
            use_colors: Whether to use colors in terminal output. Default is None (unchanged).
        """
        # Update only specified parameters
        if name is not None:
            self.name = name
        if level is not None:
            self.level = level
            self.logger.setLevel(self.level)
        if terminal is not None:
            self.terminal = terminal
        if fileout_path is not None:
            self.fileout_path = fileout_path
        if json_format is not None:
            self.json_format = json_format
        if truncate_length is not None:
            self.truncate_length = truncate_length
        if truncate is not None:
            self.truncate = truncate
        if use_colors is not None:
            self.use_colors = use_colors

        # Reconfigure handlers
        base_format = "%(levelname)s:[%(asctime)s]%(filename)s:%(lineno)d:%(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        # Clear existing handlers to avoid duplicates
        if self.logger.handlers:
            self.logger.handlers.clear()

        if self.fileout_path:
            # Regular formatter for file output (no colors)
            file_formatter = logging.Formatter(base_format, datefmt=date_format)
            file_handler = logging.FileHandler(self.fileout_path, "a")
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        if self.terminal:
            # Colored formatter for terminal output
            terminal_formatter = ColoredFormatter(
                fmt=base_format, datefmt=date_format, use_colors=self.use_colors
            )
            terminal_handler = logging.StreamHandler()
            terminal_handler.setFormatter(terminal_formatter)
            self.logger.addHandler(terminal_handler)

    def _format_message(
        self,
        message: str,
        args: Tuple[Any, ...] = None,
        user_context: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        truncate: bool = None,
        truncate_length: int = None,
    ) -> str:
        """Format message with format strings and user ID if available.

        Args:
            message: The log message, possibly with format specifiers.
            args: Optional arguments for format string substitution.
            user_context: Context can really contain anything.
            json_format: Whether to format args as JSON. Defaults to False.
            truncate: Whether to truncate the message. If None, uses the
                instance default.
            truncate_length: Maximum length for log messages before truncation.
                If None, uses the instance default.

        Returns:
            Formatted message with user ID if available and format string
            substitutions.
        """
        formatted_args = args

        # Format args as JSON if requested.
        if json_format and args:
            try:
                formatted_args = tuple(
                    json.dumps(arg, indent=4, default=str) for arg in args
                )
            except (TypeError, ValueError) as e:
                # If JSON formatting fails, append error to message.
                return f"{message} - [JSON FORMAT ERROR: {str(e)}] - Args: {args}"

        # Apply string formatting if args are provided.
        if formatted_args:
            try:
                message = message % formatted_args
            except (TypeError, ValueError) as e:
                # If formatting fails, append args to message.
                message = (
                    f"{message} - [FORMAT ERROR: {str(e)}] - Args: {formatted_args}"
                )

        # Add user context if available.
        if user_context and "uid" in user_context:
            message = f"{user_context['uid']}: {message}"

        # Use function parameters first, then fall back to instance variables.
        should_truncate: bool = truncate if truncate is not None else self.truncate
        max_length: int = (
            truncate_length if truncate_length is not None else self.truncate_length
        )

        # Apply truncate and length if specified.
        if should_truncate and len(message) > max_length:
            truncated_message: str = message[:max_length]
            return f"{truncated_message}... [TRUNCATED, LENGTH: {len(message)}]"

        return message

    def debug(
        self,
        message: str,
        *args: Any,
        user_context: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        truncate: bool = None,
        truncate_length: int = None,
    ) -> None:
        """Log a debug message.

        Args:
            message: Message to log, may contain format specifiers.
            *args: Variable arguments for format string substitution.
            user_context: Optional user authentication context. If the last arg
                is a dict, it will be treated as user_context only if explicitly
                named.
            json_format: Whether to format args as JSON. Defaults to False.
            truncate: Whether to truncate the message. If None, uses the
                instance default.
            truncate_length: Maximum length for log messages before truncation.
                If None, uses the instance default.
        """
        formatted_message = self._format_message(
            message, args, user_context, json_format, truncate, truncate_length
        )
        self.logger.debug(formatted_message, stacklevel=2)

    def info(
        self,
        message: str,
        *args: Any,
        user_context: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        truncate: bool = None,
        truncate_length: int = None,
    ) -> None:
        """Log an info message.

        Args:
            message: Message to log, may contain format specifiers.
            *args: Variable arguments for format string substitution.
            user_context: Optional user authentication context. If the last arg
                is a dict, it will be treated as user_context only if explicitly
                named.
            json_format: Whether to format args as JSON. Defaults to False.
            truncate: Whether to truncate the message. If None, uses the
                instance default.
            truncate_length: Maximum length for log messages before truncation.
                If None, uses the instance default.
        """
        formatted_message = self._format_message(
            message, args, user_context, json_format, truncate, truncate_length
        )
        self.logger.info(formatted_message, stacklevel=2)

    def warning(
        self,
        message: str,
        *args: Any,
        user_context: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        truncate: bool = None,
        truncate_length: int = None,
    ) -> None:
        """Log a warning message.

        Args:
            message: Message to log, may contain format specifiers.
            *args: Variable arguments for format string substitution.
            user_context: Optional user authentication context. If the last arg
                is a dict, it will be treated as user_context only if explicitly
                named.
            json_format: Whether to format args as JSON. Defaults to False.
            truncate: Whether to truncate the message. If None, uses the
                instance default.
            truncate_length: Maximum length for log messages before truncation.
                If None, uses the instance default.
        """
        formatted_message = self._format_message(
            message, args, user_context, json_format, truncate, truncate_length
        )
        self.logger.warning(formatted_message, stacklevel=2)

    def error(
        self,
        message: str,
        *args: Any,
        user_context: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        truncate: bool = None,
        truncate_length: int = None,
    ) -> None:
        """Log an error message.

        Args:
            message: Message to log, may contain format specifiers.
            *args: Variable arguments for format string substitution.
            user_context: Optional user authentication context. If the last arg
                is a dict, it will be treated as user_context only if explicitly
                named.
            json_format: Whether to format args as JSON. Defaults to False.
            truncate: Whether to truncate the message. If None, uses the
                instance default.
            truncate_length: Maximum length for log messages before truncation.
                If None, uses the instance default.
        """
        formatted_message = self._format_message(
            message, args, user_context, json_format, truncate, truncate_length
        )
        self.logger.error(formatted_message, stacklevel=2)

    def critical(
        self,
        message: str,
        *args: Any,
        user_context: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        truncate: bool = None,
        truncate_length: int = None,
    ) -> None:
        """Log a critical message.

        Args:
            message: Message to log, may contain format specifiers.
            *args: Variable arguments for format string substitution.
            user_context: Optional user authentication context. If the last arg
                is a dict, it will be treated as user_context only if explicitly
                named.
            json_format: Whether to format args as JSON. Defaults to False.
            truncate: Whether to truncate the message. If None, uses the
                instance default.
            truncate_length: Maximum length for log messages before truncation.
                If None, uses the instance default.
        """
        formatted_message = self._format_message(
            message, args, user_context, json_format, truncate, truncate_length
        )
        self.logger.critical(formatted_message, stacklevel=2)

    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance.

        Returns:
            The logger instance.
        """
        return self.logger

    def get_level(self) -> int:
        """Get the current logging level.

        Returns:
            The current logging level as a logging module constant (e.g., logging.DEBUG, logging.INFO).

        Example:

            ```python
            logger = get_logger()
            if logger.get_level() == logging.INFO:
                print("Logger is at INFO level")
            ```
        """
        return self.logger.level

    def get_level_name(self) -> str:
        """Get the current logging level as a string.

        Returns:
            The current logging level name (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
        """
        return logging.getLevelName(self.logger.level)


# Global logger instance (singleton)
_logger_instance = None


# Create a factory function to get a logger with authentication context.
def get_logger(
    name: str = None,
    level: str = "INFO",
    terminal: bool = True,
    json_format: bool = False,
    truncate_length: int = 10000,
    truncate: bool = True,
    fileout_path: str = None,
    use_colors: bool = True,
) -> EnhancedLogger:
    """Get or create the singleton EnhancedLogger instance.

    On first call, this creates and configures the logger.
    On subsequent calls, it returns the existing instance.
    If configuration parameters are provided on subsequent calls,
    the logger will be reconfigured with the new parameters.

    Args:
        name: Name of the logger. Some arbitrary string name. Default is None.
        level: Logging level. Defaults to "INFO".
        terminal: Output log to terminal. Defaults to True.
        json_format: Whether to format args as JSON. Default is False.
        truncate_length: Maximum length for log messages before truncation.
        truncate: Whether to enable automatic truncation. Default is True.
        use_colors: Whether to use colors in terminal output. Default is True.
        fileout_path: Path to output logs. Default is None.
    Returns:
        The singleton EnhancedLogger instance.
    """
    global _logger_instance

    if _logger_instance is None:
        # First call: create and configure the logger
        _logger_instance = EnhancedLogger(
            name=name,
            level=level,
            terminal=terminal,
            json_format=json_format,
            truncate_length=truncate_length,
            truncate=truncate,
            use_colors=use_colors,
            fileout_path=fileout_path,
        )
    else:
        # Subsequent calls: reconfigure if parameters are provided
        _logger_instance.reconfigure(
            name=name,
            level=level,
            terminal=terminal,
            json_format=json_format,
            truncate_length=truncate_length,
            truncate=truncate,
            use_colors=use_colors,
            fileout_path=fileout_path,
        )

    return _logger_instance

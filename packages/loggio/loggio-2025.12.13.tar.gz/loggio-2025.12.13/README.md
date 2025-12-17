# Enhanced Logger Loggio

A comprehensive logging utility for project that provides:

- Timestamp information in logs
- User ID tracking for authenticated requests
- File name and line number of the log call
- Clean and consistent log formatting
- Multiple usage patterns for different scenarios

## Features

- **Contextual Information**: Every log includes timestamp, log level, file
  name, and line number
- **Authentication Awareness**: Can include user ID in logs when available
- **Format String Support**: Supports Python's standard string formatting with
  %s, %d, etc.
- **Flexible Configuration**: Configurable output destination (terminal and/or
  file)
- **Consistent API**: Familiar logging methods (debug, info, warning, error,
  critical)

## Installation

### From PyPI (Recommended)

```bash
pip install loggio
```

Then import in your code:

```python
from loggio import get_logger
```

### From Source

To use standalone, use as a fork.

To get updates, use as a submodule.

#### As standalone

Go to inside your project.

Clone the repository:

```bash
git clone https://github.com/xcollantes/loggio loggio
```

#### As submodule to existing repo

Go to where you want to dependency.

Clone the repository as submodule:

`loggio` must be maintained since Python import statements don't work
work hyphens.

```bash
git submodule add https://github.com/xcollantes/loggio loggio
```

#### Cloning your project that contains submodules

Clone the repository with submodules:

```bash
git clone --recursive https://github.com/xcollantes/my-project-with-submodules
```

Remember `--recursive` for submodules.

If you clone without --recursive:

```bash
git submodule update --init --recursive
```

#### Create and Activate Virtual Environment

```bash
# Create virtual environment.
python3 -m venv env

# Activate virtual environment.
# On macOS/Linux:
source env/bin/activate

# On Windows:
# venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Environment Configuration

Create a `.env` file in the project root with the required environment
variables. The following variables are used by the application:

#### Running the Application

#### Basic Usage

```bash
python3 main.py
```

## Usage Examples

### Basic Usage (No Authentication)

For utility functions, background tasks, or non-authenticated endpoints:

```python
from loggio import get_logger

# Create a logger instance.
logger = get_logger(name="module.name")

# Log messages with different levels
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
```

Output example:

```
INFO:2023-05-01 14:30:45:example.py:24:This is an info message.
```

### Using Format Strings

The logger supports Python's standard string formatting:

```python
from loggio import get_logger

logger = get_logger(name="module.formatter")

# Using format strings
item_id = "A123"
priority = 2
logger.info("Processing item %s with priority %d", item_id, priority)
```

Output example:

```
INFO:2023-05-01 14:31:22:formatter.py:15:Processing item A123 with priority 2
```

### Usage with User Context

When you have authentication info:

```python
from loggio import get_logger

# Create a logger instance.
logger = get_logger(name="module.auth")

# Get user info from somewhere (e.g., decoded token)
user_info = {"uid": "user123", "email": "user@example.com"}

# Log with user context
logger.info("User performed an action.", user_context=user_info)
```

Output example:

```
INFO:2023-05-01 14:32:10:auth_service.py:45:user123: User performed an action.
```

### Format Strings with User Context

Combining format strings with user context:

```python
logger.info("Processing file %s for action %s", filename, action, user_context=user_info)
```

### Error Handling with Logging

```python
try:
    # Some risky operation
    result = perform_risky_operation()
    logger.info(f"Operation successful: {result}")
except Exception as e:
    logger.error(f"Operation failed: {str(e)}")
    # Handle or re-raise as appropriate
```

## Configuration Options

When creating a logger instance, you can configure:

- `name`: Logger name for filtering and organization (e.g., "api.auth",
  "service.processor")
- `level`: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) - defaults
  to "INFO"
- `fileout`: Whether to write logs to a file (default: False)
- `terminal`: Whether to output logs to the terminal/console (default: True)
- `fileout_path`: Path for log file if `fileout` is True (default:
  "logs/app.log")

Example with custom configuration:

```python
logger = get_logger(
    name="batch.processor",
    level="DEBUG",
    fileout=True,
    fileout_path="logs/batch_processor.log",
    terminal=True
)
```

## Log Format

The logger produces logs in the following format:

```
LEVEL:TIMESTAMP:FILENAME:LINE_NUMBER:MESSAGE
```

For example:

```
INFO:2023-05-01 14:35:22:auth_routes.py:28:user123: Processing protected resource request
```

## Best Practices

1. Use a hierarchical naming scheme for loggers (e.g., `api.auth`,
   `service.processor`)
2. Include meaningful context in log messages
3. Use the appropriate log level for different scenarios:
   - DEBUG: Detailed information for debugging
   - INFO: Confirmation that things are working as expected
   - WARNING: Something unexpected happened, but the application can continue
   - ERROR: A more serious problem that prevented a function from working
   - CRITICAL: A very serious error that might prevent the program from
     continuing
4. Include user context when available for better traceability
5. Include error details when logging exceptions

## Implementation Details

The Enhanced Logger builds on Python's built-in logging module with custom
formatting and context handling. It uses `stacklevel=2` to ensure the correct
file and line number are recorded in the logs rather than showing the logger
implementation file itself.

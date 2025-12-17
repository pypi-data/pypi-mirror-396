"""Demo the enhanced logger."""

from src.enhanced_logger import EnhancedLogger, get_logger

logging: EnhancedLogger = get_logger(name="logging_test")


logging.info("Hello, world!")

# How truncating messages works.
long_message = "Hello, world!" * 100
logging.info("Show truncated message: %s", long_message)
logging.info(
    "Show truncated message with length specified: %s",
    long_message,
    truncate_length=50,
)
logging.info(
    "Show full message with no truncation: %s",
    long_message,
    truncate=False,
)

# How json formatting works.
json_message: dict = {"key": "value", "key2": "value2", "key3": "value3"}
logging.info("Demo of json message with no format: %s", json_message)
logging.info("Demo of json message with format: %s", json_message, json_format=True)

# How debug, warning, error, and critical messages work.
logging.debug("This is a debug message.")
logging.warning("This is a warning message.")
logging.error("This is an error message.")
logging.critical("This is a critical message.")

# How context works.
# You can add to context and alter the logger to append to the message.
logging.info("See UID on the left.", user_context={"uid": "1234567890"})

# You can also set variables for the logger at the instance level.
logging.truncate = True
logging.truncate_length = 5
logging.info("Hello, world!")

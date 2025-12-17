"""Demo the enhanced logger."""

from src.enhanced_logger import (
    EnhancedLogger,
    get_available_timezones,
    get_logger,
    is_valid_timezone,
)

logging: EnhancedLogger = get_logger(name="logging_test")


logging.info("Hello, world!")

# How truncating messages works.
long_message = "The path of the righteous man is beset on all sides by the inequities of the selfish and the tyranny of evil men."
logging.info("Show truncated message: %s", long_message)
logging.info(
    "Show truncated message with length specified: %s",
    long_message,
    truncate_length=100,
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

# How timezone works.
# Reset truncate for clearer output.
logging.truncate_length = 10000

# Get all available IANA timezones.
timezones = get_available_timezones()
logging.info("Total IANA timezones available: %d", len(timezones))

# Validate a timezone before using it.
tz_to_check = "America/New_York"
if is_valid_timezone(tz_to_check):
    logging.info("Timezone %s is valid.", tz_to_check)

# Invalid timezone abbreviations.
if not is_valid_timezone("PST"):
    logging.warning("PST is not valid. Use America/Los_Angeles instead.")

# Change timezone to UTC.
logging = get_logger(timezone="UTC")
logging.info("This message is logged in UTC timezone.")

# Change timezone to Tokyo.
logging = get_logger(timezone="Asia/Tokyo")
logging.info("This message is logged in Tokyo timezone.")

# Change timezone to New York.
logging = get_logger(timezone="America/New_York")
logging.info("This message is logged in New York timezone.")

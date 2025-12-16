import datetime
import json
import logging
import logging.handlers
import os


class JsonFormatter(logging.Formatter):
    """Formatter that outputs log records as JSON strings, including extra
    attributes.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, datetime.timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        # Include any extra fields added to the LogRecord (e.g., via LoggerAdapter)
        standard_attrs = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                # If the key is 'extra' and contains a dict, merge its items
                if key == "extra" and isinstance(value, dict):
                    for ek, ev in value.items():
                        log_record[ek] = ev
                else:
                    log_record[key] = value
        return json.dumps(log_record, indent=2)


class ColorFormatter(logging.Formatter):
    """Formatter that adds ANSI color codes to console log messages based on level."""

    LEVEL_COLORS = {
        "DEBUG": "\033[0;36m",  # cyan
        "INFO": "\033[0;32m",  # green
        "WARNING": "\033[0;33m",  # yellow
        "ERROR": "\033[0;31m",  # red
        "CRITICAL": "\033[0;35m",  # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        color = self.LEVEL_COLORS.get(record.levelname, self.RESET)
        return f"{color}{msg}{self.RESET}"


def get_logger(name: str = "app") -> logging.Logger:
    """Create and configure a logger with rotating file handler and JSON output.

    The log directory and level can be overridden via environment variables:
    LOG_DIR (default: "logs") and LOG_LEVEL (default: "INFO").
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    # Generate a unique log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"app_{timestamp}.log"
    log_path = os.path.join(log_dir, log_filename)

    # Use FileHandler to create a new file for each run/process
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)
    return logger


# Export a module‑level logger for convenient imports
logger = get_logger()

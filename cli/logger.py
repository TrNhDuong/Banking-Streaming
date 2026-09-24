"""
Logging configuration for the CLI.

Provides structured logging with readable levels and support for
verbose/debug mode and optional log file outputs.
"""
import logging
import os
import sys

# Custom format for console output
CONSOLE_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class CliFormatter(logging.Formatter):
    """Clean formatter tailored for CLI operator feedback."""

    PREFIXES = {
        logging.DEBUG: "[DEBUG]",
        logging.INFO: "[INFO]",
        logging.WARNING: "[WARN]",
        logging.ERROR: "[ERROR]",
        logging.CRITICAL: "[FATAL]",
    }

    def format(self, record: logging.LogRecord) -> str:
        prefix = self.PREFIXES.get(record.levelno, "[INFO]")
        time_str = self.formatTime(record, DATE_FORMAT)
        return f"{time_str} {prefix} {record.getMessage()}"


def setup_cli_logging(verbose: bool = False, log_file: str | None = None) -> logging.Logger:
    """Initialize root CLI logger.
    
    Args:
        verbose: If True, set log level to DEBUG. Otherwise INFO (or from LOG_LEVEL).
        log_file: Optional file path to mirror logs to disk.
    """
    env_level = os.getenv("LOG_LEVEL", "").upper()
    if verbose:
        level = logging.DEBUG
    elif env_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        level = getattr(logging, env_level)
    else:
        level = logging.INFO

    root = logging.getLogger("cli")
    root.setLevel(level)

    # Clear existing handlers to avoid duplicates
    root.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(CliFormatter())
    root.addHandler(console_handler)

    # Optional file handler
    file_path = log_file or os.getenv("CLI_LOG_FILE")
    if file_path:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT, datefmt=DATE_FORMAT))
        root.addHandler(file_handler)

    return root


def get_logger(name: str = "cli") -> logging.Logger:
    """Get a logger namespaced under 'cli'."""
    if name == "cli" or name.startswith("cli."):
        return logging.getLogger(name)
    return logging.getLogger(f"cli.{name}")

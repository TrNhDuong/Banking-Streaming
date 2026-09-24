import logging
import os
import sys


def setup_logging() -> logging.Logger:
    """Configure structured logging for the transaction generator service."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    return logging.getLogger("transaction-generator")

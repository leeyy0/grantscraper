"""Configuration management."""

import logging
import os
import sys

from dotenv import load_dotenv

# Load environment variables from a .env file in the project root
load_dotenv()

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("DB_URL environment variable 'DB_URL' is not set")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging():
    """Configure logging for the application."""
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Optionally add file handler
    log_file = os.getenv("LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set log levels for third-party libraries to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return root_logger

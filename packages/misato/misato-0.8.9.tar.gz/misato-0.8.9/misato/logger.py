"""
misato.logger - Application logging module

Provides a unified logging configuration and a global logger instance.
Features:
- Dual output to console and file
- Automatic daily log rotation with retention of 30 days
- Log level configurable via environment variable
- Optional JSON structured logging for production environments
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


# ==================== Configuration Constants ====================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

DEFAULT_LOG_LEVEL = os.getenv("MISATO_LOG_LEVEL", "INFO").upper()
JSON_LOGGING = os.getenv("MISATO_JSON_LOG", "0") == "1"  # Enable JSON format if set to "1"


# ==================== Optional JSON Formatter ====================

class JsonFormatter(logging.Formatter):
    """Simple structured JSON log formatter"""
    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime

        log_record = {
            "time": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


# ==================== Logger Factory Function ====================

def get_logger(
    name: str = "misato",
    *,
    level: Optional[str] = None,
    json_format: Optional[bool] = None,
) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name, defaults to "misato"
        level: Log level (e.g., "DEBUG", "INFO"). If None, uses MISATO_LOG_LEVEL env var or defaults to INFO
        json_format: Whether to use JSON output. If None, determined by MISATO_JSON_LOG env var

    Returns:
        A fully configured logging.Logger instance
    """
    logger = logging.getLogger(name)

    # Prevent adding handlers multiple times (critical for repeated imports)
    if logger.handlers:
        logger.debug("Logger already initialized, returning existing instance")
        return logger

    effective_level = level or DEFAULT_LOG_LEVEL
    logger.setLevel(effective_level)

    # Choose formatter
    use_json = json_format if json_format is not None else JSON_LOGGING
    if use_json:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "misato - %(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # ==================== Console Handler ====================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(effective_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ==================== Rotating File Handler ====================
    rotating_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "misato.log",
        when="midnight",          # Rotate at midnight
        interval=1,
        backupCount=30,           # Keep logs for the last 30 days
        encoding="utf-8",
        delay=False,
    )
    rotating_handler.setLevel("DEBUG")  # Record all levels to file
    rotating_handler.setFormatter(formatter)
    logger.addHandler(rotating_handler)

    logger.info(
        f"Logger initialized | Level: {effective_level} | JSON: {use_json} | File: {rotating_handler.baseFilename}"
    )

    return logger


# ==================== Global Default Logger (Backward Compatible) ====================

logger = get_logger()


# ==================== Optional: Reconfiguration Function ====================

def reconfigure_logger(level: str = "INFO", json_format: bool = False) -> None:
    """
    Reconfigure the global logger at runtime (e.g., based on CLI flags).

    Useful for enabling debug mode dynamically.
    """
    global logger
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    logger = get_logger(level=level, json_format=json_format)
"""Application logging setup and the shared print_logging helper."""

import inspect
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("app")
    if logger.handlers:  # already configured (e.g. reload), avoid duplicates
        return logger

    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.setLevel(settings.log_level)
    logger.propagate = False
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def print_logging(level: str, message: str) -> None:
    """Log a message at the given level with the caller's module and line."""
    logger = setup_logging()

    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None
    process_name = caller.f_globals.get("__name__", "app") if caller else "app"
    line = caller.f_lineno if caller else 0
    del frame
    if process_name == "__main__" and caller is not None:
        process_name = Path(caller.f_code.co_filename).stem
    message = f"[{process_name}] Line {line}: {message}"

    level = level.strip().lower()
    exc_info = level in {"error", "critical"} and sys.exc_info()[0] is not None

    if level == "debug":
        logger.debug(message, exc_info=exc_info)
    elif level == "info":
        logger.info(message, exc_info=exc_info)
    elif level == "warning":
        logger.warning(message, exc_info=exc_info)
    elif level == "error":
        logger.error(message, exc_info=exc_info)
    elif level == "critical":
        logger.critical(message, exc_info=exc_info)
    else:
        logger.info("N/A - %s", message)

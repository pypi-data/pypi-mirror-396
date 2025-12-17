"""
Logging Configuration for ChronoEEG

Provides centralized logging setup with customizable handlers and formatters.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "chronoeeg",
    level: str = "INFO",
    log_to_file: bool = False,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
    date_format: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers.

    Parameters
    ----------
    name : str
        Logger name (default: "chronoeeg")
    level : str
        Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_to_file : bool
        Whether to log to a file
    log_file : Path, optional
        Path to log file (required if log_to_file is True)
    format_string : str, optional
        Custom format string for log messages
    date_format : str, optional
        Custom date format string

    Returns
    -------
    logging.Logger
        Configured logger instance

    Examples
    --------
    >>> logger = setup_logger("chronoeeg", level="DEBUG")
    >>> logger.info("Starting analysis...")
    >>> logger.debug("Processing epoch 1/100")
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(format_string, datefmt=date_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        if log_file is None:
            raise ValueError("log_file must be specified when log_to_file is True")

        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler (max 10MB, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "chronoeeg") -> logging.Logger:
    """
    Get or create a logger instance.

    Parameters
    ----------
    name : str
        Logger name (default: "chronoeeg")

    Returns
    -------
    logging.Logger
        Logger instance

    Examples
    --------
    >>> logger = get_logger("chronoeeg.io")
    >>> logger.info("Loading data...")
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.

    Examples
    --------
    >>> class MyProcessor(LoggerMixin):
    ...     def process(self):
    ...         self.logger.info("Processing started")
    ...         # do work
    ...         self.logger.info("Processing complete")
    """

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(f"chronoeeg.{self.__class__.__name__}")
        return self._logger

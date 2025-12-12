"""
Configure and standardize logging for console output.

This module provides a configurable logger class that sets up a stream logger
with a consistent format and suppresses noisy loggers such as 'py4j'. Use this
to ensure readable and uniform logging output in scripts and applications.

Classes
-------
StreamLogger
    Set up and manage a logger with a standard format and level.
"""

import logging
import sys


class StreamLogger:
    """
    Configure and manage a logger for console output with a standardized format.

    Set up a stream logger with a consistent format and suppress noisy loggers such as 'py4j'.
    Use this class to ensure readable and uniform logging output in scripts and applications.

    Parameters
    ----------
    name : str
        Specify the name of the logger.
    level : int, optional
        Set the logging level (e.g., logging.INFO, logging.DEBUG). Default is logging.INFO.

    Attributes
    ----------
    name : str
        The name of the logger.
    level : int
        The logging level.
    formatter : logging.Formatter
        The formatter used for log messages.
    logger : logging.Logger
        The configured logger instance.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize the logger with a specified name and logging level.

        Parameters
        ----------
        name : str
            Specify the name of the logger.
        level : int, optional
            Set the logging level (e.g., logging.INFO, logging.DEBUG). Default is logging.INFO.

        Notes
        -----
        Set up a custom formatter and configure the logger for console output.
        """
        self.name = name
        self.level = level
        # Custom formatter
        self.formatter = logging.Formatter(fmt=self.get_std_fmt(), datefmt="%Y-%m-%d %H:%M:%S")
        self.logger = self._setup_logger()

    def get_std_fmt(self) -> str:
        """
        Return the standard format string for log messages.

        Returns
        -------
        str
            Format string including timestamp, logger name, level, and message.
        """

        return "%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s"

    def _setup_logger(self) -> logging.Logger:
        """
        Configure and return a logger instance with a stream handler.

        Clear existing handlers, disable propagation, and apply a custom formatter.
        Suppress the 'py4j' logger to reduce console noise.

        Returns
        -------
        logging.Logger
            Configured logger instance.
        """
        # Logger configuration
        logger = logging.getLogger(self.name)

        # Sets log level to INFO (default)
        logger.setLevel(self.level)

        # Clears existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        # Disable propagation to prevent double logging
        logger.propagate = False

        # Stream handler for console output
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        logger.addHandler(handler)

        # Suppress py4j logger to reduce noise (pyspark related)
        logging.getLogger("py4j").setLevel(logging.WARNING)

        return logger


# eof

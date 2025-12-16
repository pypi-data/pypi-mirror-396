import logging
import sys
from typing import Optional, Callable

# Type alias for a logger factory function
type LoggerFactory = Callable[[Optional[str]], logging.Logger]

# Internal variable to hold a custom logger factory
_custom_logger_factory: Optional[LoggerFactory] = None

def register_logger_factory(factory: LoggerFactory):
    """
    Register a custom logger factory function. This function should accept a name (str or None)
    and return a logger instance (e.g., structlog or standard logger).
    """
    global _custom_logger_factory
    _custom_logger_factory = factory

def get_logger(name: str = None) -> logging.Logger:
    """
    Returns a logger configured to output to the console, or uses a registered custom logger factory.
    If no name is provided, uses the root logger.
    """
    if _custom_logger_factory is not None:
        return _custom_logger_factory(name)
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger

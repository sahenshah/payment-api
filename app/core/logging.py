"""Structured logging configuration using structlog."""
import logging
import structlog


def configure_logging() -> None:
    """Configure structlog for JSON output.
    
    Sets up a processing pipeline that:
    - Adds log level to every entry
    - Adds timestamp to every entry
    - Renders output as JSON
    """
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    # Set standard library logging level
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a named structlog logger.
    
    Args:
        name: the logger name, typically __name__
        
    Returns:
        BoundLogger: a configured structlog logger
    """
    return structlog.get_logger(name)
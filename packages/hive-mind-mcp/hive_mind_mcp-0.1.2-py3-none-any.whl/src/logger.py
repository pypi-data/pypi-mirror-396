import sys
import os
import logging
import structlog

def configure_logger():
    """
    Configures structlog for structured JSON logging.
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Decide renderer based on environment (pretty for local dev, JSON for prod/CI)
    # Using simple heuristic: if NO_PRETTY_LOGS env var is set, use JSON.
    if os.getenv("NO_PRETTY_LOGS"):
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=shared_processors + [renderer],
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = None):
    return structlog.get_logger(name)

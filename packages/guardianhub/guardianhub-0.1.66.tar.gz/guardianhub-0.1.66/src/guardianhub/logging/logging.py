import logging
import sys

# We don't need 'json' since we're not using JsonFormatter anymore
# from .logging_filters import HealthCheckFilter # Assuming this import is correct relative to the file location

def get_logger(name: str) -> logging.Logger:
    """Returns a logger instance for a given name."""
    return logging.getLogger(name)


def setup_logging(service_name: str, level: str | int = logging.INFO):
    """
    Configures the root logger and the uvicorn.access logger using a standard format.
    """
    numeric_level = logging.getLevelName(level.upper()) if isinstance(level, str) else level

    # 1. Define a standard Python Formatter
    standard_formatter = logging.Formatter(
        # Example format: [2025-10-12 00:50:20] INFO: sutram-ai-host.main - message
        fmt=f"[%(asctime)s] %(levelname)s: {service_name}.%(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 2. Setup the Root Logger (for ALL application logs, including lifespan)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers (critical for clean reconfiguration)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add the main application handler
    app_handler = logging.StreamHandler(sys.stdout)
    app_handler.setFormatter(standard_formatter)
    app_handler.setLevel(numeric_level)
    root_logger.addHandler(app_handler)

    # 3. Setup the Uvicorn Access Logger (for HTTP request logs)
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(numeric_level)
    # This prevents uvicorn logs from being duplicated by propagating to the root_logger
    uvicorn_access_logger.propagate = False

    # Clear existing uvicorn handlers
    for handler in uvicorn_access_logger.handlers[:]:
        uvicorn_access_logger.removeHandler(handler)

    # Add the dedicated uvicorn handler
    uvicorn_handler = logging.StreamHandler(sys.stdout)
    uvicorn_handler.setFormatter(standard_formatter)

    # Assuming HealthCheckFilter is defined and available
    try:
        from .logging_filters import HealthCheckFilter
        uvicorn_handler.addFilter(HealthCheckFilter(path="/health"))
    except ImportError:
        # Fallback if the filter cannot be imported
        pass

    uvicorn_handler.setLevel(numeric_level)
    uvicorn_access_logger.addHandler(uvicorn_handler)

    # This final log should now appear correctly
    root_logger.info(
        f"Logging for '{service_name}' configured at level {logging.getLevelName(numeric_level)} with standard format."
    )
# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import atexit
import logging
import re
import sys
from pathlib import Path
from typing import Optional, Union
from dataclasses import dataclass, field

from loguru import logger


class InterceptHandler(logging.Handler):
    """Handler that intercepts standard logging calls and routes them to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record by routing it to loguru."""
        # Get corresponding Loguru level if it exists
        try:
            level: Union[str, int] = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logging call originated
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


@dataclass
class LogConfig:
    """Logging configuration"""

    file: Optional[str] = None
    stdout: bool = True
    level: str = "INFO"
    loggers: dict = field(default_factory=dict)


# Hardcoded rotation settings
MAX_SIZE = "10 MB"  # Rotate at 10 MB
RETENTION = 5  # Keep 5 backup files


def _format_with_conditional_level_color(record) -> str:
    """Format log record with conditional level coloring on the message.

    If the message contains custom color tags, they are preserved.
    Otherwise, the message is wrapped with <level> tags for automatic level coloring.
    """
    message = record["message"]

    # Check if message contains color tags (e.g., <cyan>, <bright_blue>, etc.)
    has_color_tags = re.search(r"<[a-z_]+>", message) is not None

    # Format the message part with or without level coloring
    if has_color_tags:
        formatted_message = message
    else:
        formatted_message = f"<level>{message}</level>"

    # Use shorter names for better alignment (4 chars)
    level_name = record["level"].name
    if level_name == "WARNING":
        level_name = "W"
    elif level_name == "ERROR":
        level_name = "E"
    elif level_name == "INFO":
        level_name = "I"
    elif level_name == "DEBUG":
        level_name = "D"
    elif level_name == "CRITICAL":
        level_name = "C"

    module_name_width = 25
    record_name = _format_with_width(record["name"], module_name_width)
    thread_name_width = 15
    thread_name = _format_with_width(record["thread"].name, thread_name_width)

    return (
        f"<green>{record['time']:YYYY-MM-DDTHH:mm:ss}</green> "
        f"<level>{level_name: <1}</level> "
        f"<cyan>{record_name: <{module_name_width}}</cyan> "
        f"[{thread_name: <{thread_name_width}}] "
        f"{formatted_message}\n"
    )


def _format_with_width(name: str, max_length: int) -> str:
    """Format the logger name to fit within max_length by truncating from the start if necessary."""
    if len(name) <= max_length:
        return name

    parts = name.split(".")
    if len(parts) == 1:
        # No dots, just truncate from the start
        return name[0] + "..." + name[-(max_length - 4) :]

    # Keep first character of each part except the last
    shortened_parts = [part[0] for part in parts[:-1]]
    shortened_parts.append(parts[-1])
    result = ".".join(shortened_parts)

    # If still too long, truncate the last part, by keeping the first character, followed by ..., then the end
    if len(result) > max_length:
        prefix = ".".join(shortened_parts[:-1]) + "." if shortened_parts[:-1] else ""
        last_part = shortened_parts[-1]
        available = max_length - len(prefix) - 3  # 3 for "..."
        if available > 1:
            result = prefix + last_part[0] + "..." + last_part[-(available - 1) :]
        else:
            result = result[:max_length]

    return result


def setup_logging(config: Optional[LogConfig] = None):
    """Setup logging configuration with optional file output and per-logger level overrides

    This function configures loguru to intercept all standard library logging calls.
    Other modules can use standard logging (logging.getLogger(__name__)) and their
    logs will be automatically routed through loguru with all its benefits.

    Log files are automatically rotated when they reach 10MB, keeping 5 backup files.

    Args:
        config: LoggingConfig instance with file, stdout, level, and loggers settings
    """
    # Remove all existing handlers to avoid duplicates when called multiple times
    logger.remove()

    # Register cleanup to properly stop logger on exit
    atexit.register(logger.complete)

    # Configure custom colors for log levels
    logger.level("DEBUG", color="<white><dim>")

    if config is None:
        config = LogConfig()

    # Convert level strings to numeric values for comparison
    level_map = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    default_level_num = level_map.get(config.level.upper(), 20)

    # Build per-logger level map
    logger_levels = {}
    if config.loggers:
        for logger_name, logger_level in config.loggers.items():
            logger_levels[logger_name] = level_map.get(logger_level.upper(), default_level_num)

    # Intercept standard library logging and route to loguru
    # Set root logger to lowest configured level (or DEBUG if any logger uses DEBUG)
    # This ensures messages aren't filtered before reaching our level_filter
    min_configured_level = min(logger_levels.values()) if logger_levels else default_level_num
    min_level = min(min_configured_level, default_level_num)
    logging.basicConfig(handlers=[InterceptHandler()], level=min_level, force=True)

    # Also intercept any existing loggers that might have been created
    # Set them to propagate messages to the root logger without individual filtering
    # The level_filter will handle per-logger filtering in loguru
    # pylint: disable=no-member
    for name in logging.root.manager.loggerDict.keys():  # type: ignore[attr-defined]
        log = logging.getLogger(name)
        log.handlers = []
        log.propagate = True
        # Set logger level to minimum to allow level_filter to handle filtering
        log.setLevel(min_level)

    # Custom filter function for per-logger level control
    def level_filter(record):
        """Filter log records based on per-logger level configuration"""
        record_level = record["level"].no

        # Check if any logger-specific level applies
        for logger_name, min_level in logger_levels.items():
            if record["name"].startswith(logger_name):
                return record_level >= min_level

        # Use default level
        return record_level >= default_level_num

    # Patcher to escape braces in log messages to prevent format string errors
    def escape_braces(record):
        """Escape curly braces in log messages to treat them as literals"""
        record["message"] = record["message"].replace("{", "{{").replace("}", "}}")
        return record

    # Add file handler if log_file is specified
    if config.file:
        # Create log directory if it doesn't exist
        log_path = Path(config.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Add single rotating file handler with custom filter
        logger.add(
            config.file,
            format=_format_with_conditional_level_color,
            level=0,  # Accept all levels, filter will handle it
            rotation=MAX_SIZE,
            retention=RETENTION,
            enqueue=True,  # Thread-safe
            backtrace=True,  # Enable full backtrace on exceptions
            diagnose=True,  # Enable detailed exception diagnostics
            filter=level_filter if config.loggers else None,
        )

    # Add stdout handler if requested
    if config.stdout:
        logger.add(
            sys.stdout,
            format=_format_with_conditional_level_color,
            level=0,  # Accept all levels, filter will handle it
            colorize=True,
            backtrace=True,  # Enable full backtrace on exceptions
            diagnose=True,  # Enable detailed exception diagnostics
            filter=level_filter if config.loggers else None,
        )

    # If neither file nor stdout is configured, default to stdout
    if not config.file and not config.stdout:
        logger.add(
            sys.stdout,
            format=_format_with_conditional_level_color,
            level=0,  # Accept all levels, filter will handle it
            colorize=True,
            backtrace=True,  # Enable full backtrace on exceptions
            diagnose=True,  # Enable detailed exception diagnostics
            filter=level_filter if config.loggers else None,
        )

    # Configure logger to escape braces in all messages
    logger.configure(patcher=escape_braces)

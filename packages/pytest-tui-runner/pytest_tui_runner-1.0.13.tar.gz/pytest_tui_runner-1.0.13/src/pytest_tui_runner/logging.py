import sys
from pathlib import Path

import yaml
from loguru import logger

from pytest_tui_runner.paths import Paths

__all__ = ["logger", "setup_logger"]


def setup_logger(clear_log_file: bool = False) -> None:
    """Configure the loguru logger with file and terminal handlers."""
    Paths.log_dir().mkdir(parents=True, exist_ok=True)

    config = get_logger_config()

    # CONFIGURATION
    # ---------------------------------
    # file log format
    log_format = config.get(
        "format",
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "Line{line: >4} ({file}): <b>{message}</b>",
    )
    level = config.get("level", "INFO")
    rotation = config.get("rotation", "00:00")
    retention = config.get("retention", 7)
    # ---------------------------------

    # terminal log format
    stdout_format = "    <green>{time:HH:mm:ss}</green> | <b>{message}</b>"

    # Remove default logger
    logger.remove()

    # Add new logger with new log format
    logger.add(
        Paths.log_file(),
        level=level,
        format=log_format,
        colorize=False,
        backtrace=True,
        diagnose=True,
        enqueue=True,
        filter=lambda record: record["level"].name != "TERMINAL",
        rotation=rotation,
        retention=retention,
    )

    # Register a custom log level for terminal output
    #
    # This defines a **custom log level** named "TERMINAL".
    # - `no=25`: The numeric value of this level, which determines its severity.
    #   Lower values mean less severe (more verbose), higher mean more critical.
    #   - e.g., DEBUG = 10, INFO = 20, WARNING = 30.
    #   - 25 is between INFO (20) and WARNING (30), so "TERMINAL" will show messages
    #     that are more important than INFO, but less than WARNING.
    # - `color="<blue>"`: This defines the color used in terminal output for messages of this level.
    #   You can use any color supported by loguru, e.g., <cyan>, <yellow>, <red>, etc.
    #
    # To log a message at this custom level, use:
    #     logger.log("TERMINAL", "This message is for the terminal only.")
    try:
        logger.level("TERMINAL", no=25, color="<blue>")

        # Add special logger for terminal
        logger.add(
            sys.stdout,
            level="TERMINAL",
            format=stdout_format,
            colorize=False,
            backtrace=True,
            diagnose=True,
            filter=lambda record: record["level"].name == "TERMINAL",
        )
    except ValueError as e:
        logger.warning(f"Failed to set up terminal logger: {e}")

    if clear_log_file:
        Path.open(Paths.log_file(), "w").close()


def get_logger_config() -> dict:
    """Get the content of the log configuration file if it exists."""
    config_file = Paths.log_config_file()
    if config_file.is_file():
        try:
            with config_file.open("r") as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError) as e:
            logger.error(
                f"Failed to read log configuration file: {e}. Using default configuration.",
            )
    return {}

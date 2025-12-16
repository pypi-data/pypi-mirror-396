import json
from functools import lru_cache
from pathlib import Path

import yaml

from pytest_tui_runner.logging import logger
from pytest_tui_runner.utils.types.config import TestConfig
from pytest_tui_runner.utils.types.config_validator import Config


@lru_cache(maxsize=1)
def load_config(file_path: str) -> TestConfig:
    """Load and parse a configuration file.

    The result is cached, so repeated calls with the same file_path return the same object
    without re-reading the file.
    """
    path = Path(file_path)

    if not path.exists():
        logger.error(f"Config file path does not exists: {file_path}")
        raise FileNotFoundError(
            f"Configuration file '{file_path}' does not exist. "
            "Use the command 'pytest-tui init' to create a default configuration.",
        )

    logger.debug(f"Config file path set to: '{file_path}'")

    if path.suffix in {".yaml", ".yml"}:
        logger.debug("Parsing as YAML")
        with Path.open(path, encoding="utf-8") as file:
            raw = yaml.safe_load(file)
    elif path.suffix == ".json":
        logger.debug("Parsing as JSON")
        with Path.open(path, encoding="utf-8") as file:
            raw = json.load(file)
    else:
        logger.error(f"Invalid config file format: '{path.suffix}'")
        raise ValueError("Only YAML and JSON files are supported.")

    Config.model_validate(raw)
    return raw

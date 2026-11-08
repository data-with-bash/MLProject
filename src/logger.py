"""Application logger configuration."""

import logging
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = f"{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
LOG_FILE_PATH = LOG_DIR / LOG_FILE

logger = logging.getLogger("ml_project")
logger.setLevel(logging.INFO)
logger.propagate = False

# Avoid adding another file handler if this module is reloaded.
if not any(
    isinstance(handler, logging.FileHandler)
    and Path(handler.baseFilename) == LOG_FILE_PATH.resolve()
    for handler in logger.handlers
):
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(filename)s:%(lineno)d "
            "%(name)s %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(file_handler)


__all__ = ["LOG_DIR", "LOG_FILE", "LOG_FILE_PATH", "logger"]

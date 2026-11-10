"""Application logger configuration."""

import logging
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = f"{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
LOG_FILE_PATH = LOG_DIR / LOG_FILE
LOG_FORMAT = (
    "[%(asctime)s] %(filename)s:%(lineno)d "
    "%(name)s %(levelname)s - %(message)s"
)

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
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

# The project logger does not propagate to the root logger, so add a console
# handler explicitly to make progress visible when the pipeline is run.
if not any(type(handler) is logging.StreamHandler for handler in logger.handlers):
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)


__all__ = ["LOG_DIR", "LOG_FILE", "LOG_FILE_PATH", "logger"]

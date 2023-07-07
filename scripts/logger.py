from ._logger import setup_logger, logger
from .config import CONFIG
from .paths import LOG_DIR

setup_logger(LOG_DIR, CONFIG.LOGGING_LEVEL)

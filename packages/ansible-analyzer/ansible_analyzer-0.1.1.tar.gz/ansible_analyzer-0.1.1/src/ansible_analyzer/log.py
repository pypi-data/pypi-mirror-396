import logging
import os

LOG_LEVEL_ENV_VAR = "ANSIBLE_ANALYZER_LOG_LEVEL"
DEFAULT_LOG_LEVEL = "INFO"


def init_logger() -> logging.Logger:
    log_level = os.environ.get(LOG_LEVEL_ENV_VAR, DEFAULT_LOG_LEVEL).upper()
    logging.basicConfig(level=log_level)
    logger = logging.getLogger("ansible-analyzer")

    return logger

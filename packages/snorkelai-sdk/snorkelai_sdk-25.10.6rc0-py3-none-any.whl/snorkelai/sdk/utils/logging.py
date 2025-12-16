import logging
import warnings
from typing import Optional

warnings.filterwarnings(action="ignore", category=SyntaxWarning)

warnings.filterwarnings(action="ignore", category=FutureWarning)

MAX_SINGLE_LINE_LENGTH = 1024 * 200  # 200KB
DEFAULT_SERVER_ERROR_MESSAGE = "A server error occurred while handling the request"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    # Remove log handlers and propagate to root logger.
    logger.handlers = []
    logger.propagate = True
    return logger

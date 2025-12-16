import os
import sys
from loguru import logger

log_level = os.getenv("AOCP_LOG_LEVEL", "INFO").upper()
log_level = "DEBUG"
logger.remove()
logger.add(sys.stderr, level=log_level)

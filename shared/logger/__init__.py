import sys

from loguru import logger

FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "{name}:{function}:{line} | "
    "{message} | extra={extra}"
)
logger.remove()
logger.add(sys.stdout, format=FORMAT)
logger.level("INFO")

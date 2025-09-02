import sys

from loguru import logger

FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.remove()
logger.add(sys.stdout, format=FORMAT)
logger.level("INFO")

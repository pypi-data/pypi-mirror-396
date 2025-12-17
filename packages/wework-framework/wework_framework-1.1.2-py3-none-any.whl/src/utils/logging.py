import logging
from src.config.settings import settings


def get_logger(name: str):
    logging.basicConfig(level=settings.log_level, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    return logging.getLogger(name)

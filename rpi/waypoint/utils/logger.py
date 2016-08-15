import logging
from waypoint.settings import LOG_LEVEL


def get_logger(name, level=LOG_LEVEL):
    logging.basicConfig(level=level)
    logger = logging.getLogger(name)
    return logger

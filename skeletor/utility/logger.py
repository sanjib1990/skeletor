import logging
import sys
from logging import Logger

from skeletor.config import LOG_LEVEL
from skeletor.utility.decorators import singleton


@singleton
class Logger(object):
    def __init__(self):
        root = logging.getLogger()
        root.setLevel(LOG_LEVEL)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(LOG_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)

    def get(self, name) -> Logger:
        return logging.getLogger(name)

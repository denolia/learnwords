import logging
import sys

from colorlog import ColoredFormatter

logging.getLogger("urllib3").setLevel(logging.WARNING)

LOG_LEVEL = logging.DEBUG
LOGFORMAT = " %(log_color)s%(asctime)-6s:%(levelname)-6s%(reset)s | %(log_color)s%(name)s : %(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler(stream=sys.stdout)
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)


def get_logger(name: str):
    return logging.getLogger(name)

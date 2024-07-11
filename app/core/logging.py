
import uvicorn
import uvicorn.logging
import logging
import sys
import os
import logging.config

FORMAT: str = "%(levelprefix)s [%(asctime)s] [%(process)s] \
- %(name)s:%(lineno)d: %(message)s"

DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


ROOT_LEVEL = os.environ.get('PROD', "DEBUG")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": FORMAT},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "level": ROOT_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "DEBUG",
            "handlers": ["default"],
        },
        "uvicorn.access": {
            "level": "DEBUG",
            "handlers": ["default"],
        },
    },
}

# logging.config.dictConfig(LOGGING_CONFIG)


# create logger
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = uvicorn.logging.ColourizedFormatter(FORMAT, datefmt=DATE_FORMAT)
# logger.handlers[0].setFormatter(uvicorn.logging.ColourizedFormatter(FORMAT, datefmt=DATE_FORMAT))

ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
logger.propagate = False

# End

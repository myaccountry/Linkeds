import logging
from CONFIG.logs_config import *


class CustomFormatter(logging.Formatter):

    grey = GREY
    blue = BLUE
    yellow = YELLOW
    red = RED
    bold_red = BOLD_RED
    reset = RESET
    format = LOGGER_FORMAT

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def init_logger(name):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    format_handler = logging.StreamHandler()
    format_handler.setLevel(logging.DEBUG)
    format_handler.setFormatter(CustomFormatter())

    file_handler = logging.FileHandler(f"{LOGS_PATH}/{name}_logs.log")
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] -> %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(format_handler)
    return "-init Logger custom format-"


if __name__ == '__main__':
    print('OK')

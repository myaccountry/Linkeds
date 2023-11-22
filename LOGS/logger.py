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


if __name__ == '__main__':
    print('OK')


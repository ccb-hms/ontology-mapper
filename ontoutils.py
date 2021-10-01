import logging
import sys

STOP_WORDS = {'in', 'the', 'any', 'all', 'for', 'and', 'or', 'dx', 'on', 'fh', 'tx', 'only', 'qnorm', 'w', 'iqb',
              'ds', 'rd', 'rdgwas'}


def get_logger(name, level):
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def parse_list_file(file_path):
    file = open(file_path)
    lines = file.read().splitlines()
    return lines

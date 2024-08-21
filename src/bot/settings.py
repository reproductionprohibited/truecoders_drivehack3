import logging
from typing import Dict

from dotenv import dotenv_values


def setup_logger(name: str, log_filename: str, level: int = logging.INFO):
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s')

    handler = logging.FileHandler(filename=log_filename)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_config(filepath: str = '.env') -> Dict[str, str]:
    config = dotenv_values(dotenv_path=filepath)
    return config

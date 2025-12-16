import logging
import pathlib
import sys
from logging.handlers import RotatingFileHandler

# TODO: make these settings configurable
BACKUP_COUNT = 2
LOG_FILE_SIZE = 1024**2  # 1MB

logger: logging.Logger = logging.Logger("pygame_default", level=logging.INFO)


def setup_game_logger(log_file: pathlib.PurePath, name: str, level: int = logging.INFO):
    logger.name = f"pygame_{name}"
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)-22s | %(levelname)-8s | %(funcName)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file, backupCount=BACKUP_COUNT, maxBytes=LOG_FILE_SIZE
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.WARNING)
    logger.addHandler(stderr_handler)

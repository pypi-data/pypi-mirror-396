import logging
from chain_nhem_nhem.config import settings


def get_logger(name: str = "chain_nhem_nhem") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = getattr(logging, settings.LOGGER_LEVEL, logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "[%(levelname)s] [%(name)s] %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = False

    return logger

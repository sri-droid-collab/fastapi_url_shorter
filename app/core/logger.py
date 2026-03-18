import logging
import sys


def setup_logging() -> logging.Logger:
    """Configure the application-wide logger and return it."""
    logger = logging.getLogger("url_shortener")
    logger.setLevel(logging.INFO)

    # Console handler — writes to stdout so Docker / cloud log collectors pick it up
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Guard against duplicate handlers when the module is reloaded (e.g. --reload)
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# Module-level logger instance — import this instead of calling getLogger everywhere
logger = logging.getLogger("url_shortener")

import logging
import sys

def setup_logging():
    # Setup standard logging configuration
    logger = logging.getLogger("url_shortener")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    
    # Add handler to logger (ensure we don't duplicate handlers)
    if not logger.handlers:
        logger.addHandler(ch)
        
    return logger

# Create a module-level logger instance
logger = logging.getLogger("url_shortener")

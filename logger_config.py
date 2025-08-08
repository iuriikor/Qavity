"""
Logging configuration for Qavity application
"""
import logging
import sys
from datetime import datetime

def setup_logging(level=logging.WARNING, log_to_file=False):
    """
    Set up logging configuration for the Qavity application.
    
    Args:
        level: Logging level (default: INFO)
        log_to_file: Whether to log to file (default: True)
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        try:
            log_filename = f"qavity_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_filename)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
    
    # Set logging levels for noisy libraries
    logging.getLogger('dash').setLevel(logging.ERROR)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('cherrypy').setLevel(logging.ERROR)
    logging.getLogger('hypercorn').setLevel(logging.ERROR)
    logging.getLogger('quart').setLevel(logging.ERROR)
    
    return root_logger

def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Usually __name__ from the calling module
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)

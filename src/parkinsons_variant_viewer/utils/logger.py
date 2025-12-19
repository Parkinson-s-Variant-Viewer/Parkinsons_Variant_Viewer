# logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Create a logger instance
def create_logger(level=logging.INFO):
    """
    Create and configure a rotating file logger for the
    Parkinsons Variant Viewer project.

    Parameters
    ----------
    level : int, optional
        The logging level (e.g., logging.DEBUG, logging.INFO).
        Defaults to logging.INFO.

    Returns
    -------
    logger : logging.Logger
        A configured logger instance.
    """

    # Use absolute path for logs directory (works in Docker and development)
    # Try /app/src/logs first (Docker), fall back to local src/logs
    import os
    if os.path.exists('/app/src/logs'):
        log_dir = Path('/app/src/logs')
    else:
        # Development mode: calculate relative path
        current_directory = str(Path(__file__).resolve().parent)
        parent_directory = Path(current_directory).parent.parent
        log_dir = parent_directory / "logs"
    
    # Ensure the logs directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create or retrieve a named logger 
    logger = logging.getLogger('parkinsons_variant_viewer_logger')
    logger.setLevel(level)  # Level set to INFO by default 

    # Prevent adding duplicate handlers if logger already exists
    if logger.hasHandlers():
        return logger

    # Stream handler (console output) 
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    stream_handler.setFormatter(stream_formatter)

    # File handler with detailed format including module, function, and line number
    file_handler = RotatingFileHandler(str(log_dir / 'parkinsons_variant_viewer.log'),
                                       maxBytes=500000,  # 500 KB
                                       backupCount=2)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


# Instantiate the logger
logger = create_logger()

"""Tests for logger.py module."""
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path

from parkinsons_variant_viewer.utils.logger import create_logger

LOGGER_NAME = "parkinsons_variant_viewer_logger"


def clear_logger_handlers():
    """Ensure logger is in a clean state before each test."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()
    logger.propagate = False


# ----------------------
# Test handler creation path
# ----------------------
def test_create_logger_adds_handlers():
    clear_logger_handlers()

    with patch("parkinsons_variant_viewer.utils.logger.Path.mkdir") as mock_mkdir, \
         patch("parkinsons_variant_viewer.utils.logger.logging.StreamHandler") as mock_stream_cls, \
         patch("parkinsons_variant_viewer.utils.logger.RotatingFileHandler") as mock_file_cls:

        # Mock handler instances
        mock_stream_handler = MagicMock()
        mock_file_handler = MagicMock()

        mock_stream_cls.return_value = mock_stream_handler
        mock_file_cls.return_value = mock_file_handler

        logger = create_logger(logging.DEBUG)

        # Directory creation
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Stream handler configuration
        mock_stream_handler.setLevel.assert_called_once_with(logging.DEBUG)
        mock_stream_handler.setFormatter.assert_called_once()

        # File handler configuration
        mock_file_handler.setLevel.assert_called_once_with(logging.DEBUG)
        mock_file_handler.setFormatter.assert_called_once()

        # Logger properties
        assert logger.name == LOGGER_NAME
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 2


# ----------------------
# Test early-return path (hasHandlers == True)
# ----------------------
def test_create_logger_returns_existing_logger():
    clear_logger_handlers()

    logger1 = create_logger()
    logger2 = create_logger()

    assert logger1 is logger2
    assert len(logger1.handlers) == 2

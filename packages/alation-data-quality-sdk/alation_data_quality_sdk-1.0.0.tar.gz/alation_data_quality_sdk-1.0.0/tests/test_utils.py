"""Tests for utility modules."""

from unittest.mock import Mock, patch

import pytest

from data_quality_sdk.utils.exceptions import (
    AlationAPIError,
    DataQualitySDKError,
    DatasourceConfigError,
    NetworkError,
    SodaScanError,
    UnsupportedDatasourceError,
)
from data_quality_sdk.utils.logging import get_logger, setup_logging


class TestExceptions:
    """Test custom exception classes."""

    def test_data_quality_sdk_error(self):
        """Test DataQualitySDKError exception."""
        with pytest.raises(DataQualitySDKError) as exc_info:
            raise DataQualitySDKError("Test error message")

        assert str(exc_info.value) == "Test error message"

    def test_alation_api_error(self):
        """Test AlationAPIError exception."""
        with pytest.raises(AlationAPIError) as exc_info:
            raise AlationAPIError("API error message", status_code=404)

        assert str(exc_info.value) == "API error message"

    def test_datasource_config_error(self):
        """Test DatasourceConfigError exception."""
        with pytest.raises(DatasourceConfigError) as exc_info:
            raise DatasourceConfigError("Config error message")

        assert str(exc_info.value) == "Config error message"

    def test_soda_scan_error(self):
        """Test SodaScanError exception."""
        with pytest.raises(SodaScanError) as exc_info:
            raise SodaScanError("Scan error message")

        assert str(exc_info.value) == "Scan error message"

    def test_unsupported_datasource_error(self):
        """Test UnsupportedDatasourceError exception."""
        with pytest.raises(UnsupportedDatasourceError) as exc_info:
            raise UnsupportedDatasourceError("Unsupported datasource")

        assert str(exc_info.value) == "Unsupported datasource type: Unsupported datasource"

    def test_network_error(self):
        """Test NetworkError exception."""
        with pytest.raises(NetworkError) as exc_info:
            raise NetworkError("Network error message")

        assert str(exc_info.value) == "Network error message"


class TestLogging:
    """Test logging utilities."""

    @patch("data_quality_sdk.utils.logging.logging")
    def test_setup_logging_info_level(self, mock_logging):
        """Test setup_logging with INFO level."""
        mock_logger = Mock()
        mock_logger.handlers = []  # No existing handlers
        mock_logging.getLogger.return_value = mock_logger
        mock_logging.INFO = 20

        logger = setup_logging("INFO")

        mock_logging.getLogger.assert_called_with("data_quality_sdk")
        mock_logger.setLevel.assert_called_with(20)
        assert logger == mock_logger

    @patch("data_quality_sdk.utils.logging.logging")
    def test_setup_logging_debug_level(self, mock_logging):
        """Test setup_logging with DEBUG level."""
        mock_logger = Mock()
        mock_logger.handlers = []  # No existing handlers
        mock_logging.getLogger.return_value = mock_logger
        mock_logging.DEBUG = 10

        logger = setup_logging("DEBUG")

        mock_logging.getLogger.assert_called_with("data_quality_sdk")
        mock_logger.setLevel.assert_called_with(10)
        assert logger == mock_logger

    @patch("data_quality_sdk.utils.logging.logging")
    def test_get_logger(self, mock_logging):
        """Test get_logger function."""
        mock_logger = Mock()
        mock_logging.getLogger.return_value = mock_logger

        logger = get_logger("test_module")

        mock_logging.getLogger.assert_called_with("test_module")
        assert logger == mock_logger

    @patch("data_quality_sdk.utils.logging.logging")
    def test_get_logger_no_name(self, mock_logging):
        """Test get_logger function with no name."""
        mock_logger = Mock()
        mock_logging.getLogger.return_value = mock_logger

        logger = get_logger()

        mock_logging.getLogger.assert_called_with("data_quality_sdk")
        assert logger == mock_logger

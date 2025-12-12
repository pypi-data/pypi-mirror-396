"""Custom exceptions for the Data Quality SDK."""


class DataQualitySDKError(Exception):
    """Base exception for all SDK errors."""

    pass


class AlationAPIError(DataQualitySDKError):
    """Raised when Alation API calls fail."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class DatasourceConfigError(DataQualitySDKError):
    """Raised when datasource configuration is invalid or cannot be generated."""

    pass


class SodaScanError(DataQualitySDKError):
    """Raised when Soda scan execution fails."""

    def __init__(self, message: str, scan_logs: list = None):
        super().__init__(message)
        self.scan_logs = scan_logs or []


class ConfigurationError(DataQualitySDKError):
    """Raised when SDK configuration is invalid."""

    pass


class ProtobufConfigError(DatasourceConfigError):
    """Raised when protobuf configuration parsing fails."""

    pass


class UnsupportedDatasourceError(DatasourceConfigError):
    """Raised when datasource type is not supported."""

    def __init__(self, datasource_type: str):
        self.datasource_type = datasource_type
        super().__init__(f"Unsupported datasource type: {datasource_type}")


class NetworkError(DataQualitySDKError):
    """Raised when network operations fail."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error

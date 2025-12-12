"""Query client wrapper for handling datasource connections."""

import base64
from typing import Any, Dict, Optional

from ..utils.exceptions import ProtobufConfigError
from ..utils.logging import get_logger


class QueryClientWrapper:
    """Wrapper for QueryClient to handle protobuf configuration parsing."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def parse_protobuf_config(self, protobuf_config_b64: str) -> Dict[str, Any]:
        """Parse base64-encoded protobuf configuration.

        Args:
            protobuf_config_b64: Base64-encoded protobuf configuration

        Returns:
            Dictionary containing parsed configuration

        Raises:
            ProtobufConfigError: If parsing fails
        """
        try:
            # Import the QueryClient here to handle optional dependency
            from queryservice_client.queryclient import QueryClient

            config = QueryClient.configuration_from_b64_string(protobuf_config_b64)

            # Convert protobuf object to dictionary for easier handling
            config_dict = self._protobuf_to_dict(config)

            self.logger.debug("Successfully parsed protobuf configuration")
            return config_dict

        except ImportError as e:
            raise ProtobufConfigError(
                "QueryService client not available. Make sure queryservice_client is installed."
            ) from e
        except Exception as e:
            raise ProtobufConfigError(f"Failed to parse protobuf configuration: {str(e)}") from e

    def _protobuf_to_dict(self, protobuf_obj) -> Dict[str, Any]:
        """Convert protobuf object to dictionary.

        Args:
            protobuf_obj: Protobuf object to convert

        Returns:
            Dictionary representation of the protobuf object
        """
        try:
            # Try to use MessageToDict if available (Google protobuf)
            from google.protobuf.json_format import MessageToDict

            return MessageToDict(protobuf_obj)
        except ImportError:
            # Fallback to manual extraction for common fields
            return self._extract_common_config_fields(protobuf_obj)

    def _extract_common_config_fields(self, config) -> Dict[str, Any]:
        """Extract common configuration fields from protobuf object.

        Args:
            config: Protobuf configuration object

        Returns:
            Dictionary with extracted fields
        """
        result = {}

        # Common field mappings for different datasource types
        field_mappings = [
            # Database connection fields
            ("host", ["host", "hostname", "server"]),
            ("port", ["port"]),
            ("database", ["database", "db", "dbname"]),
            ("schema", ["schema", "default_schema"]),
            ("username", ["username", "user"]),
            ("password", ["password", "pwd"]),
            # Connection type and driver
            ("type", ["type", "driver", "connector_type"]),
            ("driver", ["driver", "jdbc_driver"]),
            # SSL and security
            ("ssl", ["ssl", "use_ssl", "ssl_mode"]),
            ("ssl_cert", ["ssl_cert", "ssl_certificate"]),
            # Additional parameters
            ("extra_params", ["extra_params", "additional_params", "connection_params"]),
        ]

        for result_key, possible_attrs in field_mappings:
            for attr in possible_attrs:
                if hasattr(config, attr):
                    value = getattr(config, attr)
                    if value:  # Only include non-empty values
                        result[result_key] = value
                        break

        # Special handling for nested objects if they exist
        if hasattr(config, "connection"):
            connection_obj = getattr(config, "connection")
            for result_key, possible_attrs in field_mappings:
                for attr in possible_attrs:
                    if hasattr(connection_obj, attr):
                        value = getattr(connection_obj, attr)
                        if value and result_key not in result:
                            result[result_key] = value
                            break

        self.logger.debug(f"Extracted configuration fields: {list(result.keys())}")
        return result

    def get_connection_info(self, protobuf_config_b64: str) -> Dict[str, Any]:
        """Get connection information from protobuf config.

        Args:
            protobuf_config_b64: Base64-encoded protobuf configuration

        Returns:
            Dictionary with connection information suitable for Soda

        Raises:
            ProtobufConfigError: If parsing fails
        """
        config_dict = self.parse_protobuf_config(protobuf_config_b64)

        # Extract parameters from the nested structure
        parameters = config_dict.get("parameters", {})

        # Helper function to extract value from nested parameter structure
        def extract_param_value(param_name: str, default=None):
            """Extract value from nested parameter structure."""
            param_data = parameters.get(param_name, {})

            # Check different type wrappers: text, encryptedText, boolean, integer, select, etc.
            for type_wrapper in [
                "text",
                "encryptedText",
                "boolean",
                "integer",
                "select",
                "textArea",
            ]:
                if type_wrapper in param_data:
                    return param_data[type_wrapper].get("value", default)

            return default

        # Extract essential connection information using the helper function
        connection_info = {}

        # Extract JDBC URI and parse it if available
        jdbc_uri = extract_param_value("jdbc_uri")
        if jdbc_uri:
            connection_info.update(self._parse_jdbc_uri(jdbc_uri))

        # Extract individual parameters (only if not already set by JDBC URI parsing)
        individual_params = {
            "host": extract_param_value("host")
            or extract_param_value("hostname")
            or extract_param_value("server"),
            "port": extract_param_value("port"),
            "database": extract_param_value("database")
            or extract_param_value("db")
            or extract_param_value("dbname"),
            "schema": extract_param_value("schema") or extract_param_value("default_schema"),
            "username": extract_param_value("username") or extract_param_value("user"),
            "password": extract_param_value("password") or extract_param_value("pwd"),
            "type": extract_param_value("type") or extract_param_value("connector_type"),
        }

        # Only update connection_info with individual params if they're not already set and not None
        for key, value in individual_params.items():
            if value is not None and key not in connection_info:
                connection_info[key] = value

        # Remove None values
        connection_info = {k: v for k, v in connection_info.items() if v is not None}

        # If no host found, try to extract from JDBC URI
        if not connection_info.get("host") and not jdbc_uri:
            raise ProtobufConfigError("No host or JDBC URI found in datasource configuration")

        # Try to infer type from JDBC URI or other information if not explicitly set
        if not connection_info.get("type"):
            if jdbc_uri:
                if "snowflake://" in jdbc_uri.lower():
                    connection_info["type"] = "snowflake"
                elif "postgresql://" in jdbc_uri.lower():
                    connection_info["type"] = "postgresql"
                elif "mysql://" in jdbc_uri.lower():
                    connection_info["type"] = "mysql"
            elif connection_info.get("port") == 5432:
                connection_info["type"] = "postgresql"
            elif connection_info.get("port") == 3306:
                connection_info["type"] = "mysql"

        self.logger.info(
            f"Extracted connection info for {connection_info.get('type', 'unknown')} datasource: "
            f"host={connection_info.get('host', 'N/A')}, "
            f"database={connection_info.get('database', 'N/A')}"
        )
        return connection_info

    def _parse_jdbc_uri(self, jdbc_uri: str) -> Dict[str, Any]:
        """Parse JDBC URI to extract connection details.

        Args:
            jdbc_uri: JDBC connection URI

        Returns:
            Dictionary with parsed connection details
        """
        connection_details = {}

        try:
            from urllib.parse import parse_qs, urlparse

            # Handle different JDBC URI formats
            if jdbc_uri.startswith("snowflake://"):
                # Snowflake format: snowflake://account.region.provider.com:port/?warehouse=...&db=...
                parsed = urlparse(jdbc_uri)
                connection_details.update(
                    {"host": parsed.hostname, "port": parsed.port or 443, "type": "snowflake"}
                )

                # Parse query parameters
                if parsed.query:
                    params = parse_qs(parsed.query)
                    if "db" in params:
                        connection_details["database"] = params["db"][0]
                    if "warehouse" in params:
                        connection_details["warehouse"] = params["warehouse"][0]

            elif jdbc_uri.startswith("postgresql://") or jdbc_uri.startswith("postgres://"):
                parsed = urlparse(jdbc_uri)
                connection_details.update(
                    {
                        "host": parsed.hostname,
                        "port": parsed.port or 5432,
                        "database": parsed.path.lstrip("/") if parsed.path else None,
                        "type": "postgresql",
                    }
                )

            elif jdbc_uri.startswith("mysql://"):
                parsed = urlparse(jdbc_uri)
                connection_details.update(
                    {
                        "host": parsed.hostname,
                        "port": parsed.port or 3306,
                        "database": parsed.path.lstrip("/") if parsed.path else None,
                        "type": "mysql",
                    }
                )

        except Exception as e:
            self.logger.warning(f"Failed to parse JDBC URI '{jdbc_uri}': {e}")

        return connection_details

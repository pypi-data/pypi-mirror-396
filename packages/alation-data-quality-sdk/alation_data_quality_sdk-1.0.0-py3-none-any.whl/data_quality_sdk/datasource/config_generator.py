"""Datasource configuration generator for Soda Core."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ..client.query_client import QueryClientWrapper
from ..utils.exceptions import DatasourceConfigError, UnsupportedDatasourceError
from ..utils.logging import get_logger


class DatasourceConfigGenerator:
    """Generates Soda Core datasource configuration from Alation metadata."""

    # Supported datasource types and their Soda equivalents
    DATASOURCE_TYPE_MAPPING = {
        "postgresql": "postgres",
        "postgres": "postgres",
        "mysql": "mysql",
        "bigquery": "bigquery",
        "snowflake": "snowflake",
        "redshift": "redshift",
        "oracle": "oracle",
        "sqlserver": "sqlserver",
        "mssql": "sqlserver",
        "databricks": "spark_df",  # Databricks uses Spark
        "spark": "spark_df",
        "athena": "athena",
        "trino": "trino",
        "presto": "presto",
    }

    def __init__(self):
        self.query_client = QueryClientWrapper()
        self.logger = get_logger(__name__)

    def generate_soda_config(
        self,
        datasource_name: str,
        protobuf_config_b64: str,
        db_type: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Generate Soda Core datasource configuration.

        Args:
            datasource_name: Name for the datasource in Soda config
            protobuf_config_b64: Base64-encoded protobuf configuration
            db_type: Database type from Alation
            output_path: Optional path to write the config file

        Returns:
            YAML configuration string

        Raises:
            DatasourceConfigError: If configuration generation fails
            UnsupportedDatasourceError: If datasource type is not supported
        """
        try:
            # Parse the protobuf configuration
            connection_info = self.query_client.get_connection_info(protobuf_config_b64)

            # Determine Soda datasource type
            soda_type = self._get_soda_type(db_type)

            # Generate configuration based on datasource type
            config = self._generate_config_for_type(datasource_name, soda_type, connection_info)

            # Convert to YAML string
            yaml_config = yaml.dump(config, default_flow_style=False, sort_keys=False)

            # Write to file if path provided
            if output_path:
                self._write_config_file(yaml_config, output_path)

            self.logger.info(f"Generated Soda config for {soda_type} datasource: {datasource_name}")
            return yaml_config

        except Exception as e:
            if isinstance(e, (DatasourceConfigError, UnsupportedDatasourceError)):
                raise
            raise DatasourceConfigError(f"Failed to generate Soda configuration: {str(e)}") from e

    def _get_soda_type(self, db_type: str) -> str:
        """Get Soda datasource type from Alation database type.

        Args:
            db_type: Database type from Alation

        Returns:
            Soda datasource type

        Raises:
            UnsupportedDatasourceError: If datasource type is not supported
        """
        normalized_type = db_type.lower().replace("_", "").replace("-", "")

        # Try exact match first
        if normalized_type in self.DATASOURCE_TYPE_MAPPING:
            return self.DATASOURCE_TYPE_MAPPING[normalized_type]

        # Try partial matches
        for alation_type, soda_type in self.DATASOURCE_TYPE_MAPPING.items():
            if alation_type in normalized_type or normalized_type in alation_type:
                return soda_type

        raise UnsupportedDatasourceError(db_type)

    def _generate_config_for_type(
        self, datasource_name: str, soda_type: str, connection_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate configuration for specific datasource type.

        Args:
            datasource_name: Name for the datasource
            soda_type: Soda datasource type
            connection_info: Connection information from protobuf

        Returns:
            Configuration dictionary
        """
        # Base configuration structure
        config = {f"data_source {datasource_name}": {"type": soda_type, "connection": {}}}

        connection = config[f"data_source {datasource_name}"]["connection"]

        # Generate connection config based on datasource type
        if soda_type == "postgres":
            self._configure_postgres(connection, connection_info)
        elif soda_type == "mysql":
            self._configure_mysql(connection, connection_info)
        elif soda_type == "bigquery":
            self._configure_bigquery(connection, connection_info)
        elif soda_type == "snowflake":
            self._configure_snowflake(connection, connection_info)
        elif soda_type == "redshift":
            self._configure_redshift(connection, connection_info)
        elif soda_type == "oracle":
            self._configure_oracle(connection, connection_info)
        elif soda_type == "sqlserver":
            self._configure_sqlserver(connection, connection_info)
        else:
            # Generic configuration for other types
            self._configure_generic(connection, connection_info)

        return config

    def _configure_postgres(self, connection: Dict[str, Any], info: Dict[str, Any]):
        """Configure PostgreSQL connection."""
        connection.update(
            {
                "host": info.get("host"),
                "port": info.get("port", 5432),
                "username": info.get("username"),
                "password": info.get("password"),
                "database": info.get("database"),
            }
        )

        if info.get("schema"):
            connection["schema"] = info["schema"]

    def _configure_mysql(self, connection: Dict[str, Any], info: Dict[str, Any]):
        """Configure MySQL connection."""
        connection.update(
            {
                "host": info.get("host"),
                "port": info.get("port", 3306),
                "username": info.get("username"),
                "password": info.get("password"),
                "database": info.get("database"),
            }
        )

    def _configure_bigquery(self, connection: Dict[str, Any], info: Dict[str, Any]):
        """Configure BigQuery connection."""
        # BigQuery typically uses service account keys or other auth methods
        # This is a basic configuration that might need adjustment
        project_id = info.get("database") or info.get("project_id")
        if project_id:
            connection["account_info_json_path"] = "/path/to/service_account.json"
            connection["auth_scopes"] = ["https://www.googleapis.com/auth/bigquery"]
            # Note: Users will need to provide the actual service account file

    def _configure_snowflake(self, connection: Dict[str, Any], info: Dict[str, Any]):
        """Configure Snowflake connection."""

        # Extract account name from host (remove .snowflakecomputing.com suffix)
        host = info.get("host", "")
        if host.endswith(".snowflakecomputing.com"):
            account = host.replace(".snowflakecomputing.com", "")
        else:
            account = host

        connection.update(
            {
                "user": info.get("username"),
                "password": info.get("password"),
                "account": account,
                "database": info.get("database"),
                "warehouse": info.get("warehouse", "COMPUTE_WH"),
                "role": info.get("role", "PUBLIC"),
                "port": info.get("port", 443),  # Add port parameter for Snowflake
            }
        )

        if info.get("schema"):
            connection["schema"] = info["schema"]

    def _configure_redshift(self, connection: Dict[str, Any], info: Dict[str, Any]):
        """Configure Amazon Redshift connection."""
        connection.update(
            {
                "host": info.get("host"),
                "port": info.get("port", 5439),
                "username": info.get("username"),
                "password": info.get("password"),
                "database": info.get("database"),
            }
        )

        if info.get("schema"):
            connection["schema"] = info["schema"]

    def _configure_oracle(self, connection: Dict[str, Any], info: Dict[str, Any]):
        """Configure Oracle connection."""
        connection.update(
            {
                "host": info.get("host"),
                "port": info.get("port", 1521),
                "username": info.get("username"),
                "password": info.get("password"),
                "database": info.get("database"),  # Oracle service name or SID
            }
        )

    def _configure_sqlserver(self, connection: Dict[str, Any], info: Dict[str, Any]):
        """Configure SQL Server connection."""
        connection.update(
            {
                "host": info.get("host"),
                "port": info.get("port", 1433),
                "username": info.get("username"),
                "password": info.get("password"),
                "database": info.get("database"),
            }
        )

        if info.get("schema"):
            connection["schema"] = info["schema"]

    def _configure_generic(self, connection: Dict[str, Any], info: Dict[str, Any]):
        """Configure generic connection for unsupported but similar types."""
        # Use all available connection info
        for key, value in info.items():
            if value is not None and key != "type":
                connection[key] = value

    def _write_config_file(self, yaml_config: str, output_path: str):
        """Write configuration to file.

        Args:
            yaml_config: YAML configuration string
            output_path: Path to write the file

        Raises:
            DatasourceConfigError: If file writing fails
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(yaml_config)

            self.logger.info(f"Soda configuration written to {output_path}")

        except Exception as e:
            raise DatasourceConfigError(
                f"Failed to write config file to {output_path}: {str(e)}"
            ) from e

    def create_temp_config_file(
        self,
        datasource_name: str,
        protobuf_config_b64: str,
        db_type: str,
        temp_dir: Optional[str] = None,
    ) -> str:
        """Create a temporary configuration file for Soda.

        Args:
            datasource_name: Name for the datasource
            protobuf_config_b64: Base64-encoded protobuf configuration
            db_type: Database type from Alation
            temp_dir: Optional temporary directory (defaults to system temp)

        Returns:
            Path to the temporary configuration file

        Raises:
            DatasourceConfigError: If file creation fails
        """
        import os
        import tempfile

        try:
            # Create temporary file
            temp_dir = temp_dir or tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"soda_config_{datasource_name}.yaml")

            # Generate and write configuration
            yaml_config = self.generate_soda_config(datasource_name, protobuf_config_b64, db_type)

            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(yaml_config)

            self.logger.debug(f"Created temporary Soda config file: {temp_file}")
            return temp_file

        except Exception as e:
            raise DatasourceConfigError(f"Failed to create temporary config file: {str(e)}") from e

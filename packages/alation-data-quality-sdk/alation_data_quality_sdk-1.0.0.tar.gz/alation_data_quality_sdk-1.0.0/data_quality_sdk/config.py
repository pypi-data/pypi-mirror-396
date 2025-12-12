"""Configuration management for the Data Quality SDK."""

import os
from dataclasses import dataclass
from typing import Optional

from .utils.exceptions import DataQualitySDKError


@dataclass
class SDKConfig:
    """Configuration for the Data Quality SDK.

    Required Environment Variables:
        ALATION_HOST: The base URL of the Alation instance (e.g., https://my-alation.company.com)
        MONITOR_ID: The ID of the monitor to execute checks for

    Optional Environment Variables:
        ALATION_API_TOKEN: API token for authentication (if required)
        TENANT_ID: Tenant ID for multi-tenant setups
        JOB_ID: Job identifier (defaults to 'sdk_job')
        REQUEST_ID: Request identifier (defaults to 'sdk_request')
        JOB_TYPE: Job type identifier (defaults to '94')
        ALATION_TIMEOUT: Request timeout in seconds (default: 30)
        LOG_LEVEL: Logging level (default: INFO)
        DRY_RUN: Set to 'true' to skip actual execution (default: false)
    """

    alation_host: str
    monitor_id: str
    api_token: Optional[str] = None
    tenant_id: Optional[str] = None
    job_id: str = "sdk_job"
    request_id: str = "sdk_request"
    job_type: str = "94"
    timeout: int = 30
    log_level: str = "INFO"
    dry_run: bool = False

    @classmethod
    def from_env(cls) -> "SDKConfig":
        """Create configuration from environment variables."""
        # Required variables
        alation_host = os.getenv("ALATION_HOST")
        monitor_id = os.getenv("MONITOR_ID")

        if not alation_host:
            raise DataQualitySDKError(
                "ALATION_HOST environment variable is required. "
                "Set it to your Alation instance URL (e.g., https://my-alation.company.com)"
            )

        if not monitor_id:
            raise DataQualitySDKError(
                "MONITOR_ID environment variable is required. "
                "Set it to the ID of the monitor you want to execute."
            )

        # Optional variables
        api_token = os.getenv("ALATION_API_TOKEN")
        tenant_id = os.getenv("TENANT_ID")
        job_id = os.getenv("JOB_ID", "sdk_job")
        request_id = os.getenv("REQUEST_ID", "sdk_request")
        job_type = os.getenv("JOB_TYPE", "94")
        timeout = int(os.getenv("ALATION_TIMEOUT", "30"))
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

        # Normalize alation_host (ensure no trailing slash)
        alation_host = alation_host.rstrip("/")

        return cls(
            alation_host=alation_host,
            monitor_id=monitor_id,
            api_token=api_token,
            tenant_id=tenant_id,
            job_id=job_id,
            request_id=request_id,
            job_type=job_type,
            timeout=timeout,
            log_level=log_level,
            dry_run=dry_run,
        )

    def get_checks_endpoint(self) -> str:
        """Get the checks endpoint URL."""
        return f"{self.alation_host}/api/checks?monitor_id={self.monitor_id}"

    def get_metadata_endpoint(self) -> str:
        """Get the metadata endpoint URL."""
        return f"{self.alation_host}/api/dq/query_service_metadata"

    def get_results_endpoint(self) -> str:
        """Get the results endpoint URL."""
        return f"{self.alation_host}/api/results/soda"

    def validate(self) -> None:
        """Validate the configuration."""
        if not self.alation_host.startswith(("http://", "https://")):
            raise DataQualitySDKError(
                f"ALATION_HOST must start with http:// or https://, got: {self.alation_host}"
            )

        if not self.monitor_id.isdigit():
            raise DataQualitySDKError(f"MONITOR_ID must be a numeric value, got: {self.monitor_id}")

        if self.timeout <= 0:
            raise DataQualitySDKError(f"ALATION_TIMEOUT must be positive, got: {self.timeout}")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise DataQualitySDKError(
                f"LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL, got: {self.log_level}"
            )

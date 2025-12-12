"""Alation API client for data quality operations."""

import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
import yaml

from ..utils.exceptions import AlationAPIError, NetworkError
from ..utils.logging import get_logger, log_api_request


class MonitorCheckResponse:
    """Data structure for monitor check response."""

    def __init__(self, ds_id: int, dbtype: str, checks: str):
        self.ds_id = ds_id
        self.dbtype = dbtype
        self.checks = checks

    def to_dict(self) -> Dict[str, Any]:
        return {"ds_id": self.ds_id, "dbtype": self.dbtype, "checks": self.checks}


class MetricMetadata:
    """Data structure for metric metadata."""

    def __init__(self, data: Dict[str, Any]):
        self.metric_id = data.get("metric_id")
        self.check_definition = data.get("check_definition")
        self.check_description = data.get("check_description")
        self.ds_id = data.get("ds_id")
        self.dbtype = data.get("dbtype")
        self.schema_id = data.get("schema_id")
        self.schema_name = data.get("schema_name")
        self.table_id = data.get("table_id")
        self.table_name = data.get("table_name")
        self.column_id = data.get("column_id")
        self.column_name = data.get("column_name")
        self.category = data.get("category")
        self.asset_otype = data.get("asset_otype")
        self.asset_id = data.get("asset_id")
        self.sample_failed_query = data.get("sample_failed_query", "")
        self.monitor_id = data.get("monitor_id")
        self.monitor_title = data.get("monitor_title")
        self.is_absolute_value = data.get("is_absolute_value")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "check_definition": self.check_definition,
            "check_description": self.check_description,
            "ds_id": self.ds_id,
            "dbtype": self.dbtype,
            "schema_id": self.schema_id,
            "schema_name": self.schema_name,
            "table_id": self.table_id,
            "table_name": self.table_name,
            "column_id": self.column_id,
            "column_name": self.column_name,
            "category": self.category,
            "asset_otype": self.asset_otype,
            "asset_id": self.asset_id,
            "sample_failed_query": self.sample_failed_query,
            "monitor_id": self.monitor_id,
            "monitor_title": self.monitor_title,
            "is_absolute_value": self.is_absolute_value,
        }


class SampleFailedRowQuery:
    """Data structure for sample failed row query."""

    def __init__(self, metric_unique_identifier: str, ds_id: int, query: str):
        self.metric_unique_identifier = metric_unique_identifier
        self.ds_id = ds_id
        self.query = query

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_unique_identifier": self.metric_unique_identifier,
            "ds_id": self.ds_id,
            "query": self.query,
        }


class AlationClient:
    """Client for interacting with Alation APIs following the soda_check.py pattern."""

    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30,
        tenant_id: Optional[str] = None,
    ):
        """Initialize the Alation client.

        Args:
            base_url: Base URL of the Alation instance (e.g., https://my-alation.company.com)
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
            tenant_id: Optional tenant ID for multi-tenant setups
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self.tenant_id = tenant_id
        self.session = requests.Session()
        self.logger = get_logger(__name__)

        # Set up authentication if token is provided
        if self.api_token:
            self.session.headers.update({"TOKEN": self.api_token})

        # Set tenant ID cookie if provided
        if self.tenant_id:
            self.session.cookies.update({"service.zeus.tenant.id": self.tenant_id})

        # Set default headers
        self.session.headers.update(
            {"Content-Type": "application/json", "User-Agent": "Alation-DataQuality-SDK/1.0.0"}
        )

    def get_all_metric_data(self, monitor_id: str) -> Dict[str, MetricMetadata]:
        """Get all metric metadata for a monitor.

        Args:
            monitor_id: The monitor ID to get metrics for

        Returns:
            Dictionary mapping metric_id to MetricMetadata objects

        Raises:
            AlationAPIError: If API call fails
        """
        endpoint = f"{self.base_url}/dqms/api/monitors/{monitor_id}/metrics"

        try:
            response = self._make_request("GET", endpoint)
            log_api_request(self.logger, "GET", endpoint, response.status_code)

            data = response.json()

            if not isinstance(data, list):
                raise AlationAPIError("Expected a list of metric objects from the metrics API")

            # Convert to dictionary keyed by metric_id
            metric_dict = {}
            for metric_data in data:
                metric = MetricMetadata(metric_data)
                if metric.metric_id:
                    metric_dict[str(metric.metric_id)] = metric

            self.logger.info(f"Retrieved {len(metric_dict)} metrics for monitor {monitor_id}")
            return metric_dict

        except requests.RequestException as e:
            raise NetworkError(f"Failed to retrieve metrics from Alation: {str(e)}", e)
        except json.JSONDecodeError as e:
            raise AlationAPIError(f"Invalid JSON response from metrics endpoint: {str(e)}")

    def get_all_checks_data(self, monitor_id: str) -> List[MonitorCheckResponse]:
        """Get all checks data for a monitor.

        Args:
            monitor_id: The monitor ID to get checks for

        Returns:
            List of MonitorCheckResponse objects

        Raises:
            AlationAPIError: If API call fails
        """
        # Use the standard checks endpoint
        endpoint = f"{self.base_url}/dqms/api/monitors/{monitor_id}/checks"

        try:
            response = self._make_request("GET", endpoint)
            log_api_request(self.logger, "GET", endpoint, response.status_code)

            # The API returns YAML content as a JSON-encoded string, so we need to decode it first
            try:
                # First try to parse as JSON to get the actual YAML content
                json_data = json.loads(response.text)
                if isinstance(json_data, str):
                    # The JSON contains a YAML string, parse it
                    yaml_data = yaml.safe_load(json_data)
                else:
                    # The JSON is already structured data
                    yaml_data = json_data
            except json.JSONDecodeError:
                # Fallback: try to parse directly as YAML
                yaml_data = yaml.safe_load(response.text)

            if not isinstance(yaml_data, list):
                raise AlationAPIError("Expected a list of check objects from the checks API")

            # Convert to MonitorCheckResponse objects
            check_responses = []
            for item in yaml_data:
                ds_id = item.get("ds_id")
                dbtype = item.get("dbtype")
                checks_data = item.get("checks")

                if not ds_id or not dbtype or not checks_data:
                    self.logger.warning(f"Skipping incomplete check data: {item}")
                    continue

                # Convert checks data back to YAML string
                checks_yaml = yaml.dump(checks_data, sort_keys=False)

                check_response = MonitorCheckResponse(
                    ds_id=ds_id, dbtype=dbtype, checks=checks_yaml
                )
                check_responses.append(check_response)

            self.logger.info(
                f"Retrieved {len(check_responses)} check configurations for monitor {monitor_id}"
            )
            return check_responses

        except requests.RequestException as e:
            raise NetworkError(f"Failed to retrieve checks from Alation: {str(e)}", e)
        except yaml.YAMLError as e:
            raise AlationAPIError(f"Invalid YAML response from checks endpoint: {str(e)}")
        except Exception as e:
            raise AlationAPIError(f"Failed to parse checks response: {str(e)}")

    def get_ocf_configuration(self, datasource_id: int) -> Dict[str, Any]:
        """Get OCF configuration for a datasource.

        Args:
            datasource_id: The datasource ID to get configuration for

        Returns:
            Dictionary containing OCF configuration data

        Raises:
            AlationAPIError: If API call fails
        """
        endpoint = f"{self.base_url}/api/dq/query_service_metadata/"
        data = {"datasource_id": datasource_id}

        try:
            response = self._make_request("POST", endpoint, data=data)
            log_api_request(self.logger, "POST", endpoint, response.status_code)

            response_data = response.json()

            if "error" in response_data:
                raise AlationAPIError(
                    f"Error getting OCF configuration for datasource {datasource_id}: {response_data['error']}",
                    response.status_code,
                    response.text,
                )

            if "protobuf_config" not in response_data:
                raise AlationAPIError("No protobuf_config found in OCF configuration response")

            self.logger.info(f"Retrieved OCF configuration for datasource {datasource_id}")

            return response_data

        except requests.RequestException as e:
            raise NetworkError(f"Failed to retrieve OCF configuration: {str(e)}", e)
        except json.JSONDecodeError as e:
            raise AlationAPIError(
                f"Invalid JSON response from OCF configuration endpoint: {str(e)}"
            )

    def send_result_for_scan(
        self,
        tenant_id: str,
        job_id: str,
        request_id: str,
        monitor_id: str,
        result: Dict[str, Any],
        ds_id: int,
        last_result: bool = False,
        job_type: str = "94",
    ) -> None:
        """Send scan results to the ingestion service.

        Args:
            tenant_id: Tenant identifier
            job_id: Job identifier
            request_id: Request identifier
            monitor_id: Monitor identifier
            result: Scan result data
            ds_id: Datasource identifier
            last_result: Whether this is the last result in a batch
            job_type: Type of job being executed

        Raises:
            AlationAPIError: If API call fails
        """
        import time

        # Modify request_id to include timestamp
        timestamped_request_id = f"{request_id}{int(time.time())}"

        # Construct the ingestion endpoint
        endpoint = (
            f"{self.base_url}/dqings/api/dq/tenants/{tenant_id}/jobs/{job_id}/"
            f"requests/{timestamped_request_id}/monitors/{monitor_id}/events/ingest/"
        )

        params = {
            "isLastResult": "true" if last_result else "false",
            "ds_id": str(ds_id),
            "job_type": job_type,
        }

        try:
            response = self._make_request("POST", endpoint, params=params, json=result)
            log_api_request(self.logger, "POST", endpoint, response.status_code)

            # Try to parse response even if it might be empty
            try:
                response_data = response.json()
                self.logger.info(f"Successfully sent scan results for datasource {ds_id}")
            except json.JSONDecodeError:
                # Some APIs don't return JSON, just check status code
                self.logger.info(
                    f"Successfully sent scan results for datasource {ds_id} (no response body)"
                )

        except requests.RequestException as e:
            raise NetworkError(f"Failed to send scan results: {str(e)}", e)

    def save_sample_failed_check_queries(
        self, monitor_id: str, job_id: str, samples: List[SampleFailedRowQuery]
    ) -> Any:
        """Save sample failed check queries.

        Args:
            monitor_id: Monitor identifier
            job_id: Job identifier
            samples: List of sample failed row queries

        Returns:
            Server response (if any)

        Raises:
            AlationAPIError: If API call fails
        """
        endpoint = f"{self.base_url}/dqms/api/monitors/{monitor_id}/jobs/{job_id}/sample-failed-check-queries"

        # Convert to dictionaries for JSON serialization
        samples_data = [sample.to_dict() for sample in samples]

        try:
            response = self._make_request("POST", endpoint, json=samples_data)
            log_api_request(self.logger, "POST", endpoint, response.status_code)

            self.logger.info(f"Successfully saved {len(samples)} sample failed check queries")

            # Return JSON if provided; else None
            try:
                return response.json()
            except json.JSONDecodeError:
                return None

        except requests.RequestException as e:
            raise NetworkError(f"Failed to save sample failed check queries: {str(e)}", e)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to make request to
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        try:
            response = self.session.request(method=method, url=url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout as e:
            raise requests.RequestException(f"Request timeout after {self.timeout} seconds") from e
        except requests.exceptions.ConnectionError as e:
            raise requests.RequestException(f"Connection error: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            # Re-raise with more context
            raise e

    def _extract_checks_from_response(self, data: Any) -> List[str]:
        """Extract SodaCL check blocks from API response.

        Args:
            data: Response data from checks API

        Returns:
            List of SodaCL check blocks as strings

        Raises:
            AlationAPIError: If no checks found or invalid format
        """
        checks_blocks = []

        if isinstance(data, list):
            # Response is a list of items, each with checks
            for item in data:
                if isinstance(item, dict) and "checks" in item:
                    checks_content = item["checks"]
                    if isinstance(checks_content, str) and checks_content.strip():
                        checks_blocks.append(checks_content.strip())
                    elif isinstance(checks_content, dict):
                        # Convert dict to YAML string
                        import yaml

                        checks_blocks.append(yaml.dump(checks_content, sort_keys=False))

        elif isinstance(data, dict):
            # Try different possible keys for checks content
            for key in ("dq_checks", "checks", "content"):
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    checks_blocks.append(val.strip())
                    break
                elif isinstance(val, list):
                    # Join list into one block
                    joined = "\n---\n".join([str(x) for x in val if str(x).strip()])
                    if joined.strip():
                        checks_blocks.append(joined.strip())
                    break

        if not checks_blocks:
            raise AlationAPIError("No SodaCL checks found in API response")

        return checks_blocks

    def health_check(self) -> bool:
        """Perform a health check on the Alation connection.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            # Try a simple API call to verify connectivity
            endpoint = f"{self.base_url}/api/health"
            response = self.session.get(endpoint, timeout=5)
            return response.status_code < 400
        except:
            return False

"""Soda Core scan execution and result processing."""

import os
import tempfile
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..utils.exceptions import DatasourceConfigError, SodaScanError
from ..utils.logging import get_logger, log_scan_progress

if TYPE_CHECKING:
    from soda.scan import Scan


class SodaRunner:
    """Handles Soda Core scan execution and result processing following soda_check.py pattern."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def execute_ds_scan(
        self,
        check_data: Dict[str, Any],
        ocf_config: Dict[str, Any],
        metric_dict: Dict[str, Any] = None,
        logger=None,
    ) -> Dict[str, Any]:
        """Execute a Soda Core scan for a single datasource.

        Args:
            check_data: Check data containing ds_id, dbtype, and checks YAML
            ocf_config: OCF configuration for the datasource
            metric_dict: Dictionary of metric metadata (optional)
            logger: Optional logger instance

        Returns:
            Dictionary containing scan results

        Raises:
            SodaScanError: If scan execution fails
        """
        try:
            # Import Soda Core
            from soda.scan import Scan
        except ImportError as e:
            raise SodaScanError(
                "Soda Core not available. Install with: pip install soda-core"
            ) from e

        scan = None

        try:
            # Initialize scan
            scan = Scan()

            # Set datasource name to db type (following soda_check.py pattern)
            datasource_name = check_data.get("dbtype", f"ds_{check_data.get('ds_id')}")
            scan.set_data_source_name(datasource_name)

            # Add SodaCL YAML
            checks_yaml = check_data.get("checks")
            if checks_yaml and isinstance(checks_yaml, str) and checks_yaml.strip():
                scan.add_sodacl_yaml_str(checks_yaml)
            else:
                raise SodaScanError("No valid checks YAML found in check data")

            # Decode the protobuf config and generate Soda YAML configuration
            from ..datasource.config_generator import DatasourceConfigGenerator

            # Generate Soda YAML configuration using existing infrastructure
            config_gen = DatasourceConfigGenerator()
            datasource_yaml = config_gen.generate_soda_config(
                datasource_name=check_data.get(
                    "dbtype", datasource_name
                ),  # Use dbtype as datasource name
                protobuf_config_b64=ocf_config["protobuf_config"],
                db_type=check_data.get("dbtype"),
            )

            # Add YAML configuration to scan (instead of raw OCF config)
            scan.add_configuration_yaml_str(datasource_yaml)

            # Set logger if provided
            if logger:
                scan.set_logger(logger)
                scan.set_verbose(True)

            ds_id = check_data.get("ds_id")
            dbtype = check_data.get("dbtype")

            self.logger.debug(f"Executing scan for ds_id: {ds_id}, db_type: {dbtype}")

            # Execute scan with timing
            start_time = time.perf_counter()
            start_timestamp = datetime.now(timezone.utc)

            scan.execute()

            end_time = time.perf_counter()
            end_timestamp = datetime.now(timezone.utc)

            # Get scan results using Soda's built-in method
            result = scan.get_scan_results()

            self.logger.debug(f"Result: {result}")

            # Add timing and metadata
            if isinstance(result, dict):
                result.update(
                    {
                        "scanStartTimestamp": start_timestamp.isoformat(),
                        "scanEndTimestamp": end_timestamp.isoformat(),
                        "durationSeconds": round(end_time - start_time, 6),
                        "defaultDataSource": datasource_name,
                        "dataTimestamp": end_timestamp.isoformat(),
                    }
                )

            self.logger.debug(f"Execution of scan completed for ds_id: {ds_id}, db_type: {dbtype}")

            return result

        except Exception as e:
            # Collect logs even if scan failed
            logs = []
            if scan:
                try:
                    logs = self._collect_logs(scan)
                except:
                    pass

            raise SodaScanError(
                f"Soda scan execution failed for ds_id {check_data.get('ds_id')}: {str(e)}", logs
            ) from e

    def extract_sample_failed_queries(
        self,
        scan_result: dict,
        metric_dict: Dict[str, Any],
        ds_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Extracts sample failed rows queries from the scan result.

        Args:
            scan_result: Result from Soda scan execution
            metric_dict: Dictionary of metric metadata keyed by metric_id
            ds_id: Datasource identifier

        Returns:
            List of sample failed row query objects
        """
        failed_rows_queries = []

        for check in scan_result.get("checks", []):
            if check.get("outcome") != "fail":
                continue

            check_id = check.get("source_identity")
            if not check_id:
                self.logger.info(
                    "Check source_identity is missing, skipping sample failed rows query processing for this check."
                )
                continue

            soda_generated_sample_query = check.get("sampleFailedRowsQuery", "")
            user_provided_sample_query = metric_dict.get(check_id, {}).get(
                "sample_failed_query", ""
            )

            # Prefer user-provided; fall back to Soda-generated
            sample_failed_query = user_provided_sample_query or soda_generated_sample_query

            # Treat empty strings as missing
            if sample_failed_query:
                sample_failed_query_obj = {
                    "metric_unique_identifier": check_id,
                    "ds_id": ds_id,
                    "query": sample_failed_query,
                }
                failed_rows_queries.append(sample_failed_query_obj)

        return failed_rows_queries

    def execute_scan(
        self,
        datasource_name: str,
        datasource_config_yaml: str,
        checks_blocks: List[str],
        temp_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a Soda Core scan (legacy method for backward compatibility).

        This method is kept for backward compatibility but is deprecated.
        Use execute_ds_scan for new implementations.

        Args:
            datasource_name: Name of the datasource
            datasource_config_yaml: YAML configuration for the datasource
            checks_blocks: List of SodaCL check definition blocks
            temp_dir: Optional temporary directory for config files

        Returns:
            Dictionary containing scan results and metadata

        Raises:
            SodaScanError: If scan execution fails
        """
        self.logger.warning(
            "execute_scan is deprecated. Use execute_ds_scan with OCF configuration instead."
        )

        try:
            # Import Soda Core
            from soda.scan import Scan
        except ImportError as e:
            raise SodaScanError(
                "Soda Core not available. Install with: pip install soda-core"
            ) from e

        # Create temporary config file
        config_file = self._create_temp_config_file(datasource_config_yaml, temp_dir)
        scan = None

        try:
            # Initialize scan
            scan = Scan()
            scan.add_configuration_yaml_file(config_file)
            scan.set_data_source_name(datasource_name)

            # Add check definitions
            total_checks = 0
            for block in checks_blocks:
                if isinstance(block, str) and block.strip():
                    scan.add_sodacl_yaml_str(block)
                    # Count checks in block (rough estimate)
                    total_checks += block.count("\n") + 1

            log_scan_progress(self.logger, "Starting scan execution", total_checks)

            # Execute scan with timing
            start_time = time.perf_counter()
            start_timestamp = datetime.now(timezone.utc)

            scan.execute()

            end_time = time.perf_counter()
            end_timestamp = datetime.now(timezone.utc)

            log_scan_progress(self.logger, "Scan execution completed")

            # Collect results
            results = self._collect_scan_results(
                scan, datasource_name, start_timestamp, end_timestamp, end_time - start_time
            )

            return results

        except Exception as e:
            # Collect logs even if scan failed
            logs = []
            if scan:
                try:
                    logs = self._collect_logs(scan)
                except:
                    pass

            raise SodaScanError(f"Soda scan execution failed: {str(e)}", logs) from e

        finally:
            # Clean up temporary config file
            try:
                if config_file and os.path.exists(config_file):
                    os.remove(config_file)
            except:
                pass  # Ignore cleanup errors

    def _create_temp_config_file(self, config_yaml: str, temp_dir: Optional[str] = None) -> str:
        """Create a temporary configuration file.

        Args:
            config_yaml: YAML configuration content
            temp_dir: Optional temporary directory

        Returns:
            Path to the temporary file

        Raises:
            DatasourceConfigError: If file creation fails
        """
        try:
            temp_dir = temp_dir or tempfile.gettempdir()
            temp_file = tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", dir=temp_dir, delete=False, encoding="utf-8"
            )

            temp_file.write(config_yaml)
            temp_file.close()

            return temp_file.name

        except Exception as e:
            raise DatasourceConfigError(f"Failed to create temporary config file: {str(e)}") from e

    def _collect_scan_results(
        self,
        scan: "Scan",
        datasource_name: str,
        start_timestamp: datetime,
        end_timestamp: datetime,
        duration: float,
    ) -> Dict[str, Any]:
        """Collect comprehensive scan results.

        Args:
            scan: Executed Soda scan object
            datasource_name: Name of the datasource
            start_timestamp: Scan start time
            end_timestamp: Scan end time
            duration: Scan duration in seconds

        Returns:
            Dictionary containing all scan results and metadata
        """
        # Collect logs
        logs = self._collect_logs(scan)

        # Collect structured results
        structured = self._collect_structured_results(scan)

        # Analyze results
        analysis = self._analyze_results(structured, logs)

        # Build comprehensive result object
        result = {
            "definitionName": None,
            "defaultDataSource": datasource_name,
            "dataTimestamp": end_timestamp.isoformat(),
            "scanStartTimestamp": start_timestamp.isoformat(),
            "scanEndTimestamp": end_timestamp.isoformat(),
            "durationSeconds": round(duration, 6),
            # Status flags
            "hasErrors": analysis["has_errors"],
            "hasWarnings": analysis["has_warnings"],
            "hasFailures": analysis["has_failures"],
            # Structured data
            "metrics": structured.get("metrics", []) if structured else [],
            "checks": structured.get("checks", []) if structured else [],
            "queries": structured.get("queries", []) if structured else [],
            "automatedMonitoringChecks": structured.get("automatedMonitoringChecks", [])
            if structured
            else [],
            "profiling": structured.get("profiling", []) if structured else [],
            "metadata": structured.get("metadata", []) if structured else [],
            "logs": logs,
            # Analysis and summary
            "summary": analysis["summary"],
            "failed_checks": analysis["failed_checks"],
            "warning_checks": analysis["warning_checks"],
            "passed_checks": analysis["passed_checks"],
            # Raw data for debugging
            "sodaRaw": structured if structured else None,
        }

        self.logger.info(
            f"Scan completed: {analysis['summary']['total_checks']} checks, "
            f"{analysis['summary']['passed']} passed, "
            f"{analysis['summary']['failed']} failed, "
            f"{analysis['summary']['warnings']} warnings"
        )

        return result

    def _collect_logs(self, scan: "Scan") -> List[Dict[str, Any]]:
        """Collect logs from Soda scan.

        Args:
            scan: Soda scan object

        Returns:
            List of log entries
        """
        try:
            if hasattr(scan, "get_logs"):
                logs = scan.get_logs()
                normalized_logs = []

                for idx, log_entry in enumerate(logs):
                    if isinstance(log_entry, dict):
                        entry = {
                            "level": log_entry.get("level") or log_entry.get("severity") or "INFO",
                            "message": log_entry.get("message") or log_entry.get("text") or "",
                            "timestamp": log_entry.get("timestamp")
                            or datetime.now(timezone.utc).isoformat(),
                            "index": log_entry.get("index", idx),
                            "doc": log_entry.get("doc"),
                            "location": log_entry.get("location"),
                        }
                    else:
                        entry = {
                            "level": "INFO",
                            "message": str(log_entry),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "index": idx,
                            "doc": None,
                            "location": None,
                        }

                    normalized_logs.append(entry)

                return normalized_logs

        except Exception as e:
            self.logger.warning(f"Failed to collect scan logs: {str(e)}")

        # Fallback log entry
        return [
            {
                "level": "INFO",
                "message": "Soda scan executed (log collection fallback)",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "index": 0,
                "doc": None,
                "location": None,
            }
        ]

    def _collect_structured_results(self, scan: "Scan") -> Optional[Dict[str, Any]]:
        """Collect structured results from Soda scan.

        Args:
            scan: Soda scan object

        Returns:
            Dictionary with structured results or None if not available
        """
        # Try various methods to get structured results
        methods_to_try = [
            "get_scan_results",
            "scan_results",
            "get_result_json",
            "get_results_json",
            "get_json_output_str",
            "get_json_results_str",
            "get_result",
        ]

        for method_name in methods_to_try:
            try:
                if hasattr(scan, method_name):
                    method = getattr(scan, method_name)

                    if callable(method):
                        result = method()
                    else:
                        result = method

                    if isinstance(result, str):
                        import json

                        result = json.loads(result)

                    if isinstance(result, dict):
                        return result

            except Exception as e:
                self.logger.debug(f"Method {method_name} failed: {str(e)}")
                continue

        self.logger.warning("Could not collect structured results from Soda scan")
        return None

    def _analyze_results(self, structured: Optional[Dict], logs: List[Dict]) -> Dict[str, Any]:
        """Analyze scan results to extract key information.

        Args:
            structured: Structured results from Soda
            logs: Log entries from Soda

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "has_errors": False,
            "has_warnings": False,
            "has_failures": False,
            "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0, "errors": 0},
            "failed_checks": [],
            "warning_checks": [],
            "passed_checks": [],
        }

        # Analyze structured results if available
        if structured and "checks" in structured:
            checks = structured["checks"]
            analysis["summary"]["total_checks"] = len(checks)

            for check in checks:
                status = (check.get("outcome") or check.get("status") or "UNKNOWN").upper()
                check_info = {
                    "name": check.get("name", "Unknown"),
                    "table": check.get("table", "Unknown"),
                    "column": check.get("column"),
                    "status": status,
                    "actual_value": check.get("actualValue"),
                    "expected_value": check.get("expectedValue"),
                    "message": check.get("description") or check.get("message", ""),
                    "raw_check": check,
                }

                if status in ("FAIL", "FAILED"):
                    analysis["summary"]["failed"] += 1
                    analysis["failed_checks"].append(check_info)
                    analysis["has_failures"] = True
                elif status in ("WARN", "WARNING"):
                    analysis["summary"]["warnings"] += 1
                    analysis["warning_checks"].append(check_info)
                    analysis["has_warnings"] = True
                elif status in ("PASS", "PASSED"):
                    analysis["summary"]["passed"] += 1
                    analysis["passed_checks"].append(check_info)

        # Analyze logs for errors and warnings
        for log_entry in logs:
            level = log_entry.get("level", "INFO").upper()
            if level == "ERROR":
                analysis["has_errors"] = True
                analysis["summary"]["errors"] += 1
            elif level in ("WARN", "WARNING"):
                analysis["has_warnings"] = True

        return analysis

    def build_clean_payload(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build a clean payload for uploading results.

        Args:
            raw_results: Raw scan results

        Returns:
            Cleaned payload suitable for API upload
        """
        payload = dict(raw_results)

        # Remove None values to keep payload clean
        for key in list(payload.keys()):
            if payload[key] is None:
                del payload[key]

        # Remove large raw data if not needed
        if "sodaRaw" in payload and len(str(payload["sodaRaw"])) > 50000:
            # Keep only summary of large raw data
            payload["sodaRaw"] = {
                "size": len(str(payload["sodaRaw"])),
                "summary": "Raw data truncated due to size",
            }

        return payload

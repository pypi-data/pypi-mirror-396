"""Main entry point for the Alation Data Quality SDK."""

import os
import sys
from typing import Any, Dict, Optional, Union

from .client.alation_client import AlationClient
from .config import SDKConfig
from .datasource.config_generator import DatasourceConfigGenerator
from .datasource.soda_runner import SodaRunner
from .utils.exceptions import DataQualitySDKError
from .utils.logging import setup_logging


class DataQualityRunner:
    """Main orchestrator for running Alation data quality checks."""

    def __init__(self, config: Optional[SDKConfig] = None):
        """Initialize the Data Quality Runner.

        Args:
            config: Optional SDK configuration. If not provided, will load from environment.
        """
        self.config = config or SDKConfig.from_env()
        self.logger = setup_logging(self.config.log_level)
        self.config.validate()

        # Initialize components
        self.alation_client = AlationClient(
            base_url=self.config.alation_host,
            api_token=self.config.api_token,
            timeout=self.config.timeout,
            tenant_id=self.config.tenant_id,
        )
        self.config_generator = DatasourceConfigGenerator()  # Keep for backward compatibility
        self.soda_runner = SodaRunner()

        self.logger.info(f"Data Quality SDK initialized for monitor {self.config.monitor_id}")

    def run_checks(self, return_detailed_results: bool = True) -> Union[int, Dict[str, Any]]:
        """Execute data quality checks for the configured monitor following soda_check.py pattern.

        Args:
            return_detailed_results: If True, return detailed results dict. If False, return exit code.

        Returns:
            Either detailed results dictionary or exit code (0 = success, >0 = failure)
        """
        # Initialize result structure
        detailed_result = {
            "exit_code": 0,
            "monitor_id": self.config.monitor_id,
            "alation_host": self.config.alation_host,
            "execution_metadata": {
                "sdk_version": "1.0.0",
                "dry_run": self.config.dry_run,
                "tenant_id": self.config.tenant_id,
                "job_id": self.config.job_id,
                "request_id": self.config.request_id,
            },
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "errors": 0,
                "datasources_processed": 0,
            },
            "failed_checks": [],
            "warning_checks": [],
            "passed_checks": [],
            "all_scan_results": [],  # Store results from all datasources
            "upload_status": "not_attempted",
            "upload_responses": [],  # Store responses from all uploads
            "recommendations": [],
            "errors": [],
        }

        self.logger.info("Starting Data Quality Monitor execution")

        success = True
        error_message = ""

        try:
            # Step 1: Get metric metadata
            metric_dict = {}
            try:
                metric_dict = self.alation_client.get_all_metric_data(self.config.monitor_id)
                self.logger.info(
                    f"Fetched {len(metric_dict)} metrics for monitor {self.config.monitor_id}"
                )
                detailed_result["execution_metadata"]["metrics_count"] = len(metric_dict)
            except Exception as e:
                self.logger.warning(
                    f"Failed to fetch metrics for monitor {self.config.monitor_id}: {e}"
                )
                detailed_result["errors"].append(f"Failed to fetch metrics: {str(e)}")

            # Step 2: Get all checks data
            try:
                all_checks = self.alation_client.get_all_checks_data(self.config.monitor_id)

                self.logger.info(
                    f"Retrieved {len(all_checks)} check configurations for monitor {self.config.monitor_id}"
                )
                detailed_result["execution_metadata"]["datasources_count"] = len(all_checks)

                if not all_checks:
                    self.logger.warning("No checks found for monitor")
                    detailed_result["exit_code"] = 2
                    detailed_result["errors"].append("No checks found for monitor")
                    return detailed_result if return_detailed_results else 2

            except Exception as e:
                self.logger.error(
                    f"Failed to fetch checks for monitor {self.config.monitor_id}: {e}"
                )
                detailed_result["exit_code"] = 2
                detailed_result["errors"].append(f"Failed to fetch checks: {str(e)}")
                return detailed_result if return_detailed_results else 2

            # Step 3: Execute scans for each datasource
            for i, check_data in enumerate(all_checks):
                is_last_check = i == len(all_checks) - 1
                ds_id = check_data.ds_id
                dbtype = check_data.dbtype

                self.logger.info(
                    f"Processing datasource {i+1}/{len(all_checks)}: ds_id={ds_id}, type={dbtype}"
                )

                try:
                    if self.config.dry_run:
                        self.logger.info(f"DRY RUN: Skipping scan execution for datasource {ds_id}")
                        # Create mock result for dry run
                        mock_result = {
                            "ds_id": ds_id,
                            "dbtype": dbtype,
                            "dry_run": True,
                            "checks": [],
                            "message": "Dry run - scan execution skipped",
                        }
                        detailed_result["all_scan_results"].append(mock_result)
                        continue

                    # Execute the scan for this datasource
                    result = self.execute_ds_scan(check_data, is_last_check, metric_dict)

                    if result:
                        detailed_result["all_scan_results"].append(result)
                        self._merge_scan_results(detailed_result, result)
                        detailed_result["summary"]["datasources_processed"] += 1

                except Exception as e:
                    self.logger.error(f"Failed to execute scan for datasource {ds_id}: {e}")
                    detailed_result["errors"].append(
                        f"Scan failed for datasource {ds_id}: {str(e)}"
                    )
                    success = False
                    error_message = f"Scan execution failed for datasource {ds_id}: {str(e).rstrip('.')}. Contact Alation support for further assistance."

            # Step 4: Determine overall results
            if not success or detailed_result["summary"]["failed"] > 0:
                detailed_result["exit_code"] = 1

            # Step 5: Generate recommendations
            self._generate_recommendations(detailed_result)

            if self.config.dry_run:
                detailed_result["upload_status"] = "skipped_dry_run"
                self.logger.info("DRY RUN: Results upload was skipped")

            self.logger.info("Data Quality execution completed successfully")
            return detailed_result if return_detailed_results else detailed_result["exit_code"]

        except Exception as e:
            self.logger.error(f"Exception during checks execution: {e}")
            detailed_result["exit_code"] = 5
            detailed_result["errors"].append(f"Unexpected error: {str(e)}")
            detailed_result["recommendations"].append("Contact support with error details")
            return detailed_result if return_detailed_results else 5

    def execute_ds_scan(
        self, check_data, is_last_check: bool, metric_dict: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute scan for a single datasource.

        Args:
            check_data: MonitorCheckResponse object containing check configuration
            is_last_check: Whether this is the last datasource to process
            metric_dict: Dictionary of metric metadata

        Returns:
            Scan result dictionary or None if failed
        """
        ds_id = check_data.ds_id
        dbtype = check_data.dbtype

        try:
            # Get OCF configuration for this datasource
            self.logger.info(f"Getting OCF configuration for datasource {ds_id}")
            ocf_config = self.alation_client.get_ocf_configuration(ds_id)

            # Prepare check data for scan
            check_data_dict = {"ds_id": ds_id, "dbtype": dbtype, "checks": check_data.checks}

            # Execute the scan using SodaRunner
            self.logger.info(f"Executing Soda scan for datasource {ds_id}")
            result = self.soda_runner.execute_ds_scan(
                check_data=check_data_dict,
                ocf_config=ocf_config,
                metric_dict=metric_dict,
                logger=self.logger,
            )

            # Send results to Alation
            if not self.config.dry_run:
                try:
                    self.send_result_for_scan(result, is_last_check, ds_id)

                    # Process and send sample failed queries
                    self.push_sample_failed_queries(result, metric_dict, ds_id)

                except Exception as e:
                    self.logger.error(f"Failed to send results for datasource {ds_id}: {e}")
                    # Don't fail the entire run for upload issues

            return result

        except Exception as e:
            self.logger.error(f"Failed to execute scan for datasource {ds_id}: {e}")
            raise

    def send_result_for_scan(
        self, result: Dict[str, Any], is_last_result: bool, ds_id: int
    ) -> None:
        """Send scan results to Alation ingestion service.

        Args:
            result: Scan result data
            is_last_result: Whether this is the last result in the batch
            ds_id: Datasource identifier
        """
        if not self.config.tenant_id:
            self.logger.warning("No tenant_id configured, skipping results upload")
            return

        try:
            self.alation_client.send_result_for_scan(
                tenant_id=self.config.tenant_id,
                job_id=self.config.job_id,
                request_id=self.config.request_id,
                monitor_id=self.config.monitor_id,
                result=result,
                ds_id=ds_id,
                last_result=is_last_result,
                job_type=self.config.job_type,
            )
            self.logger.info(f"Successfully sent scan results for datasource {ds_id}")

        except Exception as e:
            self.logger.error(f"Failed to send scan results for datasource {ds_id}: {e}")
            raise

    def push_sample_failed_queries(
        self, scan_result: Dict[str, Any], metric_dict: Dict[str, Any], ds_id: int
    ) -> None:
        """Extract and push sample failed row queries.

        Args:
            scan_result: Result from Soda scan execution
            metric_dict: Dictionary of metric metadata
            ds_id: Datasource identifier
        """
        try:
            # Extract sample failed queries
            failed_queries = self.soda_runner.extract_sample_failed_queries(
                scan_result, metric_dict, ds_id
            )

            if failed_queries:
                # Convert to SampleFailedRowQuery objects
                from .client.alation_client import SampleFailedRowQuery

                sample_objects = [
                    SampleFailedRowQuery(
                        metric_unique_identifier=q["metric_unique_identifier"],
                        ds_id=q["ds_id"],
                        query=q["query"],
                    )
                    for q in failed_queries
                ]

                # Send to Alation
                self.alation_client.save_sample_failed_check_queries(
                    monitor_id=self.config.monitor_id,
                    job_id=self.config.job_id,
                    samples=sample_objects,
                )

                self.logger.info(
                    f"Successfully pushed {len(failed_queries)} sample failed queries for datasource {ds_id}"
                )

        except Exception as e:
            self.logger.error(f"Failed to push sample failed queries for datasource {ds_id}: {e}")
            # Don't fail the main process for this

    def _merge_scan_results(self, detailed_result: Dict[str, Any], scan_result: Dict[str, Any]):
        """Merge scan results into the detailed result structure.

        Args:
            detailed_result: Accumulated results from all scans
            scan_result: Result from a single Soda scan
        """
        # Process checks from Soda Core's get_scan_results() format
        checks = scan_result.get("checks", [])

        for check in checks:
            outcome = check.get("outcome", "").lower()

            # Create standardized check info
            check_info = {
                "name": check.get("name", "Unknown"),
                "table": check.get("table", "Unknown"),
                "column": check.get("column"),
                "status": outcome.upper(),
                "actual_value": check.get("actualValue"),
                "expected_value": check.get("expectedValue"),
                "message": check.get("description") or check.get("message", ""),
                "severity": self._determine_check_severity(check),
                "check_type": check.get("type", "Unknown"),
                "location": check.get("location", {}),
                "raw_check": check,
                "ds_id": scan_result.get("ds_id"),  # Add datasource context
                "dbtype": scan_result.get("dbtype"),
            }

            # Add to appropriate lists and update counters
            detailed_result["summary"]["total_checks"] += 1

            if outcome in ("fail", "failed"):
                detailed_result["summary"]["failed"] += 1
                detailed_result["failed_checks"].append(check_info)
            elif outcome in ("warn", "warning"):
                detailed_result["summary"]["warnings"] += 1
                detailed_result["warning_checks"].append(check_info)
            elif outcome in ("pass", "passed"):
                detailed_result["summary"]["passed"] += 1
                detailed_result["passed_checks"].append(check_info)
            elif outcome == "error":
                detailed_result["summary"]["errors"] += 1
                # Treat errors as failures for practical purposes
                detailed_result["failed_checks"].append(check_info)

        # Update execution metadata with timing info
        if "durationSeconds" in scan_result:
            # Accumulate total duration
            current_duration = detailed_result["execution_metadata"].get(
                "total_duration_seconds", 0
            )
            detailed_result["execution_metadata"]["total_duration_seconds"] = (
                current_duration + scan_result["durationSeconds"]
            )

    def _determine_check_severity(self, check: Dict[str, Any]) -> str:
        """Determine the severity of a check based on its properties."""
        check_name = check.get("name", "").lower()

        # Critical checks
        if any(keyword in check_name for keyword in ["freshness", "duplicate", "missing_count"]):
            return "CRITICAL"
        elif any(keyword in check_name for keyword in ["row_count", "schema"]):
            return "HIGH"
        else:
            return "MEDIUM"

    def _generate_recommendations(self, detailed_result: Dict[str, Any]):
        """Generate actionable recommendations based on results."""
        recommendations = detailed_result["recommendations"]
        summary = detailed_result["summary"]

        # Check-specific recommendations
        for failed_check in detailed_result["failed_checks"]:
            check_name = failed_check.get("name", "").lower()
            table = failed_check.get("table", "Unknown")

            if "freshness" in check_name:
                recommendations.append(
                    f"🕒 Data freshness issue in {table}: Check ETL pipeline schedules"
                )
            elif "duplicate" in check_name:
                recommendations.append(
                    f"🔄 Duplicate data detected in {table}: Review data deduplication logic"
                )
            elif "missing" in check_name or "null" in check_name:
                recommendations.append(
                    f"❓ Missing data in {table}: Validate data source completeness"
                )
            elif "row_count" in check_name or "count" in check_name:
                recommendations.append(
                    f"📊 Row count issue in {table}: Check data ingestion process"
                )

        # General recommendations based on failure patterns
        failed_count = summary["failed"]
        if failed_count > 10:
            recommendations.append(
                "⚠️ High number of failures detected - consider reviewing data pipeline health"
            )
        elif failed_count > 5:
            recommendations.append("⚠️ Multiple failures detected - investigate common root causes")

        # Pipeline recommendations
        if failed_count > 0:
            recommendations.append(
                "🛑 PIPELINE ACTION: Consider failing pipeline due to data quality issues"
            )
            recommendations.append(
                "📋 Review failed checks and determine if data is safe to use downstream"
            )
        else:
            recommendations.append(
                "✅ PIPELINE ACTION: All quality checks passed - safe to continue pipeline"
            )

        # Remove duplicates
        detailed_result["recommendations"] = list(dict.fromkeys(recommendations))

    def _determine_exit_code(self, detailed_result: Dict[str, Any]):
        """Determine the final exit code based on results."""
        if detailed_result["errors"]:
            # Already has an error code set
            return

        summary = detailed_result["summary"]

        # Exit code 1 for quality check failures
        if summary["failed"] > 0:
            detailed_result["exit_code"] = 1
        else:
            detailed_result["exit_code"] = 0

    def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check of the SDK setup.

        Returns:
            Dictionary with health check results
        """
        health = {"status": "healthy", "checks": {}, "recommendations": []}

        # Check Alation connectivity
        try:
            alation_healthy = self.alation_client.health_check()
            health["checks"]["alation_connectivity"] = "ok" if alation_healthy else "failed"
            if not alation_healthy:
                health["status"] = "degraded"
                health["recommendations"].append("Check Alation connectivity")
        except Exception as e:
            health["checks"]["alation_connectivity"] = f"error: {str(e)}"
            health["status"] = "unhealthy"

        # Check Soda Core availability
        try:
            health["checks"]["soda_core"] = "ok"
        except ImportError:
            health["checks"]["soda_core"] = "missing"
            health["status"] = "unhealthy"
            health["recommendations"].append("Install Soda Core: pip install soda-core")

        # Check configuration
        try:
            self.config.validate()
            health["checks"]["configuration"] = "ok"
        except Exception as e:
            health["checks"]["configuration"] = f"invalid: {str(e)}"
            health["status"] = "unhealthy"

        return health


def cli_main():
    """Command-line interface main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Alation Data Quality SDK - Execute data quality checks using Soda Core"
    )
    parser.add_argument(
        "--health-check", action="store_true", help="Perform a health check and exit"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without executing scans or uploading results",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument(
        "--exit-code-only",
        action="store_true",
        help="Return only exit code (for pipeline integration)",
    )

    args = parser.parse_args()

    # Override environment variables with CLI arguments
    if args.dry_run:
        os.environ["DRY_RUN"] = "true"
    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level

    try:
        config = SDKConfig.from_env()
        runner = DataQualityRunner(config)

        if args.health_check:
            health = runner.health_check()
            print(f"Health Status: {health['status']}")
            for check, result in health["checks"].items():
                print(f"  {check}: {result}")
            if health["recommendations"]:
                print("Recommendations:")
                for rec in health["recommendations"]:
                    print(f"  - {rec}")
            sys.exit(0 if health["status"] == "healthy" else 1)

        # Run the checks
        result = runner.run_checks(return_detailed_results=not args.exit_code_only)

        if args.exit_code_only:
            sys.exit(result)
        else:
            # Print summary
            print(f"Execution completed with exit code: {result['exit_code']}")
            print(f"Checks summary: {result['summary']}")
            if result["recommendations"]:
                print("Recommendations:")
                for rec in result["recommendations"]:
                    print(f"  - {rec}")
            sys.exit(result["exit_code"])

    except DataQualitySDKError as e:
        print(f"SDK Error: {str(e)}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(5)


if __name__ == "__main__":
    cli_main()

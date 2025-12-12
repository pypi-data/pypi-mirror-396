#!/usr/bin/env python3
"""
Basic usage example for the Alation Data Quality SDK.

This example demonstrates the simplest way to use the SDK to run data quality checks.
"""

import os

from data_quality_sdk import DataQualityRunner, SDKConfig


def basic_example():
    """Run data quality checks with basic configuration."""
    print("=== Basic Data Quality SDK Usage ===\n")

    # Method 1: Use environment variables (recommended for production)
    print("1. Using environment variables:")
    print("   Set ALATION_HOST and MONITOR_ID environment variables")

    # Check if environment variables are set
    if os.getenv("ALATION_HOST") and os.getenv("MONITOR_ID"):
        try:
            runner = DataQualityRunner()
            result = runner.run_checks()

            print(f"✅ Checks completed with exit code: {result['exit_code']}")
            print(f"Summary: {result['summary']}")

            if result["recommendations"]:
                print("\nRecommendations:")
                for rec in result["recommendations"]:
                    print(f"  - {rec}")

        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("   (Environment variables not set, skipping execution)")

    # Method 2: Use configuration object
    print("\n2. Using configuration object:")

    # Example configuration (replace with your values)
    config = SDKConfig(
        alation_host="https://your-alation.company.com",
        monitor_id="123",
        api_token=None,  # Optional
        tenant_id=None,  # Required for results upload in production
        job_id="example_job",
        request_id="example_request",
        timeout=30,
        log_level="INFO",
        dry_run=True,  # Set to True for testing
    )

    try:
        runner = DataQualityRunner(config)
        result = runner.run_checks()

        print(f"✅ Dry run completed with exit code: {result['exit_code']}")
        print(f"Summary: {result['summary']}")

    except Exception as e:
        print(f"❌ Error: {e}")


def health_check_example():
    """Demonstrate health check functionality."""
    print("\n=== Health Check Example ===\n")

    try:
        # You can run health check even without valid configuration
        # to test basic SDK setup
        runner = DataQualityRunner()
        health = runner.health_check()

        print(f"Health Status: {health['status']}")
        print("Component Checks:")
        for component, status in health["checks"].items():
            print(f"  {component}: {status}")

        if health["recommendations"]:
            print("\nRecommendations:")
            for rec in health["recommendations"]:
                print(f"  - {rec}")

    except Exception as e:
        print(f"❌ Health check failed: {e}")


def error_handling_example():
    """Demonstrate error handling with invalid configuration."""
    print("\n=== Error Handling Example ===\n")

    # Example with invalid configuration to show error handling
    config = SDKConfig(
        alation_host="https://invalid-host.example.com",
        monitor_id="999999",
        timeout=5,  # Short timeout for quick failure
        dry_run=True,  # Use dry run to avoid actual network calls in most cases
    )

    try:
        runner = DataQualityRunner(config)
        result = runner.run_checks()

        # Even if it "succeeds" in dry run, show the structure
        print("Result structure:")
        print(f"  Exit code: {result['exit_code']}")
        print(f"  Errors: {result.get('errors', [])}")
        print(f"  Monitor ID: {result.get('monitor_id')}")
        print(f"  Execution metadata: {result.get('execution_metadata', {})}")

    except Exception as e:
        print(f"❌ Expected error with invalid config: {e}")
        print("This demonstrates the SDK's error handling capabilities.")


def detailed_results_example():
    """Show how to access detailed results."""
    print("\n=== Detailed Results Example ===\n")

    # This example shows what kind of detailed information is available
    # (using a mock result since we don't have real credentials)

    mock_result = {
        "exit_code": 1,
        "monitor_id": "123",
        "alation_host": "https://your-alation.company.com",
        "summary": {
            "total_checks": 5,
            "passed": 3,
            "failed": 2,
            "warnings": 0,
            "errors": 0,
            "datasources_processed": 2,
        },
        "failed_checks": [
            {
                "name": "row_count > 1000",
                "table": "user_events",
                "status": "FAILED",
                "actual_value": 850,
                "expected_value": "> 1000",
                "message": "Row count check failed",
                "ds_id": 1,
                "dbtype": "postgresql",
            },
            {
                "name": "freshness < 1 day",
                "table": "daily_reports",
                "status": "FAILED",
                "message": "Data is 2 days old",
                "ds_id": 2,
                "dbtype": "snowflake",
            },
        ],
        "passed_checks": [
            {
                "name": "no duplicates",
                "table": "users",
                "status": "PASSED",
                "ds_id": 1,
                "dbtype": "postgresql",
            }
        ],
        "recommendations": [
            "📊 Row count issue in user_events: Check data ingestion process",
            "🕒 Data freshness issue in daily_reports: Check ETL pipeline schedules",
            "🛑 PIPELINE ACTION: Consider failing pipeline due to data quality issues",
        ],
        "execution_metadata": {
            "sdk_version": "1.0.0",
            "datasources_count": 2,
            "metrics_count": 8,
            "total_duration_seconds": 15.3,
            "dry_run": False,
        },
    }

    print("Example of detailed results structure:")
    print(f"Exit Code: {mock_result['exit_code']}")
    print(f"Monitor ID: {mock_result['monitor_id']}")
    print(f"Total Checks: {mock_result['summary']['total_checks']}")
    print(f"Passed: {mock_result['summary']['passed']}")
    print(f"Failed: {mock_result['summary']['failed']}")
    print(f"Duration: {mock_result['execution_metadata']['duration_seconds']}s")

    print("\nFailed Checks:")
    for check in mock_result["failed_checks"]:
        print(f"  - {check['name']} on {check['table']}: {check['message']}")

    print("\nRecommendations:")
    for rec in mock_result["recommendations"]:
        print(f"  {rec}")


if __name__ == "__main__":
    # Set example environment variables if not set
    if not os.getenv("ALATION_HOST"):
        os.environ["ALATION_HOST"] = "https://your-alation.company.com"
    if not os.getenv("MONITOR_ID"):
        os.environ["MONITOR_ID"] = "123"
    if not os.getenv("DRY_RUN"):
        os.environ["DRY_RUN"] = "true"  # Use dry run for examples

    # Run all examples
    basic_example()
    health_check_example()
    error_handling_example()
    detailed_results_example()

    print("\n" + "=" * 50)
    print("Example completed!")
    print("To run with real data:")
    print("1. Set ALATION_HOST to your Alation instance URL")
    print("2. Set MONITOR_ID to a valid monitor ID")
    print("3. Set DRY_RUN=false to execute actual scans")
    print("4. Optionally set ALATION_API_TOKEN if authentication is required")

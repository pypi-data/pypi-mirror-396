#!/usr/bin/env python3
"""
Airflow DAG example for integrating Alation Data Quality SDK.

This example shows how to integrate the SDK into an Airflow data pipeline
with proper error handling, logging, and pipeline controls.
"""

import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor

# Default arguments for the DAG
default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["data-team@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    "data_quality_pipeline",
    default_args=default_args,
    description="Data Pipeline with Quality Checks",
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["data-quality", "etl"],
)


def run_data_quality_checks(**context):
    """
    Run Alation data quality checks and handle results appropriately.

    This function demonstrates:
    - Loading SDK configuration from Airflow Variables
    - Running quality checks
    - Handling different types of failures
    - Logging results for monitoring
    - Pushing results to XCom for downstream tasks
    """
    from data_quality_sdk import DataQualityRunner, SDKConfig
    from data_quality_sdk.utils.exceptions import DataQualitySDKError

    # Get configuration from Airflow Variables
    try:
        alation_host = Variable.get("ALATION_HOST")
        monitor_id = Variable.get("MONITOR_ID")
        api_token = Variable.get("ALATION_API_TOKEN", default_var=None)
    except KeyError as e:
        raise AirflowException(f"Missing Airflow Variable: {e}")

    # Create SDK configuration
    config = SDKConfig(
        alation_host=alation_host,
        monitor_id=monitor_id,
        api_token=api_token,
        timeout=60,  # Longer timeout for production
        log_level="INFO",
        dry_run=False,
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting data quality checks for monitor {monitor_id}")

    try:
        # Initialize and run checks
        runner = DataQualityRunner(config)
        result = runner.run_checks()

        # Log summary results
        summary = result["summary"]
        logger.info(
            f"Quality check results: {summary['total_checks']} total, "
            f"{summary['passed']} passed, {summary['failed']} failed, "
            f"{summary['warnings']} warnings"
        )

        # Push results to XCom for downstream tasks
        context["task_instance"].xcom_push(key="quality_check_result", value=result)

        # Handle different exit codes
        exit_code = result["exit_code"]

        if exit_code == 0:
            logger.info("✅ All data quality checks passed!")
            return result

        elif exit_code == 1:
            # Quality check failures - this is a data quality issue
            logger.error(f"❌ Data quality checks failed: {summary['failed']} checks failed")

            # Log failed checks for debugging
            for failed_check in result["failed_checks"]:
                logger.error(
                    f"Failed check: {failed_check['name']} on {failed_check.get('table', 'unknown table')}"
                )

            # Log recommendations
            for recommendation in result.get("recommendations", []):
                logger.warning(f"Recommendation: {recommendation}")

            # Decide whether to fail the pipeline based on the type of failures
            critical_failures = [
                check
                for check in result["failed_checks"]
                if "freshness" in check.get("name", "").lower()
                or "duplicate" in check.get("name", "").lower()
            ]

            if critical_failures:
                raise AirflowException(
                    f"Critical data quality issues detected. "
                    f"Pipeline execution stopped. Failed checks: {len(result['failed_checks'])}"
                )
            else:
                logger.warning("Non-critical quality issues detected, but continuing pipeline...")
                return result

        elif exit_code == 2:
            # Configuration or setup error
            logger.error("❌ Data quality check configuration error")
            for error in result.get("errors", []):
                logger.error(f"Configuration error: {error}")
            raise AirflowException(
                "Data quality configuration error - check Alation connectivity and permissions"
            )

        elif exit_code == 3:
            # Results upload failed - checks ran but couldn't report back
            logger.warning("⚠️ Quality checks completed but failed to upload results to Alation")
            # Don't fail the pipeline for upload issues if checks passed
            if summary["failed"] == 0:
                logger.info("Continuing pipeline since quality checks passed")
                return result
            else:
                raise AirflowException("Quality checks failed and results upload failed")

        elif exit_code == 4:
            # Network error
            logger.error("❌ Network connectivity error during quality checks")
            raise AirflowException("Network error - check connectivity to Alation")

        else:
            # Unexpected error
            logger.error(f"❌ Unexpected error during quality checks (exit code: {exit_code})")
            for error in result.get("errors", []):
                logger.error(f"Error: {error}")
            raise AirflowException(
                f"Unexpected error in data quality checks (exit code: {exit_code})"
            )

    except DataQualitySDKError as e:
        logger.error(f"❌ Data Quality SDK error: {str(e)}")
        raise AirflowException(f"Data Quality SDK error: {str(e)}")

    except Exception as e:
        logger.error(f"❌ Unexpected error in quality checks: {str(e)}")
        raise AirflowException(f"Unexpected error in quality checks: {str(e)}")


def check_quality_results(**context):
    """
    Check quality results from upstream task and make pipeline decisions.

    This demonstrates how to use quality check results in downstream tasks.
    """
    logger = logging.getLogger(__name__)

    # Get results from upstream task
    result = context["task_instance"].xcom_pull(
        task_ids="data_quality_checks", key="quality_check_result"
    )

    if not result:
        logger.warning("No quality check results found")
        return

    summary = result["summary"]
    logger.info(f"Retrieved quality results: {summary}")

    # Example: Skip certain downstream tasks if there are warnings
    if summary["warnings"] > 5:
        logger.warning("High number of warnings detected - consider manual review")
        # Could use Airflow's skip functionality here

    # Example: Add additional checks based on specific failed checks
    for failed_check in result.get("failed_checks", []):
        if "row_count" in failed_check.get("name", "").lower():
            logger.warning("Row count issues detected - downstream aggregations may be affected")

    return result


def send_quality_report(**context):
    """
    Send a quality report via email or Slack.

    This demonstrates how to create custom notifications based on quality results.
    """
    logger = logging.getLogger(__name__)

    result = context["task_instance"].xcom_pull(
        task_ids="data_quality_checks", key="quality_check_result"
    )

    if not result:
        return

    summary = result["summary"]
    monitor_id = result.get("monitor_id")

    # Create report
    report = f"""
    Data Quality Report - Monitor {monitor_id}

    Summary:
    - Total Checks: {summary['total_checks']}
    - Passed: {summary['passed']} ✅
    - Failed: {summary['failed']} ❌
    - Warnings: {summary['warnings']} ⚠️

    """

    if result.get("failed_checks"):
        report += "\nFailed Checks:\n"
        for check in result["failed_checks"][:5]:  # Show first 5
            report += f"- {check.get('name', 'Unknown')} on {check.get('table', 'unknown')}\n"

    if result.get("recommendations"):
        report += "\nRecommendations:\n"
        for rec in result["recommendations"][:3]:  # Show first 3
            report += f"- {rec}\n"

    logger.info(f"Quality Report:\n{report}")

    # Here you would send the report via email, Slack, etc.
    # Example: send_slack_message(report)
    # Example: send_email(report)

    return report


# Define tasks

# Start of pipeline
start_task = DummyOperator(
    task_id="start_pipeline",
    dag=dag,
)

# Data extraction task
extract_data = BashOperator(
    task_id="extract_data",
    bash_command="""
    echo "Extracting data from source systems..."
    # Your data extraction logic here
    # e.g., python extract_data.py
    echo "Data extraction completed"
    """,
    dag=dag,
)

# Data transformation task
transform_data = BashOperator(
    task_id="transform_data",
    bash_command="""
    echo "Transforming data..."
    # Your data transformation logic here
    # e.g., dbt run --models staging
    echo "Data transformation completed"
    """,
    dag=dag,
)

# Data quality checks (the main SDK integration)
quality_checks = PythonOperator(
    task_id="data_quality_checks",
    python_callable=run_data_quality_checks,
    dag=dag,
)

# Check quality results and make decisions
quality_decision = PythonOperator(
    task_id="quality_decision",
    python_callable=check_quality_results,
    dag=dag,
)

# Data loading (only runs if quality checks pass)
load_data = BashOperator(
    task_id="load_data",
    bash_command="""
    echo "Loading data to target systems..."
    # Your data loading logic here
    # e.g., python load_data.py
    echo "Data loading completed"
    """,
    dag=dag,
)

# Send quality report
send_report = PythonOperator(
    task_id="send_quality_report",
    python_callable=send_quality_report,
    trigger_rule="none_failed",  # Run even if upstream tasks have warnings
    dag=dag,
)

# End of pipeline
end_task = DummyOperator(
    task_id="end_pipeline",
    trigger_rule="none_failed_or_skipped",
    dag=dag,
)

# Define task dependencies
start_task >> extract_data >> transform_data >> quality_checks
quality_checks >> quality_decision >> load_data >> end_task
quality_checks >> send_report >> end_task


# Alternative DAG structure with parallel quality checks
# You might want to run quality checks on different datasets in parallel


def create_quality_check_task(dataset_name: str, monitor_id: str):
    """Factory function to create quality check tasks for different datasets."""

    def run_dataset_quality_checks(**context):
        from data_quality_sdk import DataQualityRunner, SDKConfig

        config = SDKConfig(
            alation_host=Variable.get("ALATION_HOST"),
            monitor_id=monitor_id,
            api_token=Variable.get("ALATION_API_TOKEN", default_var=None),
            timeout=60,
            log_level="INFO",
        )

        runner = DataQualityRunner(config)
        result = runner.run_checks()

        # Store results with dataset-specific key
        context["task_instance"].xcom_push(key=f"quality_result_{dataset_name}", value=result)

        if result["exit_code"] != 0:
            raise AirflowException(f"Quality checks failed for {dataset_name}")

        return result

    return PythonOperator(
        task_id=f"quality_checks_{dataset_name}",
        python_callable=run_dataset_quality_checks,
        dag=dag,
    )


# Example: Create separate quality check tasks for different datasets
# users_quality = create_quality_check_task('users', '123')
# orders_quality = create_quality_check_task('orders', '124')
# products_quality = create_quality_check_task('products', '125')

# Parallel quality checks structure:
# transform_data >> [users_quality, orders_quality, products_quality] >> load_data

"""Shared test fixtures for the Data Quality SDK tests."""

from unittest.mock import Mock, patch

import pytest

from data_quality_sdk.config import SDKConfig


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    return SDKConfig(
        alation_host="https://test.alation.com",
        monitor_id="123",
        api_token="test_token",
        tenant_id="test_tenant",
        job_id="test_job",
        request_id="test_request",
        timeout=30,
        log_level="INFO",
        dry_run=False,
    )


@pytest.fixture
def dry_run_config():
    """Create a dry run configuration for testing."""
    return SDKConfig(
        alation_host="https://test.alation.com",
        monitor_id="123",
        api_token="test_token",
        tenant_id="test_tenant",
        dry_run=True,
    )


@pytest.fixture
def mock_check_data():
    """Create mock check data structure."""
    mock_data = Mock()
    mock_data.ds_id = 1
    mock_data.dbtype = "postgres"
    mock_data.checks = [
        {"name": "row_count_check", "table": "users", "column": None, "check_type": "row_count"},
        {
            "name": "null_count_check",
            "table": "users",
            "column": "email",
            "check_type": "missing_count",
        },
    ]
    return mock_data


@pytest.fixture
def mock_soda_scan_result():
    """Create mock Soda scan result."""
    return {
        "ds_id": 1,
        "dbtype": "postgres",
        "durationSeconds": 15,
        "checks": [
            {
                "name": "row_count_check",
                "table": "users",
                "column": None,
                "outcome": "pass",
                "actualValue": 1000,
                "expectedValue": "> 0",
                "description": "Check passed successfully",
                "type": "row_count",
                "location": {"file": "checks.yml", "line": 10},
            },
            {
                "name": "null_count_check",
                "table": "users",
                "column": "email",
                "outcome": "fail",
                "actualValue": 50,
                "expectedValue": "= 0",
                "description": "Found 50 null values in email column",
                "type": "missing_count",
                "location": {"file": "checks.yml", "line": 15},
            },
        ],
    }


@pytest.fixture
def mock_ocf_config():
    """Create mock OCF configuration."""
    return {
        "connection": {
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "username": "test_user",
            "password": "test_pass",
            "database": "test_db",
            "schema": "public",
        }
    }


@pytest.fixture
def mock_metric_dict():
    """Create mock metric metadata dictionary."""
    return {
        "metric_1": {
            "name": "row_count_metric",
            "table": "users",
            "unique_identifier": "metric_1_unique_id",
        },
        "metric_2": {
            "name": "null_count_metric",
            "table": "users",
            "column": "email",
            "unique_identifier": "metric_2_unique_id",
        },
    }


@pytest.fixture
def mock_alation_responses():
    """Create mock responses for Alation API calls."""
    return {
        "get_all_checks_data": [Mock(ds_id=1, dbtype="postgres", checks=[])],
        "get_all_metric_data": {"metric1": {"name": "test_metric"}},
        "get_ocf_configuration": {"connection": {"host": "localhost"}},
        "health_check": True,
    }


@pytest.fixture
def mock_failed_queries():
    """Create mock failed row queries."""
    return [
        {
            "metric_unique_identifier": "metric_1_unique_id",
            "ds_id": 1,
            "query": "SELECT * FROM users WHERE id IS NULL;",
        },
        {
            "metric_unique_identifier": "metric_2_unique_id",
            "ds_id": 1,
            "query": "SELECT * FROM users WHERE email IS NULL;",
        },
    ]

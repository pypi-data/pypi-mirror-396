"""Tests for the main DataQualityRunner class."""

from unittest.mock import Mock, patch

import pytest

from data_quality_sdk.config import SDKConfig
from data_quality_sdk.main import DataQualityRunner


class TestDataQualityRunner:
    """Test cases for DataQualityRunner class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        return SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            api_token="test_token",
            tenant_id="test_tenant",
            dry_run=False,
        )

    @pytest.fixture
    def mock_alation_client(self):
        """Create a mock Alation client."""
        client = Mock()
        client.get_all_metric_data.return_value = {"metric1": {"name": "test_metric"}}
        client.get_all_checks_data.return_value = [
            Mock(ds_id=1, dbtype="postgres", checks=[{"name": "test_check"}])
        ]
        client.get_ocf_configuration.return_value = {"connection": {"host": "localhost"}}
        return client

    @pytest.fixture
    def mock_soda_runner(self):
        """Create a mock Soda runner."""
        runner = Mock()
        runner.execute_ds_scan.return_value = {
            "ds_id": 1,
            "dbtype": "postgres",
            "checks": [
                {
                    "name": "test_check",
                    "table": "test_table",
                    "outcome": "pass",
                    "actualValue": 100,
                    "expectedValue": ">= 0",
                }
            ],
        }
        return runner

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_init_with_config(
        self, mock_logging, mock_soda_runner_class, mock_client_class, mock_config
    ):
        """Test DataQualityRunner initialization with provided config."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock the validate method since we're using a real config object
        with patch.object(mock_config, "validate") as mock_validate:
            runner = DataQualityRunner(config=mock_config)

            assert runner.config == mock_config
            mock_validate.assert_called_once()
            mock_logging.assert_called_once_with(mock_config.log_level)

    @patch("data_quality_sdk.main.SDKConfig.from_env")
    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_init_without_config(
        self, mock_logging, mock_soda_runner_class, mock_client_class, mock_from_env, mock_config
    ):
        """Test DataQualityRunner initialization without provided config."""
        mock_from_env.return_value = mock_config
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        runner = DataQualityRunner()

        assert runner.config == mock_config
        mock_from_env.assert_called_once()

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_run_checks_dry_run(
        self, mock_logging, mock_soda_runner_class, mock_client_class, mock_config
    ):
        """Test run_checks in dry run mode."""
        mock_config.dry_run = True
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock the clients
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = {}
        mock_client.get_all_checks_data.return_value = [Mock(ds_id=1, dbtype="postgres", checks=[])]
        mock_client_class.return_value = mock_client

        runner = DataQualityRunner(config=mock_config)
        result = runner.run_checks()

        assert result["exit_code"] == 0
        assert result["upload_status"] == "skipped_dry_run"
        assert len(result["all_scan_results"]) == 1
        assert result["all_scan_results"][0]["dry_run"] is True

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_run_checks_no_checks_found(
        self, mock_logging, mock_soda_runner_class, mock_client_class, mock_config
    ):
        """Test run_checks when no checks are found."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock the clients
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = {}
        mock_client.get_all_checks_data.return_value = []
        mock_client_class.return_value = mock_client

        runner = DataQualityRunner(config=mock_config)
        result = runner.run_checks()

        assert result["exit_code"] == 2
        assert "No checks found for monitor" in result["errors"]

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_run_checks_successful_execution(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        mock_config,
        mock_alation_client,
        mock_soda_runner,
    ):
        """Test successful run_checks execution."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        mock_client_class.return_value = mock_alation_client
        mock_soda_runner_class.return_value = mock_soda_runner

        runner = DataQualityRunner(config=mock_config)
        result = runner.run_checks()

        assert result["exit_code"] == 0
        assert result["summary"]["total_checks"] == 1
        assert result["summary"]["passed"] == 1
        assert result["summary"]["failed"] == 0

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_health_check(
        self, mock_logging, mock_soda_runner_class, mock_client_class, mock_config
    ):
        """Test health check functionality."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock the clients
        mock_client = Mock()
        mock_client.health_check.return_value = True
        mock_client_class.return_value = mock_client

        runner = DataQualityRunner(config=mock_config)
        health = runner.health_check()

        assert health["status"] == "healthy"
        assert health["checks"]["alation_connectivity"] == "ok"
        assert health["checks"]["soda_core"] == "ok"
        assert health["checks"]["configuration"] == "ok"

    def test_merge_scan_results_passed_check(self):
        """Test merging scan results with passed checks."""
        config = SDKConfig(alation_host="https://test.alation.com", monitor_id="123")

        with patch("data_quality_sdk.main.AlationClient"), patch(
            "data_quality_sdk.main.SodaRunner"
        ), patch("data_quality_sdk.main.setup_logging"):
            runner = DataQualityRunner(config=config)

            detailed_result = {
                "summary": {
                    "total_checks": 0,
                    "passed": 0,
                    "failed": 0,
                    "warnings": 0,
                    "errors": 0,
                },
                "passed_checks": [],
                "failed_checks": [],
                "warning_checks": [],
                "execution_metadata": {},
            }

            scan_result = {
                "ds_id": 1,
                "dbtype": "postgres",
                "checks": [
                    {
                        "name": "test_check",
                        "table": "test_table",
                        "outcome": "pass",
                        "actualValue": 100,
                    }
                ],
            }

            runner._merge_scan_results(detailed_result, scan_result)

            assert detailed_result["summary"]["total_checks"] == 1
            assert detailed_result["summary"]["passed"] == 1
            assert len(detailed_result["passed_checks"]) == 1

    def test_merge_scan_results_failed_check(self):
        """Test merging scan results with failed checks."""
        config = SDKConfig(alation_host="https://test.alation.com", monitor_id="123")

        with patch("data_quality_sdk.main.AlationClient"), patch(
            "data_quality_sdk.main.SodaRunner"
        ), patch("data_quality_sdk.main.setup_logging"):
            runner = DataQualityRunner(config=config)

            detailed_result = {
                "summary": {
                    "total_checks": 0,
                    "passed": 0,
                    "failed": 0,
                    "warnings": 0,
                    "errors": 0,
                },
                "passed_checks": [],
                "failed_checks": [],
                "warning_checks": [],
                "execution_metadata": {},
            }

            scan_result = {
                "ds_id": 1,
                "dbtype": "postgres",
                "checks": [
                    {
                        "name": "row_count_check",
                        "table": "test_table",
                        "outcome": "fail",
                        "actualValue": 0,
                        "expectedValue": "> 0",
                    }
                ],
            }

            runner._merge_scan_results(detailed_result, scan_result)

            assert detailed_result["summary"]["total_checks"] == 1
            assert detailed_result["summary"]["failed"] == 1
            assert len(detailed_result["failed_checks"]) == 1

    def test_determine_check_severity(self):
        """Test check severity determination."""
        config = SDKConfig(alation_host="https://test.alation.com", monitor_id="123")

        with patch("data_quality_sdk.main.AlationClient"), patch(
            "data_quality_sdk.main.SodaRunner"
        ), patch("data_quality_sdk.main.setup_logging"):
            runner = DataQualityRunner(config=config)

            # Test critical checks
            assert runner._determine_check_severity({"name": "freshness_check"}) == "CRITICAL"
            assert runner._determine_check_severity({"name": "duplicate_check"}) == "CRITICAL"

            # Test high priority checks
            assert runner._determine_check_severity({"name": "row_count_check"}) == "HIGH"
            assert runner._determine_check_severity({"name": "schema_check"}) == "HIGH"

            # Test medium priority checks
            assert runner._determine_check_severity({"name": "custom_check"}) == "MEDIUM"

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        config = SDKConfig(alation_host="https://test.alation.com", monitor_id="123")

        with patch("data_quality_sdk.main.AlationClient"), patch(
            "data_quality_sdk.main.SodaRunner"
        ), patch("data_quality_sdk.main.setup_logging"):
            runner = DataQualityRunner(config=config)

            detailed_result = {"recommendations": [], "summary": {"failed": 0}, "failed_checks": []}

            # Test no failures
            runner._generate_recommendations(detailed_result)
            assert any(
                "✅ PIPELINE ACTION: All quality checks passed" in rec
                for rec in detailed_result["recommendations"]
            )

            # Test with failures
            detailed_result["summary"]["failed"] = 2
            detailed_result["failed_checks"] = [
                {"name": "freshness_check", "table": "users"},
                {"name": "duplicate_check", "table": "orders"},
            ]
            detailed_result["recommendations"] = []

            runner._generate_recommendations(detailed_result)

            recommendations = detailed_result["recommendations"]
            assert any("freshness issue" in rec for rec in recommendations)
            assert any("Duplicate data detected" in rec for rec in recommendations)
            assert any(
                "🛑 PIPELINE ACTION: Consider failing pipeline" in rec for rec in recommendations
            )

"""Integration tests for the Data Quality SDK."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from data_quality_sdk.config import SDKConfig
from data_quality_sdk.main import DataQualityRunner


@pytest.mark.integration
class TestDataQualityRunnerIntegration:
    """Integration tests for the complete DataQualityRunner workflow."""

    @pytest.fixture
    def integration_config(self):
        """Create configuration for integration testing."""
        return SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            api_token="test_token",
            tenant_id="test_tenant",
            job_id="integration_test_job",
            request_id="integration_test_request",
        )

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_complete_successful_workflow(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        integration_config,
        mock_check_data,
        mock_soda_scan_result,
        mock_ocf_config,
        mock_metric_dict,
    ):
        """Test complete successful workflow from start to finish."""
        # Setup mocks
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock Alation client
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = mock_metric_dict
        mock_client.get_all_checks_data.return_value = [mock_check_data]
        mock_client.get_ocf_configuration.return_value = mock_ocf_config
        mock_client.send_result_for_scan.return_value = None
        mock_client.save_sample_failed_check_queries.return_value = None
        mock_client_class.return_value = mock_client

        # Mock Soda runner
        mock_soda = Mock()
        mock_soda.execute_ds_scan.return_value = mock_soda_scan_result
        mock_soda.extract_sample_failed_queries.return_value = []
        mock_soda_runner_class.return_value = mock_soda

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        result = runner.run_checks()

        # Verify the complete workflow
        assert result["exit_code"] == 1  # Exit code 1 because we have a failed check
        assert result["summary"]["total_checks"] == 2
        assert result["summary"]["passed"] == 1
        assert result["summary"]["failed"] == 1
        assert result["summary"]["datasources_processed"] == 1

        # Verify API calls were made
        mock_client.get_all_metric_data.assert_called_once_with("123")
        mock_client.get_all_checks_data.assert_called_once()
        mock_client.get_ocf_configuration.assert_called_once_with(1)
        mock_client.send_result_for_scan.assert_called_once()

        # Verify Soda scan was executed
        mock_soda.execute_ds_scan.assert_called_once()

        # Verify recommendations were generated
        assert len(result["recommendations"]) > 0

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_workflow_with_api_failure(
        self, mock_logging, mock_soda_runner_class, mock_client_class, integration_config
    ):
        """Test workflow when API calls fail."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock Alation client with API failure
        mock_client = Mock()
        mock_client.get_all_metric_data.side_effect = Exception("API Error")
        mock_client.get_all_checks_data.return_value = []
        mock_client_class.return_value = mock_client

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        result = runner.run_checks()

        # Verify error handling
        assert result["exit_code"] == 2  # No checks found
        assert "No checks found for monitor" in result["errors"]

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_workflow_with_soda_scan_failure(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        integration_config,
        mock_check_data,
        mock_ocf_config,
        mock_metric_dict,
    ):
        """Test workflow when Soda scan fails."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock Alation client
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = mock_metric_dict
        mock_client.get_all_checks_data.return_value = [mock_check_data]
        mock_client.get_ocf_configuration.return_value = mock_ocf_config
        mock_client_class.return_value = mock_client

        # Mock Soda runner with failure
        mock_soda = Mock()
        mock_soda.execute_ds_scan.side_effect = Exception("Soda scan failed")
        mock_soda_runner_class.return_value = mock_soda

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        result = runner.run_checks()

        # Verify error handling
        assert result["exit_code"] == 1  # Scan execution failed
        assert any("Scan failed for datasource 1" in error for error in result["errors"])

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_dry_run_workflow(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        mock_check_data,
        mock_metric_dict,
    ):
        """Test dry run workflow."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Create dry run config
        dry_run_config = SDKConfig(
            alation_host="https://test.alation.com", monitor_id="123", dry_run=True
        )

        # Mock Alation client
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = mock_metric_dict
        mock_client.get_all_checks_data.return_value = [mock_check_data]
        mock_client_class.return_value = mock_client

        # Mock Soda runner (should not be called in dry run)
        mock_soda = Mock()
        mock_soda_runner_class.return_value = mock_soda

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=dry_run_config)
        result = runner.run_checks()

        # Verify dry run behavior
        assert result["exit_code"] == 0
        assert result["upload_status"] == "skipped_dry_run"
        assert len(result["all_scan_results"]) == 1
        assert result["all_scan_results"][0]["dry_run"] is True

        # Verify Soda scan was not executed
        mock_soda.execute_ds_scan.assert_not_called()

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_health_check_integration(
        self, mock_logging, mock_soda_runner_class, mock_client_class, integration_config
    ):
        """Test health check integration."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock Alation client
        mock_client = Mock()
        mock_client.health_check.return_value = True
        mock_client_class.return_value = mock_client

        # Create DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        health = runner.health_check()

        # Verify health check
        assert health["status"] == "healthy"
        assert health["checks"]["alation_connectivity"] == "ok"
        assert health["checks"]["soda_core"] == "ok"
        assert health["checks"]["configuration"] == "ok"

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_multiple_datasources_workflow(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        integration_config,
        mock_ocf_config,
        mock_metric_dict,
    ):
        """Test workflow with multiple datasources."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Create multiple check data objects
        check_data_1 = Mock()
        check_data_1.ds_id = 1
        check_data_1.dbtype = "postgres"
        check_data_1.checks = [{"name": "check_1"}]

        check_data_2 = Mock()
        check_data_2.ds_id = 2
        check_data_2.dbtype = "mysql"
        check_data_2.checks = [{"name": "check_2"}]

        # Mock Alation client
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = mock_metric_dict
        mock_client.get_all_checks_data.return_value = [check_data_1, check_data_2]
        mock_client.get_ocf_configuration.return_value = mock_ocf_config
        mock_client.send_result_for_scan.return_value = None
        mock_client_class.return_value = mock_client

        # Mock Soda runner
        mock_soda = Mock()
        mock_soda.execute_ds_scan.return_value = {
            "ds_id": 1,
            "checks": [{"name": "test", "outcome": "pass"}],
        }
        mock_soda.extract_sample_failed_queries.return_value = []
        mock_soda_runner_class.return_value = mock_soda

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        result = runner.run_checks()

        # Verify multiple datasources were processed
        assert result["summary"]["datasources_processed"] == 2
        assert len(result["all_scan_results"]) == 2

        # Verify API calls for both datasources
        assert mock_client.get_ocf_configuration.call_count == 2
        assert mock_client.send_result_for_scan.call_count == 2
        assert mock_soda.execute_ds_scan.call_count == 2

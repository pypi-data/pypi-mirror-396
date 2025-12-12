"""Alation Data Quality SDK

A production-ready SDK for running Alation data quality checks using Soda Core.
Designed for integration with data pipelines like Airflow.

Usage:
    from data_quality_sdk import DataQualityRunner

    runner = DataQualityRunner()
    result = runner.run_checks()
"""

__version__ = "1.0.0"

from .config import SDKConfig
from .main import DataQualityRunner

__all__ = ["DataQualityRunner", "SDKConfig"]

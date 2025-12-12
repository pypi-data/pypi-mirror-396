# Alation Data Quality SDK

A production-ready SDK for executing Alation data quality checks using Soda Core. This SDK is designed to be integrated into data pipelines (like Airflow) with minimal configuration.

## Features

- **Simple Configuration**: Only 2 environment variables required
- **Production Ready**: Comprehensive error handling, logging, and retry logic
- **Pipeline Friendly**: Designed for CI/CD and Airflow integration
- **Automatic Setup**: Fetches datasource credentials and check definitions automatically
- **Comprehensive Results**: Detailed scan results with actionable recommendations
- **Multiple Datasources**: Supports PostgreSQL, MySQL, BigQuery, Snowflake, and more

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

Set these two required environment variables:

```bash
export ALATION_HOST="https://your-alation-instance.company.com"
export MONITOR_ID="123"
```

Optional environment variables:

```bash
export ALATION_API_TOKEN="your-api-token"  # If authentication is required
export TENANT_ID="your-tenant-id"          # For multi-tenant setups (required for results upload)
export JOB_ID="your-job-id"                # Job identifier (default: 'sdk_job')
export REQUEST_ID="your-request-id"        # Request identifier (default: 'sdk_request')
export JOB_TYPE="DATA_QUALITY_AIRFLOW"     # Job type (default: 'DATA_QUALITY_AIRFLOW')
export ALATION_TIMEOUT="30"                # Request timeout in seconds
export LOG_LEVEL="INFO"                     # Logging level
export DRY_RUN="false"                      # Set to 'true' to skip actual execution
export IS_TEST_RUN="false"                  # Set to 'true' for test runs
export IS_ANOMALY_RUN="false"               # Set to 'true' for anomaly detection runs
```

### Basic Usage

#### Python API

```python
from data_quality_sdk import DataQualityRunner

# Initialize and run checks
runner = DataQualityRunner()
result = runner.run_checks()

# Check results
if result['exit_code'] == 0:
    print("✅ All quality checks passed!")
else:
    print(f"❌ Quality checks failed: {result['summary']}")
    for recommendation in result['recommendations']:
        print(f"  - {recommendation}")
```

#### Command Line Interface

```bash
# Run quality checks
alation-dq

# Perform health check
alation-dq --health-check

# Dry run (don't execute scans)
alation-dq --dry-run

# Return only exit code (for pipelines)
alation-dq --exit-code-only
```

## Integration Examples

### Airflow Integration

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

def run_data_quality_checks(**context):
    from data_quality_sdk import DataQualityRunner

    runner = DataQualityRunner()
    result = runner.run_checks()

    if result['exit_code'] != 0:
        raise Exception(f"Data quality checks failed: {result['summary']}")

    return result

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_quality_pipeline',
    default_args=default_args,
    description='Data Quality Pipeline',
    schedule_interval='@daily',
    catchup=False,
)

# Your ETL tasks here
extract_task = BashOperator(
    task_id='extract_data',
    bash_command='your-extract-script.sh',
    dag=dag,
)

transform_task = BashOperator(
    task_id='transform_data',
    bash_command='your-transform-script.sh',
    dag=dag,
)

# Data quality checks
quality_check_task = PythonOperator(
    task_id='data_quality_checks',
    python_callable=run_data_quality_checks,
    env_vars={
        'ALATION_HOST': '{{ var.value.ALATION_HOST }}',
        'MONITOR_ID': '{{ var.value.MONITOR_ID }}',
        'ALATION_API_TOKEN': '{{ var.value.ALATION_API_TOKEN }}',
    },
    dag=dag,
)

# Load task (only runs if quality checks pass)
load_task = BashOperator(
    task_id='load_data',
    bash_command='your-load-script.sh',
    dag=dag,
)

# Set dependencies
extract_task >> transform_task >> quality_check_task >> load_task
```

### CI/CD Integration

```yaml
# .github/workflows/data-quality.yml
name: Data Quality Checks

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  workflow_dispatch:

jobs:
  quality-checks:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run data quality checks
      env:
        ALATION_HOST: ${{ secrets.ALATION_HOST }}
        MONITOR_ID: ${{ secrets.MONITOR_ID }}
        ALATION_API_TOKEN: ${{ secrets.ALATION_API_TOKEN }}
      run: |
        alation-dq --exit-code-only
```

### Docker Usage

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY data_quality_sdk/ ./data_quality_sdk/
COPY setup.py .
RUN pip install -e .

# Set environment variables (or pass them at runtime)
ENV ALATION_HOST=""
ENV MONITOR_ID=""

CMD ["alation-dq"]
```

## How It Works

1. **Fetch Checks**: Uses the Monitor ID to fetch check definitions and datasource information from Alation
2. **Get Credentials**: Retrieves datasource connection credentials via the Alation metadata API
3. **Generate Config**: Converts the protobuf configuration to Soda Core YAML format
4. **Execute Scan**: Runs Soda Core scan with the generated configuration and check definitions
5. **Report Results**: Sends scan results back to Alation and provides detailed local results

## Supported Datasources

- PostgreSQL
- MySQL
- BigQuery
- Snowflake
- Amazon Redshift
- Oracle
- SQL Server
- Databricks
- Apache Spark
- Amazon Athena
- Trino/Presto

## Configuration

### SDK Configuration Class

```python
from data_quality_sdk import SDKConfig

# Load from environment
config = SDKConfig.from_env()

# Or create manually
config = SDKConfig(
    alation_host="https://my-alation.company.com",
    monitor_id="123",
    api_token="optional-token",
    timeout=30,
    log_level="INFO",
    dry_run=False
)

runner = DataQualityRunner(config)
```

### Health Check

Before running in production, verify your setup:

```python
runner = DataQualityRunner()
health = runner.health_check()

print(f"Status: {health['status']}")
for check, result in health['checks'].items():
    print(f"  {check}: {result}")
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

- `AlationAPIError`: Issues with Alation API calls
- `DatasourceConfigError`: Problems with datasource configuration
- `SodaScanError`: Soda Core execution failures
- `UnsupportedDatasourceError`: Unsupported datasource types
- `NetworkError`: Network connectivity issues

## Exit Codes

- `0`: Success - all checks passed
- `1`: Quality checks failed (data quality issues)
- `2`: Configuration or setup error
- `3`: Results upload failed
- `4`: Network connectivity error
- `5`: Unexpected error

## Logging

The SDK provides structured logging with configurable levels:

```python
# Set log level via environment variable
export LOG_LEVEL="DEBUG"

# Or programmatically
from data_quality_sdk.utils.logging import setup_logging
logger = setup_logging("DEBUG")
```

## Development

### Setup Development Environment

1. **Clone the repository:**
```bash
git clone https://github.com/alation/data-quality-sdk.git
cd data-quality-sdk
```

2. **Install in development mode:**
```bash
pip install -e ".[dev]"
```

3. **Set up pre-commit hooks:**
```bash
pre-commit install
```

This will automatically run code formatting, linting, and type checking on every commit.

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=data_quality_sdk --cov-report=html

# Run specific test file
pytest tests/test_config.py -v
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **flake8**: Linting and style checks
- **mypy**: Type checking
- **bandit**: Security checks

```bash
# Manual code formatting (pre-commit handles this automatically)
black data_quality_sdk/ tests/
isort data_quality_sdk/ tests/

# Linting
flake8 data_quality_sdk/

# Type checking
mypy data_quality_sdk/

# Security check
bandit -r data_quality_sdk/

# Run all pre-commit hooks manually
pre-commit run --all-files
```

### Pre-commit Hooks

The following hooks run automatically on every commit:

- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with a newline
- **check-yaml/toml/json**: Validate file formats
- **black**: Format Python code
- **isort**: Sort imports
- **flake8**: Lint code
- **mypy**: Type checking
- **bandit**: Security scanning

To skip pre-commit hooks (not recommended):
```bash
git commit --no-verify -m "message"
```

## Troubleshooting

### Common Issues

1. **"QueryService client not available"**
   - Install the queryservice_client package
   - Ensure protobuf dependencies are installed

2. **"Soda Core not available"**
   - Install Soda Core: `pip install soda-core==3.4.4+105 --index-url https://artifactory.alationdevops.com/artifactory/api/pypi/pypi/simple`

3. **"Unsupported datasource type"**
   - Check if your datasource type is in the supported list
   - Contact support to add support for new types

4. **Connection errors**
   - Verify ALATION_HOST is correct and accessible
   - Check API token permissions if using authentication
   - Ensure monitor ID exists and is accessible

### Debug Mode

Enable debug logging to get detailed information:

```bash
export LOG_LEVEL="DEBUG"
alation-dq
```

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Enable debug logging to get detailed error information
3. Review the error messages and recommendations in the output
4. Contact your Alation administrator for API access issues

## License

Apache License 2.0

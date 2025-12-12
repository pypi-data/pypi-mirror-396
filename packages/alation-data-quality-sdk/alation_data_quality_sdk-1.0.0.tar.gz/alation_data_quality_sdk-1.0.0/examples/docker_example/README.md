# Docker Example for Alation Data Quality SDK

This directory contains Docker examples for containerizing and running the Alation Data Quality SDK.

## Quick Start

### 1. Build and Run with Docker

```bash
# Build the Docker image
docker build -f Dockerfile -t alation-dq-sdk ../..

# Run with environment variables
docker run --rm \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    -e DRY_RUN="true" \
    alation-dq-sdk
```

### 2. Using Docker Compose

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
vim .env

# Run with docker-compose
docker-compose up data-quality-oneshot

# For health check only
docker-compose --profile health up data-quality-health

# For production with persistence
docker-compose --profile production up data-quality-with-config
```

## Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# Required
ALATION_HOST=https://your-alation.company.com
MONITOR_ID=123

# Optional
ALATION_API_TOKEN=your-api-token
TENANT_ID=your-tenant-id
JOB_ID=docker_job
REQUEST_ID=docker_request
LOG_LEVEL=INFO
DRY_RUN=false
IS_TEST_RUN=false
IS_ANOMALY_RUN=false
```

### Docker Environment Variables

The following environment variables are supported in the Docker container:

| Variable | Default | Description |
|----------|---------|-------------|
| `ALATION_HOST` | *required* | Your Alation instance URL |
| `MONITOR_ID` | *required* | Monitor ID to execute |
| `ALATION_API_TOKEN` | `null` | API token (if required) |
| `TENANT_ID` | `null` | Tenant ID (for multi-tenant setups) |
| `JOB_ID` | `docker_job` | Job identifier |
| `REQUEST_ID` | `docker_request` | Request identifier |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DRY_RUN` | `false` | Skip actual execution |
| `IS_TEST_RUN` | `false` | Test run mode |
| `IS_ANOMALY_RUN` | `false` | Anomaly detection mode |

## Usage Examples

### One-Time Execution

```bash
# Run checks once and exit
docker run --rm \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    -e ALATION_API_TOKEN="your-token" \
    alation-dq-sdk alation-dq --exit-code-only
```

### Scheduled Execution

```bash
# Run checks every hour
docker run -d \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    -e ALATION_API_TOKEN="your-token" \
    --name alation-dq-scheduler \
    alation-dq-sdk sh -c "
        while true; do
            echo 'Running scheduled quality checks...'
            alation-dq --exit-code-only
            echo 'Sleeping for 1 hour...'
            sleep 3600
        done
    "
```

### Health Check

```bash
# Check SDK health
docker run --rm \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    alation-dq-sdk health-check
```

### Interactive Shell

```bash
# Get shell access for debugging
docker run -it --rm \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    alation-dq-sdk bash
```

## Kubernetes Deployment

### Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: alation-dq-job
spec:
  template:
    spec:
      containers:
      - name: alation-dq
        image: alation-dq-sdk:latest
        env:
        - name: ALATION_HOST
          value: "https://your-alation.company.com"
        - name: MONITOR_ID
          value: "123"
        - name: ALATION_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: alation-secrets
              key: api-token
        command: ["alation-dq", "--exit-code-only"]
      restartPolicy: OnFailure
  backoffLimit: 3
```

### CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: alation-dq-cronjob
spec:
  schedule: "0 6 * * *"  # Daily at 6 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: alation-dq
            image: alation-dq-sdk:latest
            env:
            - name: ALATION_HOST
              value: "https://your-alation.company.com"
            - name: MONITOR_ID
              value: "123"
            - name: ALATION_API_TOKEN
              valueFrom:
                secretKeyRef:
                  name: alation-secrets
                  key: api-token
            command: ["alation-dq", "--exit-code-only"]
          restartPolicy: OnFailure
```

## Monitoring and Logging

### Log Collection

```bash
# Run with log volume
docker run -d \
    -v $(pwd)/logs:/home/app/logs \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    -e LOG_LEVEL="DEBUG" \
    alation-dq-sdk
```

### Health Monitoring

The Docker image includes a health check that runs every 30 seconds:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD alation-dq --health-check || exit 1
```

Check container health:

```bash
docker ps  # Shows health status
docker inspect <container_id>  # Detailed health info
```

## Production Considerations

### Resource Limits

```bash
# Run with resource limits
docker run --rm \
    --memory=1g \
    --cpus=1.0 \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    alation-dq-sdk
```

### Security

```bash
# Use secrets for API tokens
echo "your-api-token" | docker secret create alation-api-token -

# Run with secret
docker run --rm \
    --secret alation-api-token \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    -e ALATION_API_TOKEN_FILE="/run/secrets/alation-api-token" \
    alation-dq-sdk
```

### Multi-Stage Builds

The Dockerfile uses multi-stage builds to minimize the final image size:

- **Builder stage**: Installs build dependencies and SDK
- **Production stage**: Only includes runtime dependencies and SDK

### Non-Root User

The container runs as a non-root user (`app`) for security:

- User ID: 1000
- Home directory: `/home/app`
- Working directory: `/home/app`

## Troubleshooting

### Common Issues

1. **Permission denied errors**
   - Ensure you're not running as root
   - Check file permissions in mounted volumes

2. **Network connectivity issues**
   - Verify Docker network configuration
   - Check firewall settings
   - Ensure ALATION_HOST is accessible from container

3. **Configuration errors**
   - Validate environment variables
   - Run health check command
   - Check container logs

### Debugging

```bash
# View container logs
docker logs <container_id>

# Run with debug logging
docker run --rm \
    -e LOG_LEVEL="DEBUG" \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    alation-dq-sdk

# Interactive debugging
docker run -it --rm \
    -e ALATION_HOST="https://your-alation.company.com" \
    -e MONITOR_ID="123" \
    alation-dq-sdk bash
```

## Performance Tuning

### Memory Usage

- Typical memory usage: 100-500MB
- For large datasets: 1-2GB recommended
- Monitor with: `docker stats`

### CPU Usage

- Usually single-threaded execution
- 1 CPU core typically sufficient
- Scale horizontally for multiple monitors

### Network

- Optimize for concurrent connections to Alation
- Consider network latency to Alation instance
- Use connection pooling if available

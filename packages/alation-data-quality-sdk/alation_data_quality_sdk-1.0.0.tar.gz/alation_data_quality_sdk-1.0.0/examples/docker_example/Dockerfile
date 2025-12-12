# Multi-stage Dockerfile for Alation Data Quality SDK
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and use a non-root user
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Copy the SDK source code
COPY --chown=app:app data_quality_sdk/ ./data_quality_sdk/
COPY --chown=app:app pyproject.toml setup.py ./

# Install the SDK in development mode
RUN pip install --user -e .

# Production stage
FROM python:3.10-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copy installed packages from builder stage
COPY --from=builder /home/app/.local /home/app/.local
COPY --from=builder /home/app/data_quality_sdk /home/app/data_quality_sdk

# Copy example configuration
COPY --chown=app:app examples/docker_example/docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD alation-dq --health-check || exit 1

# Default command
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["alation-dq"]

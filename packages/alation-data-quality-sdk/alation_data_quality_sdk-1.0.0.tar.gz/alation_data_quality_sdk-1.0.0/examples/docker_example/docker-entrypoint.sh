#!/bin/bash

# Docker entrypoint script for Alation Data Quality SDK

set -e

# Function to print messages with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Validate required environment variables
validate_env() {
    if [ -z "$ALATION_HOST" ]; then
        log "ERROR: ALATION_HOST environment variable is required"
        log "Set it to your Alation instance URL (e.g., https://my-alation.company.com)"
        exit 1
    fi

    if [ -z "$MONITOR_ID" ]; then
        log "ERROR: MONITOR_ID environment variable is required"
        log "Set it to the ID of the monitor you want to execute"
        exit 1
    fi

    log "✅ Environment validation passed"
    log "   ALATION_HOST: $ALATION_HOST"
    log "   MONITOR_ID: $MONITOR_ID"
    log "   DRY_RUN: ${DRY_RUN:-false}"
    log "   IS_TEST_RUN: ${IS_TEST_RUN:-false}"
}

# Run health check
health_check() {
    log "🔍 Running health check..."
    if alation-dq --health-check; then
        log "✅ Health check passed"
    else
        log "❌ Health check failed"
        exit 1
    fi
}

# Main execution function
main() {
    log "🚀 Starting Alation Data Quality SDK"

    # Validate environment
    validate_env

    # Run health check if not in dry run mode
    if [ "${DRY_RUN:-false}" != "true" ]; then
        health_check
    fi

    log "📊 Executing data quality checks..."

    # Execute the command passed to the container
    exec "$@"
}

# Handle different command types
case "$1" in
    "alation-dq")
        main "$@"
        ;;
    "bash"|"sh")
        # Allow interactive shell access
        exec "$@"
        ;;
    "health-check")
        # Just run health check
        validate_env
        health_check
        ;;
    *)
        # For any other commands, just execute them
        log "🔧 Executing command: $*"
        exec "$@"
        ;;
esac

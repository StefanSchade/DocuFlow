#!/bin/bash

# Ensure Docker daemon is running
dockerd &

# Wait for Docker daemon to start
while(! docker info > /dev/null 2>&1); do
    echo "Waiting for Docker to start..."
    sleep 1
done

# Ensure the appuser owns the data directory and its contents
chown -R appuser:appgroup /workspace/data

# Run the pipeline script with the provided arguments
exec python /app/src/pipeline.py "$@"

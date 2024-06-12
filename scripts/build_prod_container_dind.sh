#!/bin/bash

# Ensure Docker daemon is running
dockerd &

# Wait for Docker daemon to start
while(! docker info > /dev/null 2>&1); do
    echo "Waiting for Docker to start..."
    sleep 1
done

# Check if Dockerfile path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/Dockerfile.prod"
    exit 1
fi

DOCKERFILE_PATH=$1

# Get the directory of the provided Dockerfile
DOCKERFILE_DIR=$(dirname "$DOCKERFILE_PATH")

# Build the Docker image
docker build -f "$DOCKERFILE_PATH" "$DOCKERFILE_DIR" -t prod-environment .

if [ $? -ne 0 ]; then
    echo "Docker build failed"
    exit 1
fi

echo "Docker build completed successfully"

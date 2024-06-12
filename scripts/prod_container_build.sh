#!/bin/bash

# Ensure Docker is available
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found. Please ensure Docker Desktop is running."
    exit 1
fi

# Navigate to the project directory
cd /mnt/c/Users/your-username/Documents/REPOS/docuflow

# Build the Docker image
docker build -f ./docker/Dockerfile.prod -t prod-environment .

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Docker build failed"
    exit 1
fi

echo "Docker build completed successfully"

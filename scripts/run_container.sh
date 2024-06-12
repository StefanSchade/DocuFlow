#!/bin/bash

# Check if data directory and additional arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 /path/to/data [additional arguments for pipeline.py]"
    exit 1
fi

DATA_DIR=$1
shift

# Debug information
echo "Data directory: $DATA_DIR"
echo "Additional arguments: $@"

# Run the Docker container with the provided data directory and additional arguments
docker run --rm -v "$DATA_DIR":/workspace/data prod-environment "$@"

# Check if the docker command was successful
if [ $? -ne 0 ]; then
    echo "Docker command failed"
    exit 1
fi

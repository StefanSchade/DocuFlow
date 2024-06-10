#!/bin/bash

# Check if a test type parameter is provided
if [ -z "$1" ]; then
    echo "Usage: $0 [unit|integration]"
    exit 1
fi

# Set the PYTHONPATH to the src directory
export PYTHONPATH=/workspace/src
export DEBUG_PRINTS=true

# Run pytest with the specified marker
if [ "$1" == "unit" ]; then
    pytest -m unit -s
elif [ "$1" == "integration" ]; then
    pytest -m integration -s
else
    echo "Invalid parameter: $1"
    echo "Usage: $0 [unit|integration]"
    exit 1
fi

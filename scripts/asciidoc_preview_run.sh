#!/bin/bash

# Function to ensure paths are Unix-style and have a trailing slash
normalize_path() {
  local path="$1"
  path="${path//\\//}" # Convert backslashes to forward slashes
  [[ "$path" != */ ]] && path="$path/" # Add trailing slash if not present
  echo "$path"
}

# Function to wait for a Docker container to be up and running
wait_for_container() {
  local container_name="$1"
  local retries=10
  local count=0

  while [ $count -lt $retries ]; do
    if docker ps | grep -q "$container_name"; then
      echo "Container $container_name is running."
      return 0
    fi
    count=$((count + 1))
    echo "Waiting for container $container_name to start... ($count/$retries)"
    sleep 1
  done

  echo "Error: Container $container_name did not start within expected time."
  return 1
}

# Define the project root and other directories
ROOT_IN_CONTAINER=$(dirname $(dirname $(realpath $0)))
HOST_HOME=$(normalize_path "$HOST_HOME")
REPO_ROOT=$(normalize_path "$REPO_ROOT")
REPO_NAME=$(normalize_path "$REPO_NAME")

PROJECT_ROOT="${HOST_HOME}${REPO_ROOT}${REPO_NAME}"
DOCKERFILE="${ROOT_IN_CONTAINER}/docker/Dockerfile.asciidoc-preview"
DOCS_DIR=$(normalize_path "${PROJECT_ROOT}docs")
OUTPUT_DIR="${ROOT_IN_CONTAINER}/target/docs/html"

# Log the determined paths
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "DOCKERFILE: $DOCKERFILE"
echo "DOCS_DIR: $DOCS_DIR"
echo "OUTPUT_DIR: $OUTPUT_DIR"

# Ensure the Dockerfile path exists
if [ ! -f "$DOCKERFILE" ]; then
  echo "ERROR: Dockerfile not found at $DOCKERFILE"
  exit 1
fi

# Create the output directory and clear any previous content
mkdir -p "$OUTPUT_DIR"
rm -rf "$OUTPUT_DIR"/*

# Build the Docker image
echo "Building Docker image..."
docker build -t asciidoc-preview -f "$DOCKERFILE" "$ROOT_IN_CONTAINER"

# Handle existing container conflict
if docker ps -a --format '{{.Names}}' | grep -Eq "^asciidoc-preview\$"; then
  echo "Removing existing asciidoc-preview container..."
  docker rm -f asciidoc-preview
fi

# List the docs directory
echo "Listing DOCS_DIR before running the container:"
ls -al "$DOCS_DIR"

# Run the Docker container
docker run --rm -v "$(normalize_path "$DOCS_DIR"):/workspace/docs" -v "$(normalize_path "$OUTPUT_DIR"):/workspace/target/docs/html" -p 35729:35729 -p 4000:4000 --name asciidoc-preview asciidoc-preview &

# Wait for the container to be up and running
if ! wait_for_container "asciidoc-preview"; then
  exit 1
fi

# Function to handle SIGINT and SIGTERM signals
cleanup() {
  echo "Received signal, shutting down..."
  docker stop asciidoc-preview
  exit 0
}

trap 'cleanup' SIGINT SIGTERM

# Wait for the container process to exit
wait $!

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

# Log the determined paths
echo "******************************************************************"
echo "$0"
echo "******************************************************************"


# Define the project root and other directories
ROOT_IN_CONTAINER=$(dirname $(dirname $(realpath $0)))
HOST_HOME=$(normalize_path "$HOST_HOME")
REPO_ROOT=$(normalize_path "$REPO_ROOT")
REPO_NAME=$(normalize_path "$REPO_NAME")

PROJECT_ROOT="${HOST_HOME}${REPO_ROOT}${REPO_NAME}"
DOCKERFILE="${ROOT_IN_CONTAINER}/docker/Dockerfile.asciidoc-preview"
DOCS_DIR_OUTSIDE=${PROJECT_ROOT}docs
DOCS_DIR_INSIDE=${ROOT_IN_CONTAINER}/docs
OUTPUT_DIR="${ROOT_IN_CONTAINER}/target/docs/html"

# Log the determined paths
echo ""
echo "PATH NAMES:"
echo "-----------"
echo "PROJECT_ROOT:             $PROJECT_ROOT"
echo "DOCKERFILE:               $DOCKERFILE"
echo "DOCS_DIR_OUTSIDE:         $DOCS_DIR_OUTSIDE"
echo "DOCS_DIR_INSIDE:          $DOCS_DIR_INSIDE"
echo "OUTPUT_DIR:               $OUTPUT_DIR"
echo ""

# Create the output directory and clear any previous content
mkdir -p "$OUTPUT_DIR"
rm -rf "$OUTPUT_DIR"/*

# List the docs directory
echo "Content of DOCS_DIR_OUTSIDE before running the container:"
echo "---------------------------------------------------------"
ls -al "$DOCS_DIR_INSIDE"
echo ""

# Ensure the Dockerfile exists
if [ ! -f "$DOCKERFILE" ]; then
  echo "ERROR: Dockerfile not found at $DOCKERFILE"
  exit 1
else
  echo "Build and run Container, awaiting startup:"
  echo "------------------------------------------"
fi

# Build the Docker image
echo "Dockerfile found, building image..."
docker build -t asciidoc-preview -f "$DOCKERFILE" "$ROOT_IN_CONTAINER"

# Handle existing container conflict
if docker ps -a --format '{{.Names}}' | grep -Eq "^asciidoc-preview\$"; then
  echo "Removing existing asciidoc-preview container..."
  docker rm -f asciidoc-preview
fi

# Run the Docker container
docker run --rm -v "$(normalize_path "$DOCS_DIR_OUTSIDE"):/workspace/docs" -v "$(normalize_path "$OUTPUT_DIR"):/workspace/target/docs/html" -p 35729:35729 -p 4000:4000 --name asciidoc-preview asciidoc-preview &

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

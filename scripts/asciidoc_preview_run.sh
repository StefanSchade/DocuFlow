#!/bin/bash

# Source and call helper script
source /workspace/scripts/helper/log_helper.sh && log_script_name
source /workspace/scripts/helper/wait_for_container.sh
source /workspace/scripts/helper/normalize_path.sh

# Function to handle SIGINT and SIGTERM signals
cleanup() {
  echo "Received signal, shutting down..."
  docker stop asciidoc-preview
  exit 0
}

main() {
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
docker run --rm \
           -v "$(normalize_path "$DOCS_DIR_OUTSIDE"):/workspace/docs" \
           -v "$(normalize_path "$OUTPUT_DIR"):/workspace/target/docs/html" \
           -p 35729:35729 \
           -p 4000:4000 \
           --name asciidoc-preview \
           asciidoc-preview &

# Wait for the container to be up and running
if ! wait_for_container "asciidoc-preview"; then
  echo "Container did not start in the expected time limit..."
  exit 1
fi

trap 'cleanup' SIGINT SIGTERM

# Wait for the container process to exit
wait $!
}

main
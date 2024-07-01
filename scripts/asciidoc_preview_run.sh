#!/bin/bash

# Define the project root and other directories
PROJECT_ROOT=$(dirname $(dirname $(realpath $0)))
DOCKERFILE=$PROJECT_ROOT/docker/Dockerfile.asciidoc-preview
DOCS_DIR=$PROJECT_ROOT/docs
OUTPUT_DIR=$PROJECT_ROOT/target/docs/html

# Convert paths to Windows style if running on Windows
if [[ "$OSTYPE" == "msys" ]]; then
  PROJECT_ROOT=$(cygpath -w "$PROJECT_ROOT")
  DOCKERFILE=$(cygpath -w "$DOCKERFILE")
  DOCS_DIR=$(cygpath -w "$DOCS_DIR")
  OUTPUT_DIR=$(cygpath -w "$OUTPUT_DIR")
fi

# Log the determined paths
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "DOCKERFILE: $DOCKERFILE"
echo "DOCS_DIR: $DOCS_DIR"
echo "OUTPUT_DIR: $OUTPUT_DIR"

# Create the output directory
mkdir -p $OUTPUT_DIR

# Build the Docker image
docker build -t asciidoc-preview -f $DOCKERFILE $PROJECT_ROOT

# List the docs directory before running the container
echo "Listing DOCS_DIR before running the container:"
ls -al $DOCS_DIR

# Run the Docker container
docker run --rm -v "$DOCS_DIR:/workspace/docs" -v "$OUTPUT_DIR:/workspace/target/docs/html" -p 35729:35729 -p 4000:4000 --name asciidoc-preview asciidoc-preview

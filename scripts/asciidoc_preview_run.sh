#!/bin/bash

# Define the project root and other directories
PROJECT_ROOT=$(dirname $(dirname $(realpath $0)))
DOCKERFILE=$PROJECT_ROOT/docker/Dockerfile.asciidoc-preview
DOCS_DIR=$PROJECT_ROOT/docs

# Build the Docker image
docker build -t asciidoc-preview -f $DOCKERFILE $PROJECT_ROOT

# Run the Docker container with a specified name
docker run --rm --name asciidoc-preview -v $DOCS_DIR:/workspace/docs -p 35729:35729 -p 4000:4000 asciidoc-preview

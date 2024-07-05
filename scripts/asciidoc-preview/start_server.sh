#!/bin/bash

start_server() {
  cd "$OUTPUT_DIR"
  echo "Current working directory before starting livereloadx: $(pwd)"
  echo "Content of output dir"
  ls -al
  echo "Starting livereloadx..."
  livereloadx -s . -p 4000 --verbose &

  LIVERELOAD_PID=$!

  # Wait for livereloadx to start
  sleep 5

  # Check if livereloadx is running
  if ps -p $LIVERELOAD_PID > /dev/null; then
    echo "livereloadx started successfully."
  else
    echo "Error: livereloadx failed to start."
    exit 1
  fi

  # Adding a test request to see if the livereloadx server is responding correctly
  curl -I http://localhost:4000

  # Exporting the PID to be used in cleanup
  export LIVERELOAD_PID
}

#!/bin/sh

# Convert all .adoc files to .html and watch for changes
watch_and_convert() {
  while inotifywait -e modify,create,delete -r /workspace/docs; do
    find /workspace/docs -name "*.adoc" -exec asciidoctor {} \;
  done
}

# Handle SIGINT and SIGTERM for graceful shutdown
term_handler() {
  echo "Stopping processes..."
  kill -TERM "$WATCH_PID" 2>/dev/null
  kill -TERM "$LIVERELOAD_PID" 2>/dev/null
  exit 0
}

# Trap SIGINT and SIGTERM
trap 'term_handler' SIGINT SIGTERM

# Run the watch_and_convert function in the background
watch_and_convert &
WATCH_PID=$!

# Start livereloadx to serve the files
cd /workspace/docs
livereloadx -s . -p 4000 &
LIVERELOAD_PID=$!

# Wait for both processes
wait $WATCH_PID
wait $LIVERELOAD_PID

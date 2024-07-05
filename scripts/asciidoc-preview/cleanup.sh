# Function to handle SIGINT and SIGTERM signals
cleanup() {
  echo "Received signal, shutting down..."
  kill -s SIGTERM $WATCH_PID
  kill -s SIGTERM $LIVERELOAD_PID
  exit 0
}

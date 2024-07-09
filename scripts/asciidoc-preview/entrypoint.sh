#!/bin/bash

# Get the directory of the currently executing script
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Define the input and output directories
OUTPUT_DIR=/workspace/target/docs/html
INPUT_DIR=/workspace/docs
LOG_DIR=/workspace/logs
LOG_FILE="$LOG_DIR/logfile.txt"

# Ensure the output directory and log directory exist
mkdir -p $OUTPUT_DIR
mkdir -p $LOG_DIR

# Redirect stderr to the log file
exec 2>>"$LOG_FILE"

# Source helper scripts
source "$SCRIPT_DIR/../helper/log_helper.sh" && log_script_name
source "$SCRIPT_DIR/cleanup.sh"
source "$SCRIPT_DIR/refresh_directory.sh"
source "$SCRIPT_DIR/refresh_output.sh"
source "$SCRIPT_DIR/check_input_directory.sh"
source "$SCRIPT_DIR/generate_index.sh"
source "$SCRIPT_DIR/list_subdirs_contianing_adocs.sh"
source "$SCRIPT_DIR/convert_all_adoc_files.sh"
source "$SCRIPT_DIR/start_server.sh"
source "$SCRIPT_DIR/check_server_status.sh"
source "$SCRIPT_DIR/input_changes.sh"
#source "$SCRIPT_DIR/start_inotifywait.sh"
#source "$SCRIPT_DIR/start_fswatch.sh"
#source "$SCRIPT_DIR/handle_adoc_change.sh"
#source "$SCRIPT_DIR/handle_adoc_deletion.sh"
#source "$SCRIPT_DIR/handle_adoc_creation.sh"
#source "$SCRIPT_DIR/handle_adoc_rename.sh"
#source "$SCRIPT_DIR/handle_directory_change.sh"
echo "sourced scripts in: $SCRIPT_DIR" >&2

# Trap the signals and call the cleanup function
trap 'cleanup' SIGINT SIGTERM
# Main function to run the preview
main() {
  check_input_directory "${INPUT_DIR}"
  full_refresh_output
  start_server
  start_watching_input_changes
  while true; do
    check_server_status
    sleep 1
  done
}

main

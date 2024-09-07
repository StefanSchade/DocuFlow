#!/bin/bash

# author: Stefan Schade
#
# description:
# This is an entrypoint for a dockerfile dedicated to perform 3 tasks
# 1. scan INPUT_DIR for asciidoc files (*.adoc), transform them into
#    html and replicate the input structure in OUTPUT_DIR
# 2. setting up a local web server that serves the html files to
#    localhost:4000. This server will refresh in case the html changes
# 3. watch the INPUT_DIR for changes to the asciidoc files or directories
#    and update the html.
#
# The result is a live preview when editing asciidoc files with a text
# editor in the browser.
# 
# As we operate in a dockerfile on a foreign (mounted) filesystem, tools
# that watch the filesystem relying on linux kernel features (eg. fswatch,
# inotifywait) do not work reliably - therefore we primitively poll the 
# file system repeatedly and look for changes. this assumes we have a 
# managable amount of data in the INPUT_DIR which seems reasonalbe for the
# use case.

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
#
source "$SCRIPT_DIR/../helper/log_helper.sh" && log_script_name
source "$SCRIPT_DIR/_cleanup.sh"

source "$SCRIPT_DIR/adoc_to_html/refresh_output.sh"

source "$SCRIPT_DIR/live_server/start_server.sh"
source "$SCRIPT_DIR/live_server/check_server_status.sh"

source "$SCRIPT_DIR/monitor_changes/input_changes.sh"

#source "$SCRIPT_DIR/generate_index.sh"
#source "$SCRIPT_DIR/list_subdirs_contianing_adocs.sh"
source "$SCRIPT_DIR/convert_all_adoc_files.sh"




#source "$SCRIPT_DIR/start_inotifywait.sh"
#source "$SCRIPT_DIR/refresh_directory.sh"
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
 start_server
  start_watching_input_changes
  while true; do
    check_server_status
    sleep 1
  done
}

main

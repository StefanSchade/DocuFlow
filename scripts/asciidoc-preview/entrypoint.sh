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
source "$SCRIPT_DIR/helpers.sh"
source "$SCRIPT_DIR/generate_index.sh"
source "$SCRIPT_DIR/convert_all_adoc_files.sh"
echo "sourced scripts in: $SCRIPT_DIR" >&2

# Trap the signals and call the cleanup function
trap 'cleanup' SIGINT SIGTERM

# Function to check if the input directory is correctly mounted
check_input_directory() {
  local input_dir=$1
  if [ -d "$input_dir" ]; then
    echo "$input_dir exists." >&2
  else
    echo "$input_dir does not exist." >&2
    exit 1
  fi
}

# Function to list subdirectories containing .adoc files
list_subdirs_containing_adocs() {
  local dir=$1
  find "$dir" -type d -exec sh -c 'shopt -s nullglob; adoc_files=("$1"/*.adoc); [ "${#adoc_files[@]}" -gt 0 ]' _ {} \; -print
}

# Function to clean the output directory
clean_output_directory() {
  local output_dir=$1
  rm -rf "$output_dir"/*
  mkdir -p "$output_dir"
}

# Function to refresh a single directory
refresh_directory() {
  local adoc_input_dir=$1
  local html_output_dir=$2

  echo "Performing initial conversion of .adoc files to .html..." >&2
  convert_all_adoc_files "$adoc_input_dir" "$html_output_dir"
  
  echo "Looking for subdirectories containing .adoc files..." >&2 
  local subdirectories
  subdirectories=$(list_subdirs_containing_adocs "$adoc_input_dir")

  echo "Generating index.html file..." >&2
  generate_index "$subdirectories" "$adoc_input_dir" "$html_output_dir"

  # In lieu of a return value
  echo "$subdirectories"
}

# Function to clean all output and generate everything again
refresh_completely() {
  local adoc_input_dir=$1
  local html_output_dir=$2

  echo "Cleaning output directory of previous content..." >&2
  clean_output_directory "$html_output_dir"

  local subdirectories=(".") # One entry to start with

  while [ ${#subdirectories[@]} -gt 0 ]; do
    local new_subdirs=()
    for subdir in "${subdirectories[@]}"; do
      local adoc_subdir="$adoc_input_dir/$subdir"
      local html_subdir="$html_output_dir/$subdir"
      echo "Processing directory: $adoc_subdir" >&2
      local result
      result=$(refresh_directory "$adoc_subdir" "$html_subdir")
      new_subdirs+=($result)
    done
    subdirectories=("${new_subdirs[@]}")
  done
}

# Main function to run the preview
run_preview() {
  check_input_directory "$INPUT_DIR"
  refresh_completely "$INPUT_DIR" "$OUTPUT_DIR"
  while true; do
    sleep 1
  done
}

run_preview

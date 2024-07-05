#!/bin/bash

# Function to check if input directory is correctly mounted
check_input_directory() {
  local input_dir=$1
  echo "Checking if input directory is correctly mounted...">&2
  if [ -d "$input_dir" ]; then
    echo "$input_dir exists and contains these files:">&2
    ls -la $input_dir
  else
    echo "$input_dir does not exist.">&2
    exit 1
  fi
}

# Function to clean the output directory
clean_output_directory() {
  local output_dir=$1
  rm -rf "$output_dir/*"
  mkdir -p "$output_dir"
}

#!/bin/bash

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

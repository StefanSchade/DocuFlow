#!/bin/bash

# Function to convert all .adoc files to .html initially
convert_all_adoc_files() {
  local input_dir=$1
  local output_dir=$2
  find "$input_dir" -name "*.adoc" | while read -r adoc_file; do
    relative_path="${adoc_file#$input_dir/}"
    output_subdir="$output_dir/$(dirname "$relative_path")"
    mkdir -p "$output_subdir"
    asciidoctor -D "$output_subdir" "$adoc_file"
  done
}

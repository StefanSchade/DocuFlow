#!/bin/bash

# Function to convert all .adoc files to .html initially
convert_all_adoc_files() {
  local input_dir=$1
  local output_dir=$2
  find "$input_dir" -name "*.adoc" -exec asciidoctor -D "$output_dir" {} \;
}

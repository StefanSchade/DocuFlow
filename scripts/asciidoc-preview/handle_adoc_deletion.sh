#!/bin/bash

handle_adoc_deletion() {
  local path=$1
  local file=$2
  local relative_path="${path#$INPUT_DIR/}"
  local output_path="${OUTPUT_DIR}/${relative_path%/*}"
  local html_file="${output_path}/${file%.adoc}.html"

  echo "Handling .adoc deletion: $path$file" >&2
  rm -f "$html_file"
  generate_index "$output_path"
}

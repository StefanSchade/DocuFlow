#!/bin/bash

handle_adoc_change() {
  local path=$1
  local file=$2
  local relative_path="${path#$INPUT_DIR/}"
  local output_path="${OUTPUT_DIR}/${relative_path%/*}"

  echo "Handling .adoc change: $path$file" >&2
  asciidoctor -D "$output_path" "$path$file"
  generate_index "$output_path"
}

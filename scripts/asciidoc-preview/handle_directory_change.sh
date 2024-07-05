#!/bin/bash

handle_directory_change() {
  local path=$1
  local relative_path="${path#$INPUT_DIR/}"

  echo "Handling directory change: $path" >&2
  partial_refresh_output "$relative_path"
}

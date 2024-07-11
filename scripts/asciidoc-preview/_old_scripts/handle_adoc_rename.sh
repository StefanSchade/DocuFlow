#!/bin/bash

handle_adoc_rename() {
  local path=$1
  local file=$2

  echo "Handling .adoc rename: $path$file" >&2
  # Handle the rename as a deletion and creation
  handle_adoc_deletion "$path" "$file"
  handle_adoc_creation "$path" "$file"
}

#!/bin/bash

# Function to generate a snapshot of the directory structure
generate_snapshot() {
  local dir=$1
  find "$dir" -type d -print0 | while IFS= read -r -d '' subdir; do
    echo "D $(stat --format='%Y' "$subdir") $subdir"
    echo "D $(stat --format='%Y' "$subdir") $subdir" >&2
    find "$subdir" -maxdepth 1 -type f -print0 | while IFS= read -r -d '' file; do
      echo "F $(stat --format='%Y' "$file") $file"
      echo "F $(stat --format='%Y' "$file") $file" >&2
    done
  done
}

# Function to compare snapshots and detect changes
compare_snapshots() {
  local old_snapshot=$1
  local new_snapshot=$2

  declare -A old_dirs old_files new_dirs new_files

  # Parse old snapshot
  while IFS= read -r line; do
    type=$(echo "$line" | cut -d ' ' -f 1)
    timestamp=$(echo "$line" | cut -d ' ' -f 2)
    path=$(echo "$line" | cut -d ' ' -f 3-)
    if [[ "$type" == "D" ]]; then
      old_dirs["$path"]=$timestamp
    else
      old_files["$path"]=$timestamp
    fi
  done <<< "$old_snapshot"

  # Parse new snapshot
  while IFS= read -r line; do
    type=$(echo "$line" | cut -d ' ' -f 1)
    timestamp=$(echo "$line" | cut -d ' ' -f 2)
    path=$(echo "$line" | cut -d ' ' -f 3-)
    if [[ "$type" == "D" ]]; then
      new_dirs["$path"]=$timestamp
    else
      new_files["$path"]=$timestamp
    fi
  done <<< "$new_snapshot"

  # Detect deleted and modified files/directories
  for path in "${!old_files[@]}"; do
    if [[ ! -v new_files["$path"] ]]; then
      handle_file_deletion "$path"
    elif [[ "${old_files[$path]}" -ne "${new_files[$path]}" ]]; then
      handle_file_update "$path"
    fi
  done

  for path in "${!old_dirs[@]}"; do
    if [[ ! -v new_dirs["$path"] ]]; then
      handle_directory_change "$(dirname "$path")"
    fi
  done

  # Detect new files/directories
  for path in "${!new_files[@]}"; do
    if [[ ! -v old_files["$path"] ]]; then
      handle_file_creation "$path"
    fi
  done

  for path in "${!new_dirs[@]}"; do
    if [[ ! -v old_dirs["$path"] ]]; then
      handle_directory_change "$(dirname "$path")"
    fi
  done
}

# Main function to start watching input changes
start_watching_input_changes() {
  local snapshot old_snapshot

  # Initial snapshot
  snapshot=$(generate_snapshot "$INPUT_DIR")

  while true; do
    old_snapshot=$snapshot
    snapshot=$(generate_snapshot "$INPUT_DIR")

    compare_snapshots "$old_snapshot" "$snapshot"

    sleep 3
  done
}

# Handler for file creation
handle_file_creation() {
  local path=$1
  echo "Handling file creation: $path" >&2
  handle_file_update "$path"
  handle_index_update "$(dirname "$path")"
}

# Handler for file update
handle_file_update() {
  local path=$1
  echo "Handling file update: $path" >&2
  local relative_path="${path#$INPUT_DIR/}"
  local output_path="$OUTPUT_DIR/${relative_path%.adoc}.html"
  asciidoctor -D "$(dirname "$output_path")" "$path"
}

# Handler for file deletion
handle_file_deletion() {
  local path=$1
  echo "Handling file deletion: $path" >&2
  local relative_path="${path#$INPUT_DIR/}"
  local output_path="$OUTPUT_DIR/${relative_path%.adoc}.html"
  rm -f "$output_path"
  handle_index_update "$(dirname "$path")"
}

# Handler for directory changes
handle_directory_change() {
  local dir=$1
  echo "Handling directory change: $dir" >&2
  local relative_dir="${dir#$INPUT_DIR/}"
  partial_refresh_output "$relative_dir"
}

# Handler for index update
handle_index_update() {
  local dir=$1
  echo "Updating index for directory: $dir" >&2
  generate_index "$dir" "$OUTPUT_DIR/$dir"
}

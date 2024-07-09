#!/bin/bash

start_watching_input_changes() {
  generate_snapshot "$INPUT_DIR" old_snapshot
  while true; do
    sleep 15
    echo "start_watching_input_changes: generate snapshots" >&2
    generate_snapshot "$INPUT_DIR" new_snapshot
    echo "Contents of new_snapshot:" >&2
    for entry in "${new_snapshot[@]}"; do
      echo "$entry" >&2
    done
    echo "start_watching_input_changes: comparing snapshots" >&2
    compare_snapshots old_snapshot new_snapshot
    old_snapshot=("${new_snapshot[@]}")
  done
}

# Function to generate a snapshot of the directory structure
generate_snapshot() {
  local dir=$1
  local -n snapshot=$2
  snapshot=()

  # Use find to list directories and files in a single stream
  while IFS= read -r -d '' entry; do
    if [ -d "$entry" ]; then
      local snapshotline="D $(stat --format='%Y' "$entry") $entry"
    else
      local snapshotline="F $(stat --format='%Y' "$entry") $entry"
    fi
    snapshot+=("$snapshotline")
    echo "$snapshotline" >&2
  done < <(find "$dir" \( -type d -o -type f \( -name '*.adoc' -o -name '*.asciidoc' \) \) -print0)
}

# Function to compare snapshots and detect changes
compare_snapshots() {
  local -n old_snap=$1
  local -n new_snap=$2

  local old_dirs=$(printf "%s\n" "${old_snap[@]}" | grep '^D' | sort)
  local new_dirs=$(printf "%s\n" "${new_snap[@]}" | grep '^D' | sort)

  local old_files=$(printf "%s\n" "${old_snap[@]}" | grep '^F' | sort)
  local new_files=$(printf "%s\n" "${new_snap[@]}" | grep '^F' | sort)

  echo "compare_snapshots: line count old_dirs=$(echo "$old_dirs" | wc -l), new_dirs=$(echo "$new_dirs" | wc -l), old_files=$(echo "$old_files" | wc -l), new_files=$(echo "$new_files" | wc -l)" >&2

  echo "compare_snapshots: old_dirs" >&2
  echo "$old_dirs" >&2
  echo "compare_snapshots: new_dirs" >&2
  echo "$new_dirs" >&2
  echo "compare_snapshots: old_files" >&2
  echo "$old_files" >&2
  echo "compare_snapshots: new_files" >&2
  echo "$new_files" >&2

  # Use an associative array to collect unique directories to handle
  declare -A dirs_to_handle

  # Check for timestamp changes first and register the directory itself
  check_timestamp_changes() {
    while IFS= read -r old_line; do
      local old_timestamp=$(echo "$old_line" | cut -d' ' -f2)
      local old_dirname=$(echo "$old_line" | cut -d' ' -f3-)
      local new_line=$(echo "$new_dirs" | grep " $old_dirname$")
      if [[ -n "$new_line" ]]; then
        local new_timestamp=$(echo "$new_line" | cut -d' ' -f2)
        if [[ "$old_timestamp" != "$new_timestamp" ]]; then
          echo "check_timestamp_changes: found timestamp change in dir $old_dirname" >&2
          dirs_to_handle["$old_dirname"]=1 # register the directory itself
        fi
      fi
    done <<< "$old_dirs"
  }

  # Check for true deletions and additions, skipping timestamp changes
  collect_dirs_to_refresh_cause_dir_event() {
    # Find true deletions
    comm -23 <(echo "$old_dirs") <(echo "$new_dirs") | while read -r line; do
      local dirname=$(echo "$line" | cut -d' ' -f3-)
      if [[ -z "${dirs_to_handle[$dirname]}" ]]; then
        local timestamp=$(echo "$line" | cut -d' ' -f2)
        echo "collect_dirs_to_refresh_cause_dir_event: found deleted dir $dirname with timestamp $timestamp" >&2
        dirs_to_handle["$(dirname "$dirname")"]=1 # extract parent directory
      fi
    done

    # Find true additions
    comm -13 <(echo "$old_dirs") <(echo "$new_dirs") | while read -r line; do
      local dirname=$(echo "$line" | cut -d' ' -f3-)
      if [[ -z "${dirs_to_handle[$dirname]}" ]]; then
        local timestamp=$(echo "$line" | cut -d' ' -f2)
        echo "collect_dirs_to_refresh_cause_dir_event: found added dir $dirname with timestamp $timestamp" >&2
        dirs_to_handle["$(dirname "$dirname")"]=1
      fi
    done
  }

  # file is added / deleted (rename -> both) parent dir -> list of dirs to be refreshed
  collect_dirs_to_refresh_cause_file_events() {
    comm -23 <(echo "$old_files") <(echo "$new_files") | while read -r line; do
      local filename=$(echo "$line" | cut -d' ' -f3-)
      local timestamp=$(echo "$line" | cut -d' ' -f2)
      echo "collect_dirs_to_refresh_cause_file_events: found deleted file $filename with timestamp $timestamp" >&2
      dirs_to_handle["$(dirname "$filename")"]=1
    done

    comm -13 <(echo "$old_files") <(echo "$new_files") | while read -r line; do
      local filename=$(echo "$line" | cut -d' ' -f3-)
      local timestamp=$(echo "$line" | cut -d' ' -f2)
      echo "collect_dirs_to_refresh_cause_file_events: found added file $filename with timestamp $timestamp" >&2
      dirs_to_handle["$(dirname "$filename")"]=1
    done
  }

  check_timestamp_changes
  collect_dirs_to_refresh_cause_dir_event
  collect_dirs_to_refresh_cause_file_events

  # Sort directories lexically and handle each one uniquely
  unique_dirs=($(for dir in "${!dirs_to_handle[@]}"; do echo "$dir"; done | sort))

  # Use an associative array to ensure no redundant processing of subdirectories
  declare -A processed_dirs

  for dir in "${unique_dirs[@]}"; do
    if [[ ! -v processed_dirs["$dir"] ]]; then
      processed_dirs["$dir"]=1
      local relative_subdir="${dir#$INPUT_DIR/}" # Remove base path
      echo "compare_snapshots: calling handle_directory_refresh for $relative_subdir" >&2
      partial_refresh_output "$relative_subdir"
    fi
  done
}
  # file is added / deleted (rename -> both) parent dir -> list of dirs to be refreshed
  collect_dirs_to_refresh_cause_file_events() {
    comm -23 <(echo "$old_files") <(echo "$new_files") | while read -r line; do
      local filename=$(echo "$line" | cut -d' ' -f3-)
      local timestamp=$(echo "$line" | cut -d' ' -f2)
      echo "collect_dirs_to_refresh_cause_file_events: found deleted file $filename with timestamp $timestamp" >&2
      dirs_to_handle["$(dirname "$filename")"]=1
    done

    comm -13 <(echo "$old_files") <(echo "$new_files") | while read -r line; do
      local filename=$(echo "$line" | cut -d' ' -f3-)
      local timestamp=$(echo "$line" | cut -d' ' -f2)
      echo "collect_dirs_to_refresh_cause_file_events: found added file $filename with timestamp $timestamp" >&2
      dirs_to_handle["$(dirname "$filename")"]=1
    done
  }

  collect_dirs_to_refresh_cause_dir_event
  collect_dirs_to_refresh_cause_file_events

  # Sort directories lexically and handle each one uniquely
  unique_dirs=($(for dir in "${!dirs_to_handle[@]}"; do echo "$dir"; done | sort))

  # Use an associative array to ensure no redundant processing of subdirectories
  declare -A processed_dirs

  for dir in "${unique_dirs[@]}"; do
    if [[ ! -v processed_dirs["$dir"] ]]; then
      processed_dirs["$dir"]=1
      echo "compare_snapshots: calling handle_directory_refresh for $dir" >&2
      partial_refresh_output "$dir"
    fi
  done
}

# Function to handle file changes (create, modify, delete)
handle_file_change() {
  local file=$1
  local change_type=$2

  case "$change_type" in
    "created")
      echo "Handling file creation: $file" >&2
      handle_adoc_change "$file"
      update_index_for_directory "$(dirname "$file")"
      ;;
    "modified")
      echo "Handling file update: $file" >&2
      handle_adoc_change "$file"
      ;;
    "deleted")
      echo "Handling file deletion: $file" >&2
      update_index_for_directory "$(dirname "$file")"
      ;;
  esac
}

# Function to update the index for a specific directory
update_index_for_directory() {
  local dir=$1
  echo "Updating index for directory: $dir" >&2
  generate_index "$dir"
}

# Function to handle adoc file changes
handle_adoc_change() {
  local fullpath=$1

  local relative_path="${fullpath#$INPUT_DIR/}"
  local output_path="${OUTPUT_DIR}/${relative_path%/*}"

  echo "Handling .adoc change: $fullpath" >&2
  asciidoctor -D "$output_path" "$fullpath"
  generate_index "$output_path"
}

# Set the INPUT_DIR variable to the directory you want to monitor
INPUT_DIR="/workspace/docs"

# Start watching for input changes
start_watching_input_changes

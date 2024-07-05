# Function to list subdirectories containing .adoc files
list_subdirs_containing_adocs_absolute_paths() {
  echo "got here abc" >&2
  local dir=$1
  find "$dir" -type d | while read subdir; do
    if find "$subdir" -maxdepth 1 -name "*.adoc" | read; then
      echo "${subdir#$dir/}"
    fi
  done
}

# Function to list subdirectories containing .adoc files and return relative paths
list_subdirs_containing_adocs_relative_path() {
  echo "got here abc" >&2
  local dir=$1
  local base_path=$2
  find "$dir" -type d | while read -r subdir; do
    echo "Checking subdir: $subdir" >&2
    if [[ "$subdir" != "$dir" && "$subdir" != "$dir/.." && "$subdir" != "$dir/." ]]; then
      if find "$subdir" -maxdepth 1 -name "*.adoc" | read -r; then
        # Remove base path from subdir to get the relative path
        relative_subdir=${subdir#$base_path/}
        echo "Found .adoc in: $relative_subdir" >&2
        echo "$relative_subdir"
      fi
    fi
  done
}


# Function to list subdirectories containing .adoc files and return the last directory level name
list_last_level_subdirs_containing_adocs_dirname() {
  echo "got here abc" >&2
  local dir=$1
  find "$dir" -type d | while read subdir; do
    if find "$subdir" -maxdepth 1 -name "*.adoc" | read; then
      # Extract the last directory level name
      last_level_subdir=$(basename "$subdir")
      echo "$last_level_subdir"
    fi
  done
}
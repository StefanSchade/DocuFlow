# Function to ensure paths are Unix-style and have a trailing slash
normalize_path() {
  local path="$1"
  path="${path//\\//}" # Convert backslashes to forward slashes
  [[ "$path" != */ ]] && path="$path/" # Add trailing slash if not present
  echo "$path"
}

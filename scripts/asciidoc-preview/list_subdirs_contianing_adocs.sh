# Function to list subdirectories containing .adoc files
list_subdirs_containing_adocs() {
  local dir=$1
  find "$dir" -type d -exec sh -c 'shopt -s nullglob; adoc_files=("$1"/*.adoc); [ "${#adoc_files[@]}" -gt 0 ]' _ {} \; -print
}
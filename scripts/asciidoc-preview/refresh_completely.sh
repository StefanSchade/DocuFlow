# Function to clean all output and generate everything again
refresh_completely() {
  local adoc_input_dir=$1

  echo "Cleaning output directory of previous content..." >&2
  clean_output_directory "$OUTPUT_DIR"

  local subdirectories=(".")  # Start with the base directory

  while [ ${#subdirectories[@]} -gt 0 ]; do
    local new_subdirs=()
    for subdir in "${subdirectories[@]}"; do
      echo "Processing directory: ${subdir}" >&2
      local result
      result=$(refresh_directory "$subdir")
      new_subdirs+=($result)
    done
    subdirectories=("${new_subdirs[@]}")
  done
}
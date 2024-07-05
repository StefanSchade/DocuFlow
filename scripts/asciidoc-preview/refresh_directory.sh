refresh_directory() {
  local subdir=$1
  local adoc_subdir="${INPUT_DIR}/${subdir}"
  local html_subdir="${OUTPUT_DIR}/${subdir}"

  echo "refreshing: $html_subdir ($adoc_subdir -> $html_subdir)" >&2

  mkdir -p "$html_subdir"

  convert_all_adoc_files "$adoc_subdir" "$html_subdir"
  local subdirectories
  subdirectories=$(list_subdirs_containing_adocs_relative_path "$adoc_subdir" "$INPUT_DIR" | tr '\n' ' ')

  echo "subdirs with base $OUTPUT_DIR ${subdirectories[*]}" >&2
  
  generate_index "$subdirectories" "$adoc_subdir" "$html_subdir"
  echo "$subdirectories"
}

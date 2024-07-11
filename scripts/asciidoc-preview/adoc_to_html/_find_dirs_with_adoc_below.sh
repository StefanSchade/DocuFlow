# Find all directories below the start path that directly contain asciidoc
find_dirs_containing_adoc_below() {
  local relative_start_path="$1"
  local absolute_input_start_path="${INPUT_DIR}/${relative_start_path}"

  echo "$relative_start_path" # Always include the start dir even if there is no adoc at all
  find "$absolute_input_start_path" -type d | while read -r subdir; do
    echo "Checking subdir: $subdir" >&2
    if [[ "$subdir" != "$absolute_input_start_path" && \
          "$subdir" != "$absolute_input_start_path/.." && \
          "$subdir" != "$absolute_input_start_path/." ]]; then
      if find "$subdir" -maxdepth 1 -name "*.adoc" | read -r; then
        relative_subdir="${subdir#$INPUT_DIR/}" # Remove base path
        echo "Found .adoc in: $relative_subdir" >&2
        echo "$relative_subdir"
      fi
    fi
  done
}




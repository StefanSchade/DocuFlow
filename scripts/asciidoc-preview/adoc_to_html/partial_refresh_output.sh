partial_refresh_output() {
  local relative_start_path=$1
  local absolute_input_start_path="${INPUT_DIR}/${relative_start_path}"
  local absolute_output_start_path="${OUTPUT_DIR}/${relative_start_path}"

  echo "Cleaning dir $absolute_output_start_path of previous files..." >&2
  clean_output_directory "$absolute_output_start_path"

  # Capture output from the function
  local output
  output=$(find_dirs_containing_adoc_below "$relative_start_path")

  # Debugging output
  echo "Output from find_dirs_containing_adoc_below: $output" >&2

  # Initialize an array to store subdirectories
  local subdirectories=()

  # Populate the array by iterating over each line of the output
  while IFS= read -r line; do
    subdirectories+=("$line")
  done <<< "$output"

  # Debugging array population
  echo "Number of subdirectories found: ${#subdirectories[@]}" >&2
  echo "Subdirectories: ${subdirectories[*]}" >&2

  for subdir in "${subdirectories[@]}"; do
    echo "Processing dir | input $INPUT_DIR | output $OUTPUT_DIR | relative $subdir " >&2
    mkdir -p "$OUTPUT_DIR/$subdir"
    find "$INPUT_DIR/$subdir" -maxdepth 1 -name "*.adoc" -exec asciidoctor -D "$OUTPUT_DIR/$subdir" {} \;
  done
  source "$SCRIPT_DIR/generate_index_files.sh"
  generate_all_indexes "$relative_start_path"
}


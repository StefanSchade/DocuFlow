#!/bin/bash

# Get the directory of the currently executing script
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
echo "base directory is: $SCRIPT_DIR"

# Source helper scripts
source "$SCRIPT_DIR/../helper/log_helper.sh" && log_script_name
source "$SCRIPT_DIR/cleanup.sh"
source "$SCRIPT_DIR/helpers.sh"

# Define the input and output directories
OUTPUT_DIR=/workspace/target/docs/html
INPUT_DIR=/workspace/docs

# Ensure the output directory exists
mkdir -p $OUTPUT_DIR

# Trap the signals and call the cleanup function
trap 'cleanup' SIGINT SIGTERM

# Check if input directory is correctly mounted
check_input_directory "$INPUT_DIR"

# Main function to run the preview
run_preview() {
  while true; do
    echo "Cleaning output directory of previous content..."
    clean_output_directory "$OUTPUT_DIR"

    echo "Performing initial conversion of .adoc files to .html..."
    convert_all_adoc_files "$INPUT_DIR" "$OUTPUT_DIR"
    echo "Initial conversion complete."

    echo "Generating index.html file..."
    generate_index "$INPUT_DIR" ""

    while ! FILE_SYSTEM_STRUCTURE_CHANGED; do
      inotifywait -m -e modify,create,delete -r "$INPUT_DIR" | 
      while read -r path action file; do
        echo "inotifywait detected a change: path=$path action=$action file=$file"
        full_path="${path}${file}"
        relative_path="${full_path#$INPUT_DIR/}"
        output_subdir="${OUTPUT_DIR}/$(dirname "$relative_path")"

        if [[ "$file" =~ .*\.adoc$ ]]; then
          echo "Change detected: $action $file"
          echo "Converting $full_path to HTML..."
          asciidoctor -D "$output_subdir" "$full_path"

          # Check if file was converted
          HTML_FILE="${output_subdir}/$(basename "${file}" .adoc).html"
          if [ -f "$HTML_FILE" ]; then
            echo "Conversion complete: $HTML_FILE"
            generate_index "$INPUT_DIR" ""
          else
            echo "Error: Conversion failed for $full_path"
          fi
        elif [[ "$action" == "CREATE" || "$action" == "MOVED_TO" || "$action" == "DELETE" || "$action" == "MOVED_FROM" ]]; then
          echo "Structure change detected: $action $file"
          FILE_SYSTEM_STRUCTURE_CHANGED=true
          break 2
        else
          echo "Ignored change: $action $file"
        fi
      done
    done
  done
}

# Start the preview
run_preview

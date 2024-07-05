#!/bin/bash

# Get the directory of the currently executing script
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Define the input and output directories
OUTPUT_DIR=/workspace/target/docs/html
INPUT_DIR=/workspace/docs
LOG_DIR=/workspace/logs
LOG_FILE="$LOG_FILE/logfile.txt"

# Ensure the output directory exists
mkdir -p $OUTPUT_DIR
mkdir -p $LOG_DIR

# Redirect stderr to the log file
exec 2>>"$LOG_FILE"

# Source helper scripts
source "$SCRIPT_DIR/../helper/log_helper.sh" && log_script_name
source "$SCRIPT_DIR/cleanup.sh" 
source "$SCRIPT_DIR/helpers.sh"
source "$SCRIPT_DIR/generate_index.sh"
source "$SCRIPT_DIR/convert_all_adoc_files.sh"
echo "sourced scripts in: $SCRIPT_DIR">&2

# Trap the signals and call the cleanup function
trap 'cleanup' SIGINT SIGTERM

# Check if input directory is correctly mounted
check_input_directory "$INPUT_DIR"

# process a single directory completely
refresh_directory() {
  local adoc_input_dir=$1
  local html_output_dir=$2

  echo "Performing initial conversion of .adoc files to .html...">&2
  convert_all_adoc_files "$adoc_input_dir" "$html_output_dir"
  
  echo "looking for subdirs containing adocs...">&2 
  subdirectories = list_subdirs_contianing_adocs "$adoc_input_dir"

  echo "Generating index.html file...">&2
  generate_index $subdirectories "$adoc_input_dir" "html_output_dir"

  # in lieu of a return value
  echo subdirectories
}

# function to clean all output and generate everything again
refresh_completely() {
  local adoc_input_dir=$1
  local html_output_dir=$2

  echo "Cleaning output directory of previous content...">&2
  clean_output_directory "$OUTPUT_DIR"

  subdirectories = "." // one entry to start with

  now start a recursive sweep of the directories using the subfunction refresh_directory()

  the result should be that the whole structure is transfered to a dir structure like that

  html_base_dir
  |- index.html
  |- one.html
  |
  |-dev_guide/
  |     |
  |     |-index.html
  |     |-chapter01.html
  |     |-chapter02.html
  |
  |
  |-arch_doc/
  |     |
  |     |-index.html
  |     |-chapter01.html
  |     |-chapter02.html



  

}

# Main function to run the preview
run_preview() {
  while true; do
    
    
    

    

    while ! FILE_SYSTEM_STRUCTURE_CHANGED; do
      inotifywait -m -e modify,create,delete -r "$INPUT_DIR" | 
      while read -r path action file; do
        echo "inotifywait detected a change: path=$path action=$action file=$file">&2
        full_path="${path}${file}"
        relative_path="${full_path#$INPUT_DIR/}"
        output_subdir="${OUTPUT_DIR}/$(dirname "$relative_path")"

        if [[ "$file" =~ .*\.adoc$ ]]; then
          echo "Change detected: $action $file">&2
          echo "Converting $full_path to HTML...">&2
          asciidoctor -D "$output_subdir" "$full_path"

          # Check if file was converted
          HTML_FILE="${output_subdir}/$(basename "${file}" .adoc).html"
          if [ -f "$HTML_FILE" ]; then
            echo "Conversion complete: $HTML_FILE">&2
            generate_index "$INPUT_DIR" ""
          else
            echo "Error: Conversion failed for $full_path">&2
          fi
        elif [[ "$action" == "CREATE" || "$action" == "MOVED_TO" || "$action" == "DELETE" || "$action" == "MOVED_FROM" ]]; then
          echo "Structure change detected: $action $file">&2
          FILE_SYSTEM_STRUCTURE_CHANGED=true
          break 2
        else
          echo "Ignored change: $action $file">&2
        fi
      done
    done
  done
}

# Start the preview
run_preview

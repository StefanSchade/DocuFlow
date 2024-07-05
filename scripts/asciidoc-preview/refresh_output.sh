# Function to clean the output directory
clean_output_directory() {
  local output_dir=$1
  rm -rf "$output_dir"/*
  mkdir -p "$output_dir"
}

# find all directories below the start path that directly contain asciidoc
find_dirs_containing_adoc_below() {
    local relative_start_path="$1"
    local absolute_input_start_path="${INPUT_DIR}/$1"
    
    echo "{$1}" # always include the start dir even if there is no adoc at all
    find "$absolute_input_start_path" -type d | while read -r subdir; do
    echo "Checking subdir: $subdir" >&2
    if [[ "$subdir" != "$absolute_input_start_path" && \
          "$subdir" != "$absolute_input_start_path/.." && \
          "$subdir" != "$absolute_input_start_path/." ]]; then
      if find "$subdir" -maxdepth 1 -name "*.adoc" | read -r; then
        relative_subdir=${subdir#$absolute_input_start_path/} # Remove base path
        echo "Found .adoc in: $relative_subdir" >&2
        echo "$relative_subdir"
      fi
    fi
  done | tr '\n' ';'
}

partial_refresh_output() {
  local relative_start_path=$1
  local absolute_input_start_path="${INPUT_DIR}/$1"
  local absolute_output_start_path="${OUTPUT_DIR}/$1"

  echo "Cleaning dir {$absolute_output_start_path} of previous files..." >&2
  clean_output_directory "$absolute_output_start_path"

  IFS=';' read -r -a subdirectories <<< "$(find_dirs_containing_adoc_below "$relative_start_path")"

  for subdir in "${subdirectories[@]}"; do
      echo "Processing directory: ${subdir} -  base path: ${OUTPUT_DIR} base path: ${INPUT_DIR}" >&2
      mkdir -p "${OUTPUT_DIR}/$subdir"
      find "${INPUT_DIR}/$subdir" -maxdepth 1 -name "*.adoc" -exec 'asciidoctor -D "${1}" "$0"' {} "${OUTPUT_DIR}/${subdir}" \;
      #local result
      #result=$(refresh_directory "$subdir")
      #new_subdirs+=($result)
    #done
    #subdirectories=("${new_subdirs[@]}")
  done
}

# Function to clean all output and generate everything again
full_refresh_output() {
  partial_refresh_output "."
}



#!/bin/bash

# Function to check if input directory is correctly mounted
check_input_directory() {
  local input_dir=$1
  echo "Checking if input directory is correctly mounted..."
  if [ -d "$input_dir" ]; then
    echo "$input_dir exists."
  else
    echo "$input_dir does not exist."
    exit 1
  fi
}

# Function to clean the output directory
clean_output_directory() {
  local output_dir=$1
  rm -rf "$output_dir/*"
  mkdir -p "$output_dir"
}

# Function to convert all .adoc files to .html initially
convert_all_adoc_files() {
  local input_dir=$1
  local output_dir=$2
  find "$input_dir" -name "*.adoc" -exec asciidoctor -D "$output_dir" {} \;
}

# Function to generate index.html
generate_index() {
  local input_dir=$1
  local subdir=$2
  local index_file="${OUTPUT_DIR}/${subdir}index.html"
  echo "<html><body><h1>Generated Documentation</h1><ul>" > "$index_file"
  
  for file in "$OUTPUT_DIR/$subdir"*.html; do
    filename=$(basename "$file")
    echo "<li><a href=\"$filename\">$filename</a></li>" >> "$index_file"
  done
  
  echo "</ul></body></html>" >> "$index_file"
}

# Additional helper functions can be added here

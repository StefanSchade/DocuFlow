#!/bin/bash

list_all_output_dirs() {
  find "$OUTPUT_DIR" -type d
}

generate_index() {
  local dir=$1
  local index_file="${dir}/index.html"
  echo "Generating index.html file in: $index_file" >&2

  echo "<html><body><h1>Generated Documentation</h1><ul>" > "$index_file"
  
  # Add links to subdirectory index files
  subdirs=($(find "$dir" -mindepth 1 -maxdepth 1 -type d | sort))
  for subdir in "${subdirs[@]}"; do
    subdir_name=$(basename "$subdir")
    echo "<li><strong><a href=\"$subdir_name/index.html\">$subdir_name</a></strong></li>" >> "$index_file"
  done

  # Add links to HTML files in the current directory
  files=($(find "$dir" -mindepth 1 -maxdepth 1 -type f -name "*.html" ! -name "index.html" | sort))
  for file in "${files[@]}"; do
    filename=$(basename "$file")
    echo "<li><a href=\"$filename\">$filename</a></li>" >> "$index_file"
  done

  echo "</ul></body></html>" >> "$index_file"
}

generate_all_indexes() {
  local dirs=$(list_all_output_dirs)
  for dir in $dirs; do
    generate_index "$dir"
  done
}

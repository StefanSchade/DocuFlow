#!/bin/bash

list_all_output_dirs() {
  find "$OUTPUT_DIR" -type d
}

generate_index() {
  local dir=$1
  local index_file="${dir}/index.html"
  echo "<html><body><h1>Generated Documentation</h1><ul>" > "$index_file"
  
  # Add links to subdirectory index files
  for subdir in "$dir"/*; do
    if [ -d "$subdir" ]; then
      subdir_name=$(basename "$subdir")
      echo "<li><strong><a href=\"$subdir_name/index.html\">$subdir_name</a></strong></li>" >> "$index_file"
    fi
  done

  # Add links to HTML files in the current directory
  for file in "$dir"/*.html; do
    if [ -f "$file" ]; then
      filename=$(basename "$file")
      if [ "$filename" != "index.html" ]; then
        echo "<li><a href=\"$filename\">$filename</a></li>" >> "$index_file"
      fi
    fi
  done

  echo "</ul></body></html>" >> "$index_file"
}

generate_all_indexes() {
  local relative_start_path="$1"
  local dirs=()

  while IFS= read -r dir; do
    dirs+=("$dir")
  done < <(list_all_output_dirs $relative_start_path)

  for dir in "${dirs[@]}"; do
    echo "Generating index for: $dir" >&2
    generate_index "$dir"
  done
}

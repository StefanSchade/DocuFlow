list_all_output_dirs() {
  find "$OUTPUT_DIR" -type d
}

generate_index() {
  local dir=$1
  local index_file="${dir}/index.html"
  echo "Generating index.html file in: $index_file" >&2

  echo "<html><body><h1>Generated Documentation</h1><ul>" > "$index_file"
  
  # Add links to subdirectory index files
  for subdir in "$dir"/*; do
    if [ -d "$subdir" ]; then
      subdir_name=$(basename "$subdir")
      echo "<li><a href=\"$subdir_name/index.html\">$subdir_name</a></li>" >> "$index_file"
    fi
  done

  # Add links to HTML files in the current directory
  for file in "$dir"/*.html; do
    if [ -f "$file" ]; then
      filename=$(basename "$file")
      echo "<li><a href=\"$filename\">$filename</a></li>" >> "$index_file"
    fi
  done

  echo "</ul></body></html>" >> "$index_file"
}

generate_all_indexes() {
  local dirs=$(list_all_output_dirs)
  for dir in $dirs; do
    generate_index "$dir"
  done
}
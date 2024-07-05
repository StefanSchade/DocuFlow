generate_index() {
  local subdirectories=$1
  local adoc_subdir=$2
  local html_subdir=$3

  local index_file="${html_subdir}/index.html"
  echo "Generating index.html file in: $index_file" >&2

  echo "<html><body><h1>Generated Documentation</h1><ul>" > "$index_file"
  
  # Add links to HTML files in the current directory
  for file in "$html_subdir"/*.html; do
    filename=$(basename "$file")
    echo "<li><a href=\"$filename\">$filename</a></li>" >> "$index_file"
  done

  # Add links to subdirectory index files
  for subdir in $subdirectories; do
    subdir_name=$(basename "$subdir")
    echo "<li><a href=\"$subdir_name/index.html\">$subdir_name</a></li>" >> "$index_file"
  done

  echo "</ul></body></html>" >> "$index_file"
}

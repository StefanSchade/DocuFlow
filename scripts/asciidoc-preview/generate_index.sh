#!/bin/bash

# Function to generate index.html
generate_index() {
  local dir=$1
  for subdir in $(find "$dir" -type d); do
    index_file="${subdir}/index.html"
    echo "<html><body><h1>Generated Documentation</h1><ul>" > "$index_file"
    for file in "$subdir"/*.html; do
      [ -e "$file" ] || continue
      filename=$(basename "$file")
      echo "<li><a href=\"$filename\">$filename</a></li>" >> "$index_file"
    done
    for subsubdir in "$subdir"/*/; do
      [ -d "$subsubdir" ] || continue
      subsubdirname=$(basename "$subsubdir")
      echo "<li><a href=\"$subsubdirname/index.html\">$subsubdirname/</a></li>" >> "$index_file"
    done
    echo "</ul></body></html>" >> "$index_file"
  done
}

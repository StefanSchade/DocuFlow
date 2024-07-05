#!/bin/bash

# Function to generate index.html
generate_index() {
  local subdirectories=$1
  local input_dir=$2
  local output_dir=$3

  for subdir in $subdirectories; do
    local index_file="${output_dir}/${subdir}index.html"
    echo "<html><body><h1>Generated Documentation</h1><ul>" > "$index_file"
    
    for file in "$output_dir/$subdir"*.html; do
      filename=$(basename "$file")
      echo "<li><a href=\"$filename\">$filename</a></li>" >> "$index_file"
    done

    echo "</ul></body></html>" >> "$index_file"
  done
}

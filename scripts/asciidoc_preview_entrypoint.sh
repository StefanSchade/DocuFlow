#!/bin/bash

# Log the determined paths
echo
echo "******************************************************************"
echo "$0"
echo "******************************************************************"

# Define the output directory
OUTPUT_DIR=/workspace/target/docs/html
INPUT_DIR=/workspace/docs

# Ensure the output directory exists
mkdir -p $OUTPUT_DIR

# Function to handle SIGINT and SIGTERM signals
cleanup() {
  echo "Received signal, shutting down..."
  kill -s SIGTERM $WATCH_PID
  kill -s SIGTERM $LIVERELOAD_PID
  exit 0
}

trap 'cleanup' SIGINT SIGTERM

# Check if input directory is correctly mounted
echo "Checking if input directory is correctly mounted..."
if [ -d "$INPUT_DIR" ]; then
  echo "$INPUT_DIR exists."
else
  echo "$INPUT_DIR does not exist."
  exit 1
fi

# Input dir
echo "Checking input directory contents before initial conversion..."
ls -la $INPUT_DIR

# Clean the output directory before initial conversion
echo "Cleaning output directory..."
rm -rf $OUTPUT_DIR/*
mkdir -p $OUTPUT_DIR

# Function to generate index.html file with links to all generated HTML files
generate_index() {
  local dir=$1
  local base_path=$2
  local index_file="${OUTPUT_DIR}${base_path}/index.html"

  mkdir -p "$(dirname "$index_file")"

  echo "<html><body><h1>Generated Documentation</h1><ul>" > $index_file

  for entry in "$dir"/*; do
    if [ -d "$entry" ]; then
      local subdir=$(basename "$entry")
      echo "<li><strong><a href=\"${subdir}/index.html\">${subdir}/</a></strong></li>" >> $index_file
      generate_index "$entry" "${base_path}/${subdir}"
    elif [[ "$entry" == *.adoc ]]; then
      local filename=$(basename "${entry%.adoc}.html")
      local relative_path="${base_path}/${filename}"
      mkdir -p "${OUTPUT_DIR}${base_path}"
      asciidoctor -D "${OUTPUT_DIR}${base_path}" "$entry"
      echo "<li><a href=\"$filename\">$filename</a></li>" >> $index_file
    fi
  done

  echo "</ul></body></html>" >> $index_file
}

# Convert all .adoc files to .html initially and generate index.html
echo "Performing initial conversion of .adoc files to .html..."
generate_index $INPUT_DIR ""

# Log the files found
echo "Files found for conversion:"
find $OUTPUT_DIR -name "*.html" -print

# Watch and convert .adoc files to .html
echo "Starting inotifywait to monitor input dir ($INPUT_DIR)..."
inotifywait -m -e modify,create,delete,move -r $INPUT_DIR |
while read path action file; do
  echo "inotifywait detected a change: $path $action $file"
  if [[ "$file" =~ .*\.adoc$ ]]; then
    echo "Change detected: $action $file"
    echo "Converting $path$file to HTML..."
    asciidoctor -D "${OUTPUT_DIR}$(dirname ${path#$INPUT_DIR})" "$path$file"
    
    # Check if file was converted
    HTML_FILE="${OUTPUT_DIR}$(dirname ${path#$INPUT_DIR})/$(basename "${file}" .adoc).html"
    if [ -f "$HTML_FILE" ]; then
      echo "Conversion complete: $HTML_FILE"
      
      # Regenerate the index.html file
      generate_index $INPUT_DIR ""
    else
      echo "Error: Conversion failed for $path$file"
    fi
  elif [[ "$action" == "CREATE" || "$action" == "MOVED_TO" || "$action" == "DELETE" || "$action" == "MOVED_FROM" ]]; then
    echo "Structure change detected: $action $file"
    generate_index $INPUT_DIR ""
  else
    echo "Ignored change: $action $file"
  fi
done &

WATCH_PID=$!

# Start livereloadx to serve the files
cd $OUTPUT_DIR
echo "Current working directory before starting livereloadx: $(pwd)"
echo "Content of output dir"
ls -al
echo "Starting livereloadx..."
livereloadx -s . -p 4000 --verbose &

LIVERELOAD_PID=$!

# Wait for livereloadx to start
sleep 5

# Check if livereloadx is running
if ps -p $LIVERELOAD_PID > /dev/null; then
  echo "livereloadx started successfully."
else
  echo "Error: livereloadx failed to start."
  exit 1
fi

# Adding a test request to see if the livereloadx server is responding correctly
curl -I http://localhost:4000

wait $WATCH_PID

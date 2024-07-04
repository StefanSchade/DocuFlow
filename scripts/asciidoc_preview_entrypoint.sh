#!/bin/bash

# Source and call helper script
source /workspace/scripts/helper/log_helper.sh && log_script_name

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

# Convert all .adoc files to .html initially
echo "Performing initial conversion of .adoc files to .html..."
find $INPUT_DIR -name "*.adoc" -exec asciidoctor -D $OUTPUT_DIR {} \;

# Check if files were generated
echo "Checking if HTML files were generated..."
if [ "$(ls -A $OUTPUT_DIR)" ]; then
  echo "HTML files were generated successfully:"
  ls -la $OUTPUT_DIR
else
  echo "Error: No HTML files were generated."
  exit 1
fi

echo "Initial conversion complete."

# Create an index.html file with links to all generated HTML files
INDEX_FILE="${OUTPUT_DIR}/index.html"
generate_index() {
  echo "<html><body><h1>Generated Documentation</h1><ul>" > $INDEX_FILE
  for file in $OUTPUT_DIR/*.html; do
    filename=$(basename "$file")
    echo "<li><a href=\"$filename\">$filename</a></li>" >> $INDEX_FILE
  done
  echo "</ul></body></html>" >> $INDEX_FILE
}

generate_index

# Log the files found
echo "Files found for conversion:"
find $OUTPUT_DIR -name "*.html" -print

# Watch and convert .adoc files to .html
echo "Starting inotifywait to monitor input dir ($INPUT_DIR)..."
inotifywait -m -e modify,create,delete -r $INPUT_DIR |
while read path action file; do
  echo "inotifywait detected a change: $path $action $file"
  if [[ "$file" =~ .*\.adoc$ ]]; then
    echo "Change detected: $action $file"
    echo "Converting $path$file to HTML..."
    asciidoctor -D $OUTPUT_DIR "$path$file"
    
    # Check if file was converted
    HTML_FILE="${OUTPUT_DIR}/$(basename "${file}" .adoc).html"
    if [ -f "$HTML_FILE" ]; then
      echo "Conversion complete: $HTML_FILE"
      
      # Regenerate the index.html file
      generate_index
    else
      echo "Error: Conversion failed for $path$file"
    fi
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
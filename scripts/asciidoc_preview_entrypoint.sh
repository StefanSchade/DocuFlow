#!/bin/sh

# Convert all .adoc files to .html and watch for changes
watch_and_convert() {
  while inotifywait -e modify,create,delete -r /workspace/docs; do
    find /workspace/docs -name "*.adoc" -exec asciidoctor {} \;
  done
}

# Run the watch_and_convert function in the background
watch_and_convert &

# Start livereloadx to serve the files
cd /workspace/docs
livereloadx -s . -p 4000

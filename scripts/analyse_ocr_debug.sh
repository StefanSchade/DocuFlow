#!/bin/bash

# Check if the filename argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi

# Set the file name from the first argument
FILENAME=$1

# Define the path to the JSON file
JSON_FILE="/workspace/data/ocr_debug/$FILENAME"

# Extract and join the text elements
jq -r '.text | join(" ")' "$JSON_FILE"

# Extract and join the confidence elements
jq -r '[.conf[] | tostring] | join("  ")' "$JSON_FILE"

# Extract and combine text elements with their corresponding confidence
jq -r '[
    .text as $texts | 
    .conf as $confs | 
    range(0; ($texts | length)) | 
    "(" + $texts[.] + " | " + ($confs[.] | tostring) + ")" 
] | join(" ")' "$JSON_FILE"

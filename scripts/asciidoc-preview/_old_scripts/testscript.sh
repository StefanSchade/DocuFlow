#!/bin/bash

  INPUT_DIR=~/Documents/test

  # Setup a directory for testing
  mkdir -p "$INPUT_DIR/lower_level/"
  echo "demo file" > "$INPUT_DIR/lower_level/demofile.txt"

  # Test section: Watch the lower_level directory and touch the test file
  echo "Testing inotifywait with a lower-level directory..."
  (
    inotifywait -r -e modify,create,delete,move -m "$INPUT_DIR" 2>&1 |
    while read -r path action file; do
      echo "Test Handling change: action $action | path $path | file $file"
    done
  ) &

  TEST_PID=$!

  # Touch the test file to trigger inotifywait
  sleep 1
  touch "$INPUT_DIR/lower_level/demofile.txt"

  # Allow some time for the test to complete
  sleep 5

  # Kill the test inotifywait process
  kill $TEST_PID

  echo "inotifywait test completed. Proceeding to the main inotifywait setup."
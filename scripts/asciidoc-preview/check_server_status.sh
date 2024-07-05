#!/bin/bash

check_server_status() {
  if ps -p $LIVERELOAD_PID > /dev/null; then
    echo "livereloadx is running."
  else
    echo "Error: livereloadx is not running."
    exit 1
  fi
}

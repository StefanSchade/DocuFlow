#!/bin/bash

LOG_FILE="your_log_file.log"
MAX_SIZE=$((5 * 1024 * 1024))  # 5 MB
LOG_LEVEL="INFO"

log() {
    local level=$1
    shift
    local message=$@
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    declare -A levels=( ["ERROR"]=0 ["WARN"]=1 ["INFO"]=2 ["DEBUG"]=3 )
    if (( ${levels[$level]} <= ${levels[$LOG_LEVEL]} )); then
        echo "$timestamp [$level] $message" >> "$LOG_FILE"
    fi

    # Check log file size and rotate if necessary
    local file_size=$(stat -c%s "$LOG_FILE")
    if (( file_size > MAX_SIZE )); then
        tail -c $MAX_SIZE "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
    fi
}

# Set desired log level (e.g., INFO, DEBUG, ERROR)
LOG_LEVEL="DEBUG"

# Usage examples
log "INFO" "This is an info message."
log "ERROR" "This is an error message."
log "DEBUG" "This is a debug message."
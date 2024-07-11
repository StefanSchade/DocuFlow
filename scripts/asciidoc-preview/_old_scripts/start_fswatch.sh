#!/bin/bash

start_fswatch() {
  echo "Setting up fswatch on $INPUT_DIR" >&2

  # Run fswatch with detailed logging
  fswatch -0 -r -e ".*" -i "\\.adoc$" "$INPUT_DIR" 2>&1 |
  while read -r -d "" event; do
    echo "fswatch event detected: $event" >&2
    handle_fswatch_event "$event"
  done
}

handle_fswatch_event() {
  local event=$1

  # Log the raw event
  echo "Raw event: $event" >&2

  local path action file
  path=$(dirname "$event")
  file=$(basename "$event")
  action="MODIFY"

  # Determine action based on the existence and type of the event target
  if [ ! -e "$event" ]; then
    action="DELETE"
  elif [ -d "$event" ]; then
    action="CREATE,ISDIR"
  fi

  # Log the parsed event details
  echo "Handling change: action $action | path $path | file $file" >&2

  case "$action" in
    MODIFY|CREATE)
      if [[ "$file" =~ \.adoc$ ]]; then
        handle_adoc_change "$path" "$file"
      fi
      ;;
    DELETE)
      if [[ "$file" =~ \.adoc$ ]]; then
        handle_adoc_deletion "$path" "$file"
      fi
      ;;
    MOVED_TO|MOVED_FROM)
      if [[ "$file" =~ \.adoc$ ]]; then
        handle_adoc_rename "$path" "$file"
      fi
      ;;
    CREATE,ISDIR|DELETE,ISDIR|MOVED_TO,ISDIR|MOVED_FROM,ISDIR)
      handle_directory_change "$path"
      ;;
  esac
}
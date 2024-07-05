#!/bin/bash

start_inotifywait() {
  inotifywait -m -e modify,create,delete,move -r "$INPUT_DIR" |
  while read -r path action file; do
    handle_inotify_event "$path" "$action" "$file"
  done
}

handle_inotify_event() {
  local path=$1
  local action=$2
  local file=$3

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

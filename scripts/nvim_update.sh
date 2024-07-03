#!/bin/bash

# Source and call helper script
source /workspace/scripts/helper/log_helper.sh && log_script_name

# Check if a configuration name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <config-name>"
    exit 1
fi

CONFIG_NAME=$1
SOURCE_PATH="/workspace/config/nvim-$CONFIG_NAME"
DEST_PATH="/root/.config/nvim"
NVIM_STATE="/root/.local/state/nvim/"

# Check if the source directory exists
if [ ! -d "$SOURCE_PATH" ]; then
    echo "Error: Configuration '$CONFIG_NAME' does not exist at $SOURCE_PATH"
    exit 1
else 
    echo "Configuration '$CONFIG_NAME' found in folder $SOURCE_PATH."
fi

# Check if the destination directory exists and prompt the user for confirmation
if [ -d "$DEST_PATH" ]; then
    echo -e "\e[31mWarning: This will overwrite your existing Neovim configuration in $DEST_PATH. Are you sure? (y/n)\e[0m"
    read -p ">" choice
    case "$choice" in 
      y|Y ) 
        rm -rf $NVIM_STATE/*
        rm -rf $DEST_PATH/*
        cp -r $SOURCE_PATH/* $DEST_PATH
        echo "Neovim configuration replaced in $DEST_PATH"
        ;;
      n|N ) 
        echo "Operation cancelled."
        exit 0
        ;;
      * ) 
        echo "Invalid input. Operation cancelled."
        exit 1
        ;;
    esac
else
    mkdir -p "$DEST_PATH"
    cp -r $SOURCE_PATH/* $DEST_PATH
    echo "Neovim configuration copied to $DEST_PATH"
fi

cp /workspace/config/tmux/tmux.conf ~/.tmux.conf

#gem install neovim

#export PATH="$(ruby -e 'print Gem.user_dir')/bin:$PATH"

tmux source-file ~/.tmux.conf
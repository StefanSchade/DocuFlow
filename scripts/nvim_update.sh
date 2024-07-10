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

export LUA_PATH='/usr/share/lua/5.1/?.lua;/usr/share/lua/5.1/?/init.lua;./?.lua;/usr/share/luajit-2.0.4/?.lua;/usr/local/share/lua/5.1/?.lua;/usr/local/share/lua/5.1/?/init.lua'
export LUA_CPATH='/usr/lib/lua/5.1/?.so;/usr/local/lib/lua/5.1/?.so;./?.so'

echo "abc"

#gem install neovim

#export PATH="$(ruby -e 'print Gem.user_dir')/bin:$PATH"

#mkdir -p /tmp/tmux-0
#chown root:root /tmp/tmux-0
#chmod 755 /tmp/tmux-0


# mkdir -p /tmp/tmux-0
# chown root:root /tmp/tmux-0
# chmod 700 /tmp/tmux-0

# tmux source-file ~/.tmux.conf


# Ensure tmux directory exists with correct permissions

# Ensure tmux directory exists with correct permissions
if [ ! -d /tmp/tmux-0 ]; then
    echo "Creating /tmp/tmux-0 directory"
    mkdir -p /tmp/tmux-0
fi

chown root:root /tmp/tmux-0
chmod 700 /tmp/tmux-0

# Start tmux server
tmux start-server

# Source tmux configuration
if tmux source-file ~/.tmux.conf; then
    echo "tmux configuration sourced successfully"
else
    echo "Failed to source tmux configuration"
fi

# Manually test cloning a repository to ensure connectivity
echo "Testing git clone to ensure connectivity"
if [ -d "/root/.local/share/nvim/lazy/catppuccin" ]; then
    echo "Directory already exists. Skipping git clone."
else
    git clone https://github.com/catppuccin/nvim.git /root/.local/share/nvim/lazy/catppuccin
    if [ $? -ne 0 ]; then
        echo "Git clone failed. Check your network and proxy settings."
        exit 1
    else
        echo "Git clone succeeded."
    fi
fi
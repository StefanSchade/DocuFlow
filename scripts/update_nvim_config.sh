#!/bin/bash

# Define the source and destination paths
SOURCE_PATH="/workspace/.config/nvim"
DEST_PATH="/root/.config/nvim"

# Check if the source directory exists
if [ -d "$SOURCE_PATH" ]; then
    # Copy the Neovim configuration to the destination
    cp -r $SOURCE_PATH/* $DEST_PATH
    echo "Neovim configuration copied to $DEST_PATH"
else
    echo "Source directory $SOURCE_PATH does not exist. Please check the path."
fi

# Install vim-plug if not already installed
if [ ! -f ~/.local/share/nvim/site/autoload/plug.vim ]; then
    echo "Installing vim-plug..."
    curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
        https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    echo "vim-plug installed."
fi

# Provide a message to run :PlugInstall inside nvim
echo "Please run :PlugInstall inside nvim to install plugins."

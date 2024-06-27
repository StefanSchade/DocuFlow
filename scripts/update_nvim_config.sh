#!/bin/bash

# Define the source and destination paths
SOURCE_PATH="/workspace/.config/nvim_"
DEST_PATH="/root/.config/nvim"

# Check if the source directory exists
if [ -d "$SOURCE_PATH" ]; then
    # Ensure the destination directory exists
    mkdir -p "$DEST_PATH"
    
    # Copy the Neovim configuration to the destination
    cp -r "$SOURCE_PATH"/* "$DEST_PATH"
    echo "Neovim configuration copied to $DEST_PATH"
else
    echo "Source directory $SOURCE_PATH does not exist. Please check the path."
fi

# Install vim-plug if not already installed
if [ ! -f ~/.local/share/nvim/site/autoload/plug.vim ]; then
    echo "Installing vim-plug for Neovim..."
    sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
fi

# Install Python LSP server
pip3 install -U setuptools pip
pip3 install 'python-lsp-server[all]'

# Provide a message to run :PlugInstall inside nvim
echo "Please run :PlugInstall inside nvim to install plugins."
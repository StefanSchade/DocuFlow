#!/bin/bash

# Source and call helper script
source /workspace/scripts/helper/log_helper.sh && log_script_name

# Install neovim gem
gem install neovim

# Update PATH for Ruby gems
GEM_USER_DIR=$(ruby -e "puts Gem.user_dir")
echo 'export PATH="$GEM_USER_DIR/bin:$PATH"' >> ~/.bashrc

# Reload bashrc to update PATH
source ~/.bashrc

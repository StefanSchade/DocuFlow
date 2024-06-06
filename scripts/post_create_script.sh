#!/bin/bash

# some output for troubleshooting
ls -la /workspace/scripts

# Retrieve the Git user and email from command-line arguments
GIT_USER="$1"
GIT_EMAIL="$2"

# configure git
git config --global user.name "$GIT_USER"
git config --global user.email "$GIT_EMAIL"

git config --list

# make sure scripts are executable
chmod +x /workspace/scripts/*.sh

# execute scripts
source /workspace/scripts/setup_docker_proxy.sh 
source /workspace/scripts/install_python_dependencies.sh

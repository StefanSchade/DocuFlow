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
source /workspace/scripts/setup_ssh_git.sh 
source /workspace/scripts/setup_docker_proxy.sh 
source /workspace/scripts/install_python_dependencies.sh

# Check for ZScaler certificate and add to CA store if it exists
CERT_PATH="/workspace/zscaler.crt"
if [ -f "$CERT_PATH" ]; then
    echo "ZScaler certificate found. Adding to CA store."
    mkdir -p /usr/local/share/custom-ca-certificates
    cp $CERT_PATH /usr/local/share/custom-ca-certificates/zscaler.crt
    c_rehash /usr/local/share/custom-ca-certificates
    echo "CApath = /usr/local/share/custom-ca-certificates" >> /etc/ssl/openssl.cnf
    echo "ZScaler certificate added to CA store."
else
    echo "ZScaler certificate not found. Skipping CA store update."
fi

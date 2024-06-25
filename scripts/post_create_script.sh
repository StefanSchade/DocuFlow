#!/bin/bash

# Some output for troubleshooting
ls -la /workspace/scripts

# Retrieve the Git user and email from command-line arguments
GIT_USER="$1"
GIT_EMAIL="$2"

# Configure Git with the provided user name and email
git config --global user.name "$GIT_USER"
git config --global user.email "$GIT_EMAIL"

# Display the current Git configuration
git config --list

# Make sure scripts are executable
chmod +x /workspace/scripts/*.sh

# Execute additional setup scripts
source /workspace/scripts/setup_ssh_git.sh 
source /workspace/scripts/setup_docker_proxy.sh 
# redundant, as already in Dockerfile.dev
# source /workspace/scripts/install_python_dependencies.sh

# Check for ZScaler certificate and add to default CA store if it exists
CERT_PATH="/workspace/zscaler.crt"

if [ -f "$CERT_PATH" ]; then
    echo "ZScaler certificate found. Adding to default CA store."

    # Copy the ZScaler certificate to the system CA directory
    cp $CERT_PATH /usr/local/share/ca-certificates/zscaler.crt

    # Ensure the certificate has correct permissions
    chmod 644 /usr/local/share/ca-certificates/zscaler.crt

    # Update the CA certificates
    update-ca-certificates --fresh

    echo "ZScaler certificate added to default CA store."
else
    echo "ZScaler certificate not found. Skipping CA store update."
fi

echo "The following Python packages are installed:"
pip list

# setting env variables

echo 'export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata' >> ~/.bashrc
echo 'export TESSDATA_PREFIX=/usr/local/Cellar/tesseract/4.00/share/tessdata' >> ~/.zshrc

# setting up aliases

echo 'alias update_nvim="~/workspace/update_nvim_config.sh' >> ~/.bashrc
echo 'alias update_nvim="~/workspace/update_nvim_config.sh' >> ~/.zshrc


#!/bin/bash

echo "Script started."

# Some output for troubleshooting
ls -la /workspace/scripts

echo "Checking the necessary env variables"
# Check if GIT_USER and GIT_EMAIL and REPO_ROOT are set
if [ -z "$GIT_USER" ]; then
  echo "Error: GIT_USER is not set. Exiting."
  exit 1
else
  echo "GIT_USER is set to: $GIT_USER"
fi

if [ -z "$GIT_EMAIL" ]; then
  echo "Error: GIT_EMAIL is not set. Exiting."
  exit 1
else
  echo "GIT_EMAIL is set to: $GIT_EMAIL"
fi

if [ -z "$REPO_ROOT" ]; then
  echo "Error: REPO_ROOT is not set. Exiting."
  exit 1
else
  echo "REPO_ROOT is set to: $REPO_ROOT"
fi

if [ -z "$HOST_HOME" ]; then
  echo "Error: HOST_HOME is not set. Exiting."
  exit 1
else
  echo "HOST_HOME is set to: $HOST_HOME"
fi

if [ -z "$REPO_NAME" ]; then
  echo "Error: REPO_NAME is not set. We will try to determin this from the git setup."
else
  echo "REPO_NAME is set to: $REPO_NAME"
fi

# Configure Git with the provided user name and email
echo "Configuring Git with user: $GIT_USER and email: $GIT_EMAIL"
git config --global user.name "$GIT_USER"
git config --global user.email "$GIT_EMAIL"

# Display the current Git configuration
echo "Current Git configuration:"
git config --list

# Make sure scripts are executable
echo "Making sure all scripts in /workspace/scripts are executable."
chmod +x /workspace/scripts/*.sh

# Execute additional setup scripts
echo "Executing setup_ssh_git.sh"
source /workspace/scripts/setup_ssh_git.sh || { echo "Failed to execute setup_ssh_git.sh"; exit 1; }

echo "Executing setup_docker_proxy.sh"
source /workspace/scripts/setup_docker_proxy.sh || { echo "Failed to execute setup_docker_proxy.sh"; exit 1; }

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

# Setting environment variables
echo 'export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata' >> ~/.bashrc
echo 'export TESSDATA_PREFIX=/usr/local/Cellar/tesseract/4.00/share/tessdata' >> ~/.zshrc

# Setting up aliases
echo 'alias update_nvim="~/workspace/update_nvim_config.sh"' >> ~/.bashrc
echo 'alias update_nvim="~/workspace/update_nvim_config.sh"' >> ~/.zshrc

# Function to get the repository name from the Git remote URL
get_repo_name_from_git() {
  git remote get-url origin | sed 's#.*/\([^/]*\)\.git#\1#'
}

# Check if REPO_NAME is already set
if [ -z "$REPO_NAME" ]; then
  REPO_NAME=$(get_repo_name_from_git)
  if [ -z "$REPO_NAME" ]; then
    echo "Error: REPO_NAME could not be determined from Git. Exiting."
    exit 1
  fi
  echo "Setting REPO_NAME environment variable to: $REPO_NAME"
  echo "export REPO_NAME=$REPO_NAME" >> ~/.bashrc
  source ~/.bashrc
else
  echo "REPO_NAME is already set to: $REPO_NAME"
fi

# Logging environment variables
echo "Environment variables:"
echo "REPO_ROOT: $REPO_ROOT"
echo "REPO_NAME: $REPO_NAME"
echo "HOME: $HOME"

echo "Script completed."

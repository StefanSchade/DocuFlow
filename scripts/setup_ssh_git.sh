#!/bin/bash

# Start the SSH agent
eval "$(ssh-agent -s)"

# Fix permissions of the private key files
chmod 600 /root/.ssh/*_rsa

# Fix permissions of the .ssh/config file if it exists
if [ -f /root/.ssh/config ]; then
    chmod 600 /root/.ssh/config
fi

# Add all SSH keys to the agent
for key in /root/.ssh/*_rsa; do
    ssh-add $key
done

# Remove the offending key for GitHub from known_hosts
ssh-keygen -f "/root/.ssh/known_hosts" -R "github.com"

# Add GitHub's new RSA key to known_hosts
ssh-keyscan -t rsa github.com >> /root/.ssh/known_hosts

# List all identities added to the SSH agent
echo "SSH Identities:"
ssh-add -l

# Print the contents of the known_hosts file for debugging
echo "Known Hosts:"
cat /root/.ssh/known_hosts

# Test the SSH connection to GitHub (optional, can be removed if not needed)
ssh -T git@github.com || true  # Add || true to avoid script failure

# Docker setup
echo "Setting up Docker repository and GPG key..."

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

# Add Docker’s official APT repository
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

# Update the package index
apt-get update

# Install Docker
apt-get install -y docker-ce docker-ce-cli containerd.io

# Print Docker version
docker --version

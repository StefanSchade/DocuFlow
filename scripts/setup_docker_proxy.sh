#!/bin/bash

# Ensure we are in the correct working directory
cd /workspace

# Example proxy settings (replace with actual proxy information)
HTTP_PROXY="http://your.proxy.address:8080"
HTTPS_PROXY="http://your.proxy.address:8080"
NO_PROXY="localhost,127.0.0.1"

# Export proxy settings for the Docker build process
export http_proxy=$HTTP_PROXY
export https_proxy=$HTTPS_PROXY
export no_proxy=$NO_PROXY

# Path to the Zscaler certificate in the workspace directory
CERT_PATH="/workspace/zscaler.crt"

# Copy the Zscaler certificate to the appropriate directory
cp $CERT_PATH /usr/local/share/ca-certificates/zscaler.crt

# Update CA certificates
update-ca-certificates

# Verify the certificate installation
ls -l /etc/ssl/certs/ca-certificates.crt

# Configure Git to use the updated CA certificates
git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt

# Verify Git configuration
git config --global --get http.sslCAInfo

echo "Proxy and certificate setup completed successfully."

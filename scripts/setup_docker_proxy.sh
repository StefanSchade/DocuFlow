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

# Verify proxy settings
echo "Proxy settings applied: http_proxy=$http_proxy, https_proxy=$https_proxy, no_proxy=$no_proxy"

# Check for the custom CA certificates path in OpenSSL configuration
if ! grep -q "CApath = /usr/local/share/custom-ca-certificates" /etc/ssl/openssl.cnf; then
    echo "Custom CApath not found in OpenSSL configuration. Adding it."
    echo "CApath = /usr/local/share/custom-ca-certificates" >> /etc/ssl/openssl.cnf
else
    echo "Custom CApath already present in OpenSSL configuration."
fi

# Verify the certificate installation
openssl s_client -CApath /usr/local/share/custom-ca-certificates -connect github.com:443

# Configure Git to use the updated CA certificates
git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt

# Verify Git configuration
git config --global --get http.sslCAInfo

echo "Proxy and certificate setup completed successfully."

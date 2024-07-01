# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y \
    asciidoctor \
    nodejs \
    npm \
    inotify-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install livereloadx
RUN npm install -g livereloadx

# Copy the entrypoint script into the container
COPY entrypoint_asciidoc_preview.sh /usr/local/bin/entrypoint_asciidoc_preview.sh
RUN chmod +x /usr/local/bin/entrypoint_asciidoc_preview.sh

# Set the working directory for the project
WORKDIR /workspace

# Use the entrypoint script
ENTRYPOINT ["entrypoint_asciidoc_preview.sh"]

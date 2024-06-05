#!/bin/bash

# Ensure we are in the correct working directory
cd /workspace

# Activate the virtual environment
source /workspace/venv/bin/activate

# Install Python dependencies from requirements.txt
pip install --no-cache-dir -r /workspace/requirements.txt

# List installed packages to verify installation
pip list

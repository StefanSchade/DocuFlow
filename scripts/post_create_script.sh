#!/bin/bash

# some output for trouble shooting
ls -la /workspace/scripts

# configure git
git config --global user.name 'Stefan Schade'
git config --global user.email 'dr_stefan_schade@yahoo.com'

# make sure scripts are executable
chmod +x /workspace/scripts/*.sh

# execute scripts
source /workspace/scripts/setup_docker_proxy.sh 
source /workspace/scripts/install_python_dependencies.sh
#!/bin/bash

# Create directories if they do not exist
mkdir -p ./shared-workspace
mkdir -p ./data/delta_lake

# Set permissions for the directories
chmod -R 777 ./shared-workspace
chmod -R 777 ./data/delta_lake

echo "Directories and permissions set successfully."

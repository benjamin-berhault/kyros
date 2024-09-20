#!/bin/bash

# Path to the .env file
ENV_FILE=".env-using-local-registry"

# Get the IP address of docker0 interface (the host IP inside Docker)
CONTAINER_IP=$(ip addr show docker0 | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1)

# If the IP address was found, update the BASE_URL_JARS in .env
if [[ -n "$CONTAINER_IP" ]]; then
    NEW_BASE_URL_JARS="${CONTAINER_IP}:5001/jars/"
    sed -i "s|^BASE_URL_JARS=.*|BASE_URL_JARS=${NEW_BASE_URL_JARS}|" $ENV_FILE
    echo "Updated BASE_URL_JARS to: ${NEW_BASE_URL_JARS}"
else
    echo "Could not retrieve IP for docker0 interface"
fi

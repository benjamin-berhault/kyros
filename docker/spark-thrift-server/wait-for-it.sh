#!/bin/bash

host_port=$1

# Check if the host and port are provided
if [ -z "$host_port" ]; then
  echo "Error: No host:port provided"
  exit 1
fi

# Split host and port
host=$(echo $host_port | cut -d':' -f1)
port=$(echo $host_port | cut -d':' -f2)

# Check if the port is provided
if [ -z "$port" ]; then
  echo "Error: No port provided"
  exit 1
fi

# Wait for the service to be available
while ! nc -z $host $port; do
  echo "Waiting for $host:$port..."
  sleep 2
done

# Shift the first argument (host:port) to allow execution of the remaining command
shift

# Execute the command passed as arguments
exec "$@"

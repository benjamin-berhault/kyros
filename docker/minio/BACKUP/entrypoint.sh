#!/bin/sh

# Set MinIO environment variable to prevent redirection
export MINIO_BROWSER_REDIRECT="off"

# Start MinIO server in the background
/usr/local/bin/minio server /data --console-address ":9001" &

# Start Nginx in the foreground
nginx -g 'daemon off;'

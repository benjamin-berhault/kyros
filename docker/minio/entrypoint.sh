#!/bin/bash

# Start MinIO server in the background
export MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
export MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
minio server /data --address ":9000" --console-address ":9001" &

# Start Nginx in the foreground
nginx -g 'daemon off;'
#nginx -g "add_header X-Frame-Options SAMEORIGIN;"

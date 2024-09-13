#!/bin/sh

# Debug: print the MINIO_HOST value
echo "MINIO_HOST is set to: $MINIO_HOST"

# Wait until MinIO is reachable, ignoring AccessDenied errors
while ! curl -s $MINIO_HOST > /dev/null; do
  echo "Waiting for MinIO server at $MINIO_HOST..."
  sleep 5
done

# Configure MinIO client with the specified host and credentials
mc alias set myminio "$MINIO_HOST" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"

# Split the BUCKET_NAMES environment variable by commas and loop through each bucket name
for bucket in $(echo "$BUCKET_NAMES" | tr ',' ' '); do
  # Check if the bucket exists, if not, create it and set public policy
  if mc ls myminio/"$bucket" &>/dev/null; then
    echo "Bucket '$bucket' already exists. Skipping creation."
  else
    mc mb myminio/"$bucket"
    # Set anonymous download policy (public access)
    mc anonymous set download myminio/"$bucket"
    echo "Bucket '$bucket' created and public access enabled."
  fi
done

# Keep the container alive
tail -f /dev/null

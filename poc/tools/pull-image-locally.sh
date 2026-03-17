#!/bin/sh

# Registry address
REGISTRY="localhost:5000"

# Function to extract valid images from docker-compose.yml
extract_images() {

  # Extract only lines containing 'image' and ensure they contain valid image names
  IMAGES=$(grep -E '^\s*(image|IMAGE):\s' docker-compose.yml | awk '{gsub(/\$\{IF_USING_LOCAL_REGISTRY\}/, ""); print $2}' | grep -E '^[a-zA-Z0-9._/-]+(:[a-zA-Z0-9._-]+)?$')

  if [ -z "$IMAGES" ]; then
    echo "No valid images found in docker-compose.yml"
    exit 1
  fi

  echo "$IMAGES"
}

# Check if arguments are provided
if [ "$#" -lt 1 ]; then
  # No arguments, extract images from docker-compose.yml
  IMAGES=$(extract_images)
  echo "Images to process: $IMAGES"
else
  # Use provided arguments as image names
  IMAGES="$@"
fi

# Iterate over all images
for IMAGE in $IMAGES
do
  # Validate that the image reference is not empty or invalid
  if [ -z "$IMAGE" ]; then
    echo "Invalid or empty image reference. Skipping..."
    continue
  fi

  echo "Processing image: $IMAGE"

  # Pull the image from Docker Hub
  docker pull "$IMAGE"

  # Check if the pull was successful
  if [ $? -ne 0 ]; then
    echo "Error: Failed to pull image $IMAGE. Skipping..."
    continue
  fi

  # Tag the image for the local registry
  docker tag "$IMAGE" "$REGISTRY/$IMAGE"

  # Push the tagged image to the local registry
  docker push "$REGISTRY/$IMAGE"

  echo "Image $IMAGE has been successfully pushed to $REGISTRY"
done

#!/bin/sh

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# File that contains the list of JAR URLs or paths
JARS_FILE="$SCRIPT_DIR/tools/jars.txt"

# Directory where JARs will be downloaded
JAR_DIR="./docker/local-registry/jars"

# Function to display help message
display_help() {
  echo "Usage: sudo ./tools/pull-jars-locally.sh"
  echo
  echo "This script downloads JAR files listed in jars.txt and saves them into the specified directory."
  echo
  echo "Options:"
  echo "  -h, --help     Show this help message and exit."
  echo
  echo "Requirements:"
  echo "  - This script requires sudo privileges to run."
  echo "  - jars.txt must contain valid URLs or paths to JAR files, one per line."
  echo
  echo "Example jars.txt content:"
  echo "  https://example.com/path/to/library1.jar"
  echo "  https://example.com/path/to/library2.jar"
  echo
  exit 0
}

# Check if -h or --help is passed as argument
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  display_help
fi

# Check if jars.txt exists
if [ ! -f "$JARS_FILE" ]; then
  echo "Error: $JARS_FILE not found!"
  exit 1
fi

# Create the base JAR directory if it doesn't exist
if [ ! -d "$JAR_DIR" ]; then
  echo "Creating directory: $JAR_DIR"
  mkdir -p "$JAR_DIR"
fi

# Download each JAR listed in jars.txt
while IFS= read -r JAR_URL
do
  # Parse the full path from the URL, excluding the protocol (e.g., https://)
  JAR_PATH=$(echo "$JAR_URL" | sed -e 's|^[^/]*//||')

  # Get the directory path (without the filename) from the JAR URL
  JAR_SUBDIR=$(dirname "$JAR_PATH")

  # Full directory path where the JAR will be saved
  FULL_JAR_DIR="$JAR_DIR/$JAR_SUBDIR"

  # Create the necessary subdirectories if they don't exist
  if [ ! -d "$FULL_JAR_DIR" ]; then
    echo "Creating directory: $FULL_JAR_DIR"
    mkdir -p "$FULL_JAR_DIR"
  fi

  # Get the JAR file name
  JAR_NAME=$(basename "$JAR_URL")

  # Full path where the JAR will be saved
  FULL_JAR_PATH="$FULL_JAR_DIR/$JAR_NAME"

  # Download the JAR if not already present
  if [ ! -f "$FULL_JAR_PATH" ]; then
    echo "Downloading $JAR_NAME to $FULL_JAR_PATH..."
    curl -L -o "$FULL_JAR_PATH" "$JAR_URL"
  else
    echo "$JAR_NAME already exists in $FULL_JAR_DIR, skipping download."
  fi
done < "$JARS_FILE"

echo "All JARs processed."

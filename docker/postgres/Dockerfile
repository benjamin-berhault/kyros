# Use the official PostgreSQL image as the base image
ARG IMAGE=postgres:16.4
FROM ${IMAGE}

# Create the sparkuser with a specific UID and GID
RUN groupadd -g 1001 sparkgroup && \
    useradd -m -u 1001 -g sparkgroup -s /bin/bash sparkuser

# Add the initialization script to create the sparkuser
COPY init-db.sh /docker-entrypoint-initdb.d/

# Set the permissions for the script
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh


# Use Debian as the base image
FROM debian:latest

# Install necessary packages
RUN apt-get update && \
    apt-get install -y wget gnupg2 ca-certificates nginx net-tools curl && \
    rm -rf /var/lib/apt/lists/*

# Install MinIO
RUN wget https://dl.min.io/server/minio/release/linux-amd64/minio && \
    chmod +x minio && \
    mv minio /usr/local/bin/

# Copy the custom MinIO binary to the image
#COPY minio/minio /usr/local/bin/minio

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose Nginx port (public port)
EXPOSE 9003

# Expose MinIO console port (if needed)
EXPOSE 9001

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
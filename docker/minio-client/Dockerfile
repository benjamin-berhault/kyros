# Use Alpine as the base image
ARG IMAGE=alpine:3.18
FROM ${IMAGE}

# Install curl and MinIO client (mc)
RUN apk --no-cache add curl && \
    curl -O https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/local/bin/mc

# Define build-time arguments
ARG MINIO_HOST
ARG MINIO_ACCESS_KEY
ARG MINIO_SECRET_KEY
ARG BUCKET_NAMES

# Create an entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

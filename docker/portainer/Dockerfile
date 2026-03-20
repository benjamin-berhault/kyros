# Base image is Alpine Linux
FROM alpine:3.20

# Set environment variables
ENV PORTAINER_VERSION=2.21.1

# Install curl and ca-certificates, create the /portainer directory, and download Portainer
RUN apk add --no-cache curl ca-certificates && \
    mkdir -p /portainer && \
    curl -L https://github.com/portainer/portainer/releases/download/${PORTAINER_VERSION}/portainer-${PORTAINER_VERSION}-linux-amd64.tar.gz | tar -xz -C /portainer

# Expose the default Portainer port
EXPOSE 9000

# Set the bcrypt hashed password for the admin user, hash from 'your_password'
ENV ADMIN_PASSWORD_HASH='$2b$12$EdeGFjVKDc0FImNkF1xXhOiM5xdFc21jvmBUfZzUQV3ol9B.Xf16C'

# Set the entrypoint to run Portainer and initialize the admin user
ENTRYPOINT ["/bin/sh", "-c", "/portainer/portainer/portainer --admin-password $ADMIN_PASSWORD_HASH"]

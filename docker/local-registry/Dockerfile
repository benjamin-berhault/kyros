# Use an Alpine base image to keep the container lightweight
ARG IMAGE=alpine:3.16
FROM ${IMAGE}

# Install necessary dependencies: nginx, Docker registry, and supervisor
RUN apk add --no-cache nginx docker-registry supervisor openssl

# Create directories for Docker registry, JAR storage, and SSL certificates
RUN mkdir -p /var/lib/registry /usr/share/nginx/html/jars /var/log/supervisor /etc/nginx/certs

# Set write permissions for the /usr/share/nginx/html/jars directory
RUN chmod -R 777 /usr/share/nginx/html/jars

# Copy SSL certificates (self-signed or from a CA)
COPY server.crt /etc/nginx/certs/server.crt
COPY server.key /etc/nginx/certs/server.key

# Copy default nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the registry configuration file
COPY config.yml /etc/docker/registry/config.yml

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisord.conf

# Expose port 5000 for HTTPS
EXPOSE 5000 5001

# Start both services using supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]

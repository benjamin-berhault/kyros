# Use an official Python runtime as a base image
FROM python:3.9-slim

# Install Nginx
RUN apt-get update && apt-get install -y nginx curl && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose port 80 for Nginx
EXPOSE 5005

# Set the entrypoint to run both Nginx and the Flask app
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

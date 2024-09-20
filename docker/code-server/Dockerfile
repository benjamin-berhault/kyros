# Dockerfile for code-server

# Use the official code-server base image
FROM codercom/code-server:latest

# Set environment variables
ENV PASSWORD=yourpassword 

# Install Docker CLI and other dependencies for Debian (bullseye)
RUN sudo apt-get update --allow-releaseinfo-change && sudo apt-get install -y \
    git \
    build-essential \
    curl \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/*

# Create the docker group and add the coder user to it
RUN sudo groupadd docker && sudo usermod -aG docker coder

# Add Docker’s official GPG key
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the Docker repository for Debian bullseye (Debian 11)
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bullseye stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker CLI
RUN sudo apt-get update && sudo apt-get install -y docker-ce-cli

# Install additional VSCode extensions (optional)
RUN code-server --install-extension ms-python.python \
    && code-server --install-extension ms-toolsai.jupyter \
    && code-server --install-extension esbenp.prettier-vscode

# Copy custom user settings (optional)
COPY settings.json /home/coder/.local/share/code-server/User/settings.json

# Ensure directory exists
RUN mkdir -p /home/coder/project/code-server

# Set working directory
WORKDIR /home/coder/project/code-server

# Expose the default port for code-server (8080)
EXPOSE 8080

# Start code-server
CMD ["code-server", "--bind-addr", "0.0.0.0:8080"]

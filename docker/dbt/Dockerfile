# Use a minimal Alpine image with Python
FROM python:3.10-alpine

# Set the working directory (optional)
WORKDIR /usr/app/dbt

# Install dependencies, SSH server, and dbt
RUN apk add --no-cache gcc musl-dev postgresql-dev libffi-dev openssl-dev python3-dev cargo openssh \
    && pip install --upgrade pip \
    && pip install dbt-core dbt-postgres

# Create a new user
RUN adduser -D -s /bin/sh -u 1000 myuser \
    && echo "myuser:mysecurepassword" | chpasswd

# Configure SSH to allow password login and root login
RUN ssh-keygen -A \
    && echo "PermitRootLogin yes" >> /etc/ssh/sshd_config \
    && echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]
#ssh root@172.20.0.3
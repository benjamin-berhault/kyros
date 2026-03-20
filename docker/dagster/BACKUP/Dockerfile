# Use the official Python image as a base
ARG IMAGE=python:3.10-slim
FROM ${IMAGE}

# Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /opt/dagster/app/

# Set the working directory
WORKDIR /opt/dagster/app

# Install Python packages
RUN pip install -r requirements.txt

# Set environment variable for Dagster home
ENV DAGSTER_HOME=/opt/dagster/dagster_home

# Ensure the DAGSTER_HOME directory exists
RUN mkdir -p ${DAGSTER_HOME}

# Expose the port Dagster webserver runs on
EXPOSE 3000

# Command to start Dagster webserver
ENTRYPOINT ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]

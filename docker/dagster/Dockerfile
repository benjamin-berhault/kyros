# Use the official Python image as a base
FROM python:3.9-slim

# Copy and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set environment variable
ENV DAGSTER_HOME=/opt/dagster

# Copy contents of the test directory to /opt/dagster/
COPY dagster/. /opt/dagster/

# Expose the port Dagster webserver runs on
EXPOSE 3000

# Keep the container running for investigation purposes
#CMD ["tail", "-f", "/dev/null"]
CMD ["dagster-webserver", "-w", "/opt/dagster/workspace.yaml", "-h", "0.0.0.0"]

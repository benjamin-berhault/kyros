# Use the official Trino image as the base
FROM trinodb/trino:latest

# Set environment variables if needed
ENV JAVA_TOOL_OPTIONS=-Xmx4g

# Create the necessary directories for Trino configuration
RUN mkdir -p /etc/trino/catalog

# Copy your custom configurations into the container
COPY ./catalog/hive.properties /etc/trino/catalog/hive.properties

# Expose Trino web UI port (optional if you want to access Trino UI)
EXPOSE 8080

# Start the Trino server
ENTRYPOINT ["trino"]

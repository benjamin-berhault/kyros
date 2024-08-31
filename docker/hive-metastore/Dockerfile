# Use the Apache Hive 4.0.0 base image
FROM apache/hive:4.0.0

# Switch to root to create the sparkuser and sparkgroup
USER root

# Create the sparkuser with a specific UID and GID
RUN groupadd -g 1001 sparkgroup && \
    useradd -m -u 1001 -g sparkgroup -s /bin/bash sparkuser

# Switch back to the hive user (or appropriate non-root user if required)
USER hive

# Expose the metastore port
EXPOSE 9083

# Command to start the Hive Metastore service
CMD ["hive", "--service", "metastore"]

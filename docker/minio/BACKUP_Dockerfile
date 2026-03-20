# Use the official MinIO image as the base image
ARG IMAGE=minio/minio:RELEASE.2024-09-09T16-59-28Z
FROM ${IMAGE}

# Create the Hadoop configuration directory
RUN mkdir -p /etc/hadoop/conf

# Copy the Hadoop configuration files into the container
COPY core-site.xml /etc/hadoop/conf/core-site.xml

# Expose the MinIO ports
EXPOSE 9000 9001

# Command to run MinIO server
CMD ["server", "/data", "--console-address", ":9001"]

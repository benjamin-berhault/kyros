# Define the base image to be used
ARG SPARK_BASE_IMAGE=bitnami/spark:3.4.1
FROM ${SPARK_BASE_IMAGE}

# Layer: Image Metadata
ARG build_date

LABEL org.label-schema.build-date=${build_date}
LABEL org.label-schema.description="Spark master image"
LABEL org.label-schema.schema-version="1.0"

# Switch to the root user
USER root

# Create a group and a non-root user (e.g., sparkuser) with a specific user ID
RUN groupadd -g 1001 sparkgroup && \
    useradd -m -s /bin/bash -u 1001 -g sparkgroup sparkuser

# Install additional Python packages, if needed
RUN pip install delta-spark

# Expose necessary ports for the Spark Master
EXPOSE 8080 7077

# Switch back to the non-root user (optional, but recommended for security)
USER sparkuser

# Command to start the Spark Master
CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]

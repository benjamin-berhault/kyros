# Define the base image to be used
ARG SPARK_BASE_IMAGE=bitnami/spark:3.4.1

# Use the provided base image
FROM ${SPARK_BASE_IMAGE}

# Layer: Image Metadata
ARG build_date

LABEL org.label-schema.build-date=${build_date}
LABEL org.label-schema.description="Spark worker image"
LABEL org.label-schema.schema-version="1.0"

# Install additional Python packages, if needed
RUN pip install delta-spark

# Expose necessary ports for the Spark Worker
EXPOSE 8081

# Command to start the Spark Worker
CMD ["sh", "-c", "bin/spark-class org.apache.spark.deploy.worker.Worker spark://${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT}"]

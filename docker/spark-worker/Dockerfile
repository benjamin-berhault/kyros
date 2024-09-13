# Define the base image to be used
ARG IMAGE=bitnami/spark:3.4.1
FROM ${IMAGE}

# Layer: Image Metadata
ARG build_date

LABEL org.label-schema.build-date=${build_date}
LABEL org.label-schema.description="Spark worker image"
LABEL org.label-schema.schema-version="1.0"

# Switch to the root user
USER root

# Create a group and a non-root user (e.g., sparkuser) with a specific user ID
RUN groupadd -g 1001 sparkgroup && \
    useradd -m -s /bin/bash -u 1001 -g sparkgroup sparkuser

# Install additional Python packages, if needed
RUN pip install delta-spark

# Create the core-site.xml file and add the hadoop.security.group.mapping property
RUN mkdir -p /opt/bitnami/spark/conf && \
    echo '<?xml version="1.0" encoding="UTF-8"?>' > /opt/bitnami/spark/conf/core-site.xml && \
    echo '<configuration>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '  <property>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '    <name>hadoop.security.group.mapping</name>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '    <value>org.apache.hadoop.security.ShellBasedUnixGroupsMapping</value>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '  </property>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '  <property>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '    <name>hadoop.security.group.mapping.fallback</name>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '    <value>true</value>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '  </property>' >> /opt/bitnami/spark/conf/core-site.xml && \
    echo '</configuration>' >> /opt/bitnami/spark/conf/core-site.xml

# Expose necessary ports for the Spark Worker
EXPOSE 8081

# Switch back to the non-root user (optional, but recommended for security)
USER sparkuser

# Command to start the Spark Worker
CMD ["sh", "-c", "bin/spark-class org.apache.spark.deploy.worker.Worker spark://${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT}"]

# Use a base image that includes Spark
ARG IMAGE=apache/spark:3.4.1
FROM ${IMAGE}

# Set environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install required packages
USER root
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /opt/spark/logs

# Create symbolic links for the entire sbin and bin directories
RUN ln -s /opt/bitnami/spark/sbin /opt/spark/sbin && \
    ln -s /opt/bitnami/spark/bin /opt/spark/bin

# Add Delta Lake JAR
RUN wget https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar -P $SPARK_HOME/jars/

# Set ownership of logs directory
RUN chown -R 1001:1001 /opt/spark/logs

# Switch back to non-root user if necessary (usually it's the same user used in the base image)
USER 1001

# Set the working directory
WORKDIR /opt/spark

# Start the Thrift server
CMD ${SPARK_HOME}/sbin/start-thriftserver.sh \
    --master spark://${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT} \
    --hiveconf hive.server2.thrift.bind.host=0.0.0.0 \
    --hiveconf hive.server2.thrift.port=10000 \
    --hiveconf hive.metastore.uris=thrift://hive-metastore:9083 \
    --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
    --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog

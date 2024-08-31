# Use a base image that includes Spark
ARG IMAGE=apache/spark:3.4.1
FROM ${IMAGE}

# Set environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install required packages
USER root
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a group and a non-root user (e.g., sparkuser) with a specific user ID
RUN groupadd -g 1001 sparkgroup && \
    useradd -m -s /bin/bash -u 1001 -g sparkgroup sparkuser

# Create necessary directories
RUN mkdir -p /opt/spark/logs /home/sparkuser/delta_lake

# Create symbolic links for the entire sbin and bin directories
RUN ln -s /opt/bitnami/spark/sbin /opt/spark/sbin && \
    ln -s /opt/bitnami/spark/bin /opt/spark/bin

# Add Delta Lake JARs and Hadoop client JAR
RUN wget https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar -P $SPARK_HOME/jars/ && \
    wget https://repo1.maven.org/maven2/io/delta/delta-storage/2.4.0/delta-storage-2.4.0.jar -P $SPARK_HOME/jars/ && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/3.3.1/hadoop-client-3.3.1.jar -P $SPARK_HOME/jars/

# Set ownership of necessary directories to the non-root user
RUN chown -R sparkuser:sparkgroup /opt/spark /home/sparkuser && \
    [ -d /opt/hadoop ] && chown -R sparkuser:sparkgroup /opt/hadoop || echo "/opt/hadoop does not exist"

# Copy core-site.xml into the appropriate location
COPY core-site.xml /opt/spark/conf/core-site.xml

# Add a wait-for-it style bash script to check the service availability
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Set ownership of Spark directories to sparkuser
RUN chown -R sparkuser:sparkgroup /opt/spark /home/sparkuser

# Switch to the sparkuser
USER sparkuser

# Set the working directory
WORKDIR /opt/spark

# Start the Thrift server after ensuring that both spark-master and hive-metastore are reachable
CMD /usr/local/bin/wait-for-it.sh ${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT} -- \
    /usr/local/bin/wait-for-it.sh hive-metastore:9083 -- \
    ${SPARK_HOME}/sbin/start-thriftserver.sh \
    --master spark://${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT} \
    --hiveconf hive.server2.thrift.bind.host=0.0.0.0 \
    --hiveconf hive.server2.thrift.port=10000 \
    --hiveconf hive.metastore.uris=thrift://hive-metastore:9083 \
    --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
    --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
    --conf spark.delta.logStore.class=org.apache.spark.sql.delta.storage.HDFSLogStore \
    --conf spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/opt/spark/conf/log4j.properties \
    --conf spark.executor.extraJavaOptions=-Dlog4j.configuration=file:/opt/spark/conf/log4j.properties

# Use the official Trino image as the base
ARG IMAGE=trinodb/trino:455
FROM ${IMAGE}

# Define build argument for local JARs URL
ARG BASE_URL_JARS
ENV BASE_URL_JARS=${BASE_URL_JARS}

# Switch to root user to install packages and make necessary changes
USER root

# Install wget using microdnf
RUN microdnf install -y wget findutils nano && microdnf clean all

# Set environment variables if needed
ENV JAVA_TOOL_OPTIONS="-Xmx4g"
ENV AWS_JAVA_V1_DISABLE_DEPRECATION_ANNOUNCEMENT=true
ENV AWS_JAVA_V1_PRINT_LOCATION=true

# Create the necessary directories for Trino configuration
RUN mkdir -p /etc/trino

# Copy configuration files into the container
COPY etc /etc/trino/

COPY check /home/trino/
#RUN javac /home/trino/CheckS3AFileSystem.java

#COPY trino.sh /etc/profile.d/trino.sh
#RUN chmod +x /etc/profile.d/trino.sh

# Add a custom entry point script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# If the core-site.xml file is not present in your MinIO setup, 
# it’s important to note that MinIO itself doesn’t require or 
# use Hadoop configuration files like core-site.xml. 
# Instead, core-site.xml is relevant when you are configuring 
# Hadoop or Hadoop-compatible tools (like Trino) to interact with 
# S3 or S3-compatible storage systems such as MinIO.
# Ensure that Hadoop configuration is accessible
ENV HADOOP_CONF_DIR=/etc/trino/hadoop-conf

# Add the required JAR files for S3 support
RUN mkdir -p /usr/lib/trino/plugin/hive

RUN wget ${BASE_URL_JARS}repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.2.0/hadoop-common-3.2.0.jar -P /usr/lib/trino/plugin/hive/ 
RUN wget ${BASE_URL_JARS}repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.2.0/hadoop-common-3.2.0.jar -P /usr/lib/trino/plugin/hive/ 
RUN wget ${BASE_URL_JARS}repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.770/aws-java-sdk-bundle-1.12.770.jar -P /usr/lib/trino/plugin/hive/ 


#RUN wget ${BASE_URL_JARS}repo1.maven.org/maven2/io/trino/trino-server-dev/455/trino-server-dev-455.jar -P /usr/lib/trino/lib/
#RUN wget ${BASE_URL_JARS}repo1.maven.org/maven2/io/trino/trino-server/455/trino-server-455.jar -P /usr/lib/trino/lib/

# Switch back to the original user
USER trino

# Expose Trino web UI port
EXPOSE 8080

# Start the Trino server explicitly
# Set the entry point to the custom script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]

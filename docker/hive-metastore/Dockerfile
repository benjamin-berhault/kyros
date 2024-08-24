# Use Apache Hive as the base image for Hive Metastore
FROM apache/hive:4.0.0

ENV SERVICE_METASTORE_PORT 9083
ENV HIVE_METASTORE_USER metastore_user
ENV HIVE_METASTORE_PASSWORD metastore_password

# Switch to root user to install dependencies
USER root

# Install wget if not already installed
RUN apt-get update && apt-get install -y wget

# Download the PostgreSQL JDBC driver
RUN wget -q https://jdbc.postgresql.org/download/postgresql-42.2.25.jar -P /opt/hive/lib

# Ensure the driver has the right permissions
RUN chmod 644 /opt/hive/lib/postgresql-42.2.25.jar

# Switch back to the hive user
USER hive

# Copy the hive-site.xml configuration file
COPY config/hive-site.xml /opt/hive/conf/hive-site.xml

# Expose the Hive Metastore port
EXPOSE 9083

# Command to keep the container alive without starting Hive Metastore
CMD ["tail", "-f", "/dev/null"]
# Command to start the Hive Metastore service
#CMD ["hive", "--service", "metastore", "-dbType", "postgres"]


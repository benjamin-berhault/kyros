# Use the Apache Hive 4.0.0 base image
FROM apache/hive:4.0.0

# Switch to root to perform administrative tasks
USER root

# Update package lists and install wget
RUN apt-get update && \
    apt-get install -y wget nano

# Create the sparkuser with a specific UID and GID
RUN groupadd -g 1001 sparkgroup && \
    useradd -m -u 1001 -g sparkgroup -s /bin/bash sparkuser

# Download the PostgreSQL JDBC driver and place it in the Hive lib directory
RUN wget https://jdbc.postgresql.org/download/postgresql-42.5.4.jar -O /opt/hive/lib/postgresql-42.5.4.jar

# # Copy the custom hive-site.xml to the container
COPY hive-site.xml /opt/hive/conf/hive-site.xml

# Add a script to check if hive-site.xml is configured correctly
RUN bash -c "\
    if grep -q 'jdbc:postgresql://postgres:5432/metastore' /opt/hive/conf/hive-site.xml && \
       grep -q 'org.postgresql.Driver' /opt/hive/conf/hive-site.xml && \
       grep -q 'hive.metastore.db.type' /opt/hive/conf/hive-site.xml && \
       grep -q 'postgres' /opt/hive/conf/hive-site.xml; \
    then \
        echo 'hive-site.xml is configured correctly for PostgreSQL'; \
    else \
        echo 'hive-site.xml configuration is incorrect or not properly replaced'; \
        exit 1; \
    fi"

# # Switch back to the hive user
USER hive

# # Expose the metastore port
EXPOSE 9083


# Initialize the schema (if needed), but continue even if it fails because can already exists
# Initialize the schema (if needed), but continue even if it fails because it might already exist
RUN echo "Starting schema initialization" && \
    schematool -dbType postgres -initSchema -verbose || true && \
    echo "Schema initialization complete"

# Override the ENTRYPOINT to disable the base image's entrypoint script: ENTRYPOINT ["sh" "-c" "/entrypoint.sh"]  
#ENTRYPOINT ["tail", "-f", "/dev/null"]

# Start the Hive Metastore service
ENTRYPOINT ["hive", "--service", "metastore"]

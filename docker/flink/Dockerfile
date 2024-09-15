ARG IMAGE=flink:1.17.0-scala_2.12-java11
FROM ${IMAGE}

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Python 3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir apache-flink numpy

# Set Python 3 as the default python
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN wget -P /opt/flink/lib https://repo1.maven.org/maven2/com/ververica/flink-sql-connector-postgres-cdc/2.3.0/flink-sql-connector-postgres-cdc-2.3.0.jar
RUN wget -P /opt/flink/lib https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.0/flink-sql-connector-kafka-1.17.0.jar

# Set the working directory
WORKDIR /opt/flink

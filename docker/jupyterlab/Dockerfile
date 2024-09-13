# Base image for JupyterLab with Python
ARG IMAGE=jupyter/base-notebook:latest
FROM ${IMAGE}

# -- Layer: Image Metadata

ARG build_date

LABEL org.label-schema.build-date=${build_date}
LABEL org.label-schema.name="Data Engineering with Apache Spark and Delta Lake Cookbook - JupyterLab Image"
LABEL org.label-schema.description="JupyterLab image"

# Switch to root to install Java and other dependencies
USER root

RUN apt-get update && apt-get install -y openjdk-11-jdk netcat

# Switch back to the original user (jovyan for Jupyter base images)
USER ${NB_USER}

# -- Layer: JupyterLab + Python kernel for PySpark and Iceberg

# Define build arguments with default values
ARG spark_version=3.4.1
ARG jupyterlab_version=4.2.4
ARG sparksql_magic_version=0.0.3
ARG kafka_python_version=2.0.2
ARG iceberg_version=1.2.0

RUN pip3 install --no-cache-dir wget==3.2 \
    pandas \
    pyarrow \
    pyspark==${spark_version} \
    jupyterlab==${jupyterlab_version} \
    sparksql-magic==${sparksql_magic_version} \
    kafka-python==${kafka_python_version} \
    delta-spark

# Download Delta Lake JAR
RUN wget -qO- https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar -P $SPARK_HOME/jars/

# Download Apache Iceberg JARs for Spark
RUN wget -qO- https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.3_2.12/${iceberg_version}/iceberg-spark-runtime-3.3_2.12-${iceberg_version}.jar -P $SPARK_HOME/jars/

# Set up Java environment variables
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

# Ensure shared workspace and delta lake directories have the correct ownership and permissions
USER root
RUN mkdir -p /home/jovyan/work /home/jovyan/delta_lake /home/jovyan/parquet /home/jovyan/iceberg && \
    chown -R jovyan:users /home/jovyan/work /home/jovyan/delta_lake /home/jovyan/parquet /home/jovyan/iceberg && \
    chmod -R 770 /home/jovyan/work && \
    chmod -R 777 /home/jovyan/delta_lake /home/jovyan/parquet /home/jovyan/iceberg

# Switch back to the original user
USER jovyan

# Copy a Jupyter configuration file (optional)
COPY jupyter_notebook_config.py /home/jovyan/.jupyter/

# Expose JupyterLab port
EXPOSE 8888

# Set working directory (ensure SHARED_WORKSPACE is defined or use a fallback)
ENV SHARED_WORKSPACE="/home/jovyan"
WORKDIR ${SHARED_WORKSPACE}

# Command to wait for Spark master and then start JupyterLab
CMD ["/bin/bash", "-c", "while ! nc -z spark-master 7077; do echo 'Waiting for Spark master...'; sleep 2; done; jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.disable_check_xsrf=True"]

#CMD ["/bin/bash", "-c", "while ! nc -z spark-master 7077; do echo 'Waiting for Spark master...'; sleep 2; done; jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''"]

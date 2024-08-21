ARG BASE_IMAGE=jupyter/base-notebook:latest
FROM ${BASE_IMAGE}

# -- Layer: Image Metadata

ARG build_date

LABEL org.label-schema.build-date=${build_date}
LABEL org.label-schema.name="Data Engineering with Apache Spark and Delta Lake Cookbook - JupyterLab Image"
LABEL org.label-schema.description="JupyterLab image"

# Switch to root to install Java
USER root

RUN apt-get update && apt-get install -y openjdk-11-jdk

# Switch back to the original user (jovyan for Jupyter base images)
USER ${NB_USER}

# -- Layer: JupyterLab + Python kernel for PySpark

# Define build arguments with default values
ARG spark_version=3.4.1
ARG jupyterlab_version=3.0.16
ARG sparksql_magic_version=0.0.3
ARG kafka_python_version=2.0.2

RUN pip3 install --no-cache-dir wget==3.2 \
    pyspark==${spark_version} \
    jupyterlab==${jupyterlab_version} \
    sparksql-magic==${sparksql_magic_version} \
    kafka-python==${kafka_python_version}

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

EXPOSE 8888

WORKDIR ${SHARED_WORKSPACE}
CMD jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=;python

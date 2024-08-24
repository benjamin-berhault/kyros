ARG SPARK_BASE_IMAGE=bitnami/spark:3.4.1
FROM ${SPARK_BASE_IMAGE}

# -- Layer: Image Metadata

ARG build_date

LABEL org.label-schema.build-date=${build_date}
LABEL org.label-schema.description="Spark master image"
LABEL org.label-schema.schema-version="1.0"

# In docker/spark-master/Dockerfile
RUN pip install delta-spark

EXPOSE 8080 7077

# -- Command to Start the Spark Master
CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]

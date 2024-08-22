ARG SPARK_BASE_IMAGE
FROM ${SPARK_BASE_IMAGE}

# -- Layer: Image Metadata

ARG build_date

LABEL org.label-schema.build-date=${build_date}
LABEL org.label-schema.description="Spark worker image"
LABEL org.label-schema.schema-version="1.0"

# -- Expose Ports for Spark Worker
EXPOSE 8081

# -- Command to Start the Spark Worker
CMD bin/spark-class org.apache.spark.deploy.worker.Worker spark://${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT}

ARG SPARK_BASE_IMAGE
FROM ${SPARK_BASE_IMAGE}

# -- Layer: Image Metadata

ARG build_date

LABEL org.label-schema.build-date=${build_date}
LABEL org.label-schema.description="Spark master image"
LABEL org.label-schema.schema-version="1.0"

# -- Runtime

EXPOSE 8080 7077

# -- Command to Start the Spark Master
CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]

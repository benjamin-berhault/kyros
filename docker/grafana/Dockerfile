ARG IMAGE=grafana/grafana:main
FROM $IMAGE

# Set metadata for this image
LABEL maintainer="TO-FILL"

# Switch to root to perform administrative tasks
USER root

# Install the Kafka data source plugin using grafana-cli
RUN grafana-cli plugins install hamedkarbasi93-kafka-datasource

# Create necessary directories
RUN mkdir -p /etc/grafana/provisioning/dashboards
RUN mkdir -p /var/lib/grafana/dashboards

# Expose Grafana's port
EXPOSE 3000

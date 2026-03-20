# Use the official SQLPad image
ARG IMAGE=sqlpad/sqlpad:7.5.0
FROM ${IMAGE}

# Copy the connections.json file to the appropriate directory
COPY connections.json /var/lib/sqlpad/connections.json

# Expose the port SQLPad will run on
EXPOSE 3001

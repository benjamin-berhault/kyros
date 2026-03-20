#!/bin/bash

echo "Starting schema initialization"
schematool -dbType postgres -initSchema -verbose || echo "Schema initialization might have already been done."
echo "Schema initialization complete"

# Start Hive Metastore service
hive --service metastore

#!/bin/bash

# Set up the environment
export JAVA_TOOL_OPTIONS="-Xmx4g"
export ETC_DIR=/etc/trino
export INSTALL_PATH=/usr/lib/trino
export DATA_DIR=/usr/lib/trino/var

# # Expand the classpath to include all JARs in the directories
# CLASSPATH=$(find /usr/lib/trino/lib /usr/lib/trino/plugin/hive -name '*.jar' | tr '\n' ':')

# # Ensure JARs are in the classpath
# export CLASSPATH

# Logging the classpath for debugging
echo "Classpath: $CLASSPATH"

# Check if config.properties exists
if [ ! -f "$ETC_DIR/config.properties" ]; then
  echo "Config file is missing: $ETC_DIR/config.properties"
  exit 1
fi

# Start the Trino server
exec $INSTALL_PATH/bin/launcher run --etc-dir $ETC_DIR


#tail -f /dev/null

# Now call the original entry point to start Trino
# Example of an entry point script with the correct classpath
#export CLASSPATH="/usr/lib/trino/lib/*"
#exec java $JAVA_TOOL_OPTIONS -cp $CLASSPATH io.trino.server.TrinoServer "$@"

#exec /usr/lib/trino/bin/run-trino
#java -cp /usr/lib/trino/lib/trino-server-maicd n-455.jar:/usr/lib/trino/plugin/hive/guava-33.3.0-jre.jar:/usr/lib/trino/plugin/hive/* io.trino.server.TrinoServer


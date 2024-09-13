for container in spark-master spark-worker-1 spark-worker-2 hive-metastore spark-thrift-server; do
  echo "Checking $container"
  
  # Define an array with the config file names to search
  config_files=("core-site.xml" "hive-site.xml")

  for config_file in "${config_files[@]}"; do
    # Find the configuration file
    file_path=$(docker exec -it $container bash -c "find / -name '$config_file' 2>/dev/null | head -n 1")
    
    if [ -n "$file_path" ]; then
      # Trim any potential leading or trailing whitespace/newlines from the path
      file_path=$(echo $file_path | tr -d '\r' | tr -d '\n')
      
      # Check for the hadoop.security.group.mapping property
      echo "Found $config_file at $file_path"
      docker exec -it $container bash -c "grep -A 2 'hadoop.security.group.mapping' $file_path || echo 'Property not set in $file_path'"
    else
      echo "$config_file not found in $container"
    fi
  done
  
  echo ""
done

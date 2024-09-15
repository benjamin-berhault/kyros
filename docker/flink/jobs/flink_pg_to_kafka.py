import configparser
import os
from pyflink.table import EnvironmentSettings, TableEnvironment

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('/opt/flink/jobs/config.ini')

# Debug: Print the content of the config file
print(f"Sections: {config.sections()}")

# Access the configuration values
try:
    BOOTSTRAP_SERVERS = config['kafka']['bootstrap_servers']
    OUTPUT_KAFKA_TOPIC = config['kafka']['output_topic']
except KeyError as e:
    print(f"Error: {e}")
    raise

env_settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(env_settings)

# Define the source table
t_env.execute_sql("""
    CREATE TABLE shipments (
        shipment_id INT,
        order_id INT,
        origin STRING,
        destination STRING,
        is_arrived BOOLEAN,
        db_name STRING METADATA FROM 'database_name' VIRTUAL,
        operation_ts TIMESTAMP_LTZ(3) METADATA FROM 'op_ts' VIRTUAL,
        PRIMARY KEY (shipment_id) NOT ENFORCED
    ) WITH (
        'connector' = 'postgres-cdc',
        'hostname' = 'postgres',
        'port' = '5432',
        'username' = 'postgres',
        'password' = 'postgres',
        'database-name' = 'postgres',
        'schema-name' = 'public',
        'table-name' = 'shipments'
    )
""")

# Define the sink table
t_env.execute_sql(f"""
    CREATE TABLE shipments_output_upsert (
        shipment_id INT,
        order_id INT,
        origin STRING,
        destination STRING,
        is_arrived BOOLEAN,
        db_name STRING,
        operation_ts TIMESTAMP_LTZ(3),
        PRIMARY KEY (shipment_id) NOT ENFORCED
    ) WITH (
        'connector' = 'upsert-kafka',
        'topic' = '{OUTPUT_KAFKA_TOPIC}',
        'properties.bootstrap.servers' = '{BOOTSTRAP_SERVERS}',
        'key.format' = 'json',
        'value.format' = 'json'
    )
""")

# 'topic' = 'shipments',
# 'properties.bootstrap.servers' = 'redpanda:29092',

# Perform the insertion
t_env.execute_sql("INSERT INTO shipments_output_upsert SELECT * FROM shipments")

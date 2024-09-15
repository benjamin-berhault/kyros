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
    KAFKA_SOURCE_TOPIC = config['kafka']['source_topic']
except KeyError as e:
    print(f"Error: Missing configuration for {e}")
    raise

env_settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(env_settings)

# Define the Kafka source table
t_env.execute_sql(f"""
    CREATE TABLE kafka_source (
        LCLid STRING,
        tstp TIMESTAMP(3),
        `energy(kWh/hh)` FLOAT,
        `price_p/kWh` FLOAT,
        tariff_type STRING,
        WATERMARK FOR tstp AS tstp - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = '{KAFKA_SOURCE_TOPIC}',
        'properties.bootstrap.servers' = '{BOOTSTRAP_SERVERS}',
        'properties.group.id' = 'flink_consumer',
        'format' = 'json',
        'scan.startup.mode' = 'earliest-offset',
        'json.timestamp-format.standard' = 'ISO-8601'
    )
""")

# Define the sink table
t_env.execute_sql(f"""
    CREATE TABLE energy_aggregates (
        LCLid STRING,
        start_time TIMESTAMP(3),
        end_time TIMESTAMP(3),
        min_energy FLOAT,
        max_energy FLOAT,
        avg_energy FLOAT,
        PRIMARY KEY (LCLid, start_time) NOT ENFORCED
    ) WITH (
        'connector' = 'upsert-kafka',
        'topic' = '{OUTPUT_KAFKA_TOPIC}',
        'properties.bootstrap.servers' = '{BOOTSTRAP_SERVERS}',
        'key.format' = 'json',
        'value.format' = 'json'
    )
""")

# Insert query
t_env.execute_sql(f"""
    INSERT INTO energy_aggregates
    SELECT
        LCLid,
        TUMBLE_START(tstp, INTERVAL '1' HOUR) AS start_time,
        TUMBLE_END(tstp, INTERVAL '1' HOUR) AS end_time,
        MIN(`energy(kWh/hh)`) AS min_energy,
        MAX(`energy(kWh/hh)`) AS max_energy,
        AVG(`energy(kWh/hh)`) AS avg_energy
    FROM kafka_source
    GROUP BY
        TUMBLE(tstp, INTERVAL '1' HOUR),
        LCLid
""")

print("Job executed successfully.")

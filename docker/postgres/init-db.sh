#!/bin/bash
set -e  # Stop script on any error

# Create the metastore user and database
echo "Creating the metastore user and database..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $METASTORE_USER WITH PASSWORD '$METASTORE_PASSWORD';
    CREATE DATABASE $METASTORE_DB;
    GRANT ALL PRIVILEGES ON DATABASE $METASTORE_DB TO $METASTORE_USER;
    -- Change the owner of the public schema to the metastore user
    \c $METASTORE_DB
    ALTER SCHEMA public OWNER TO $METASTORE_USER;
EOSQL

echo "Metastore user and database created successfully."

# Create the Spark user and grant privileges
echo "Creating the spark user and granting privileges..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $SPARK_USER WITH PASSWORD '$SPARK_PASSWORD';
    -- Grant access to the metastore database for the spark user
    GRANT ALL PRIVILEGES ON DATABASE $METASTORE_DB TO $SPARK_USER;
EOSQL

echo "Spark user created and privileges granted successfully."

# Create the Dagster and Flink users, databases, and grant privileges
echo "Setting up Dagster and Flink users and databases..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Existing Dagster user setup
    DROP ROLE IF EXISTS $DAGSTER_ROLE;
    CREATE ROLE $DAGSTER_ROLE WITH LOGIN PASSWORD '$DAGSTER_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE $DAGSTER_DB TO $DAGSTER_ROLE;

    -- New Flink catalog database and user setup
    --CREATE DATABASE flink_catalog;
    
    --DROP ROLE IF EXISTS flink;
    --CREATE ROLE flink WITH LOGIN PASSWORD 'flink_password';
    --GRANT ALL PRIVILEGES ON DATABASE flink_catalog TO flink;
EOSQL

echo "Dagster and Flink users created and privileges granted successfully."


# # Create the SQLPad user and database
# echo "Creating SQLPad user and database..."

# psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
#     CREATE USER $SQLPAD_USER WITH PASSWORD '$SQLPAD_PASSWORD';
#     CREATE DATABASE $SQLPAD_DB;
#     GRANT ALL PRIVILEGES ON DATABASE $SQLPAD_DB TO $SQLPAD_USER;
#     -- Change the owner of the public schema to the SQLPad user
#     \c $SQLPAD_DB
#     ALTER SCHEMA public OWNER TO $SQLPAD_USER;
# EOSQL

# echo "SQLPad user and database created successfully."

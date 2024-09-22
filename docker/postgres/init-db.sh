#!/bin/bash
set -e  # Stop script on any error

# Function to execute psql commands
execute_psql() {
    local dbname=$1
    local user=$2
    shift 2
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$dbname" "$@"
}

# Create the metastore user and database
echo "Creating the metastore user and database..."

execute_psql "$POSTGRES_DB" "$POSTGRES_USER" <<-EOSQL
    CREATE USER $METASTORE_USER WITH PASSWORD '$METASTORE_PASSWORD';
    CREATE DATABASE $METASTORE_DB;
    GRANT ALL PRIVILEGES ON DATABASE $METASTORE_DB TO $METASTORE_USER;
    -- Create a dedicated schema for metastore
    \c $METASTORE_DB
    CREATE SCHEMA IF NOT EXISTS metastore AUTHORIZATION $METASTORE_USER;
EOSQL

echo "Metastore user and database created successfully."

# Create the Spark user and grant privileges
echo "Creating the spark user and granting privileges..."

execute_psql "$POSTGRES_DB" "$POSTGRES_USER" <<-EOSQL
    CREATE USER $SPARK_USER WITH PASSWORD '$SPARK_PASSWORD';
    -- Grant access to the metastore database for the spark user
    GRANT ALL PRIVILEGES ON DATABASE $METASTORE_DB TO $SPARK_USER;
EOSQL

echo "Spark user created and privileges granted successfully."

# Create the Dagster and Flink users, databases, and grant privileges
echo "Setting up Dagster and Flink users and databases..."

execute_psql "$POSTGRES_DB" "$POSTGRES_USER" <<-EOSQL
    -- Create Dagster database and role
    CREATE DATABASE $DAGSTER_DB;
    CREATE ROLE $DAGSTER_ROLE WITH LOGIN PASSWORD '$DAGSTER_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE $DAGSTER_DB TO $DAGSTER_ROLE;

    -- Create a dedicated schema for Dagster
    \c $DAGSTER_DB
    CREATE SCHEMA IF NOT EXISTS dagster AUTHORIZATION $DAGSTER_ROLE;
EOSQL

echo "Dagster and Flink users and databases created and privileges granted successfully."

# Create the Sandpit user, databases, and grant privileges
echo "Setting up Dagster and Flink users and databases..."

execute_psql "$POSTGRES_DB" "$POSTGRES_USER" <<-EOSQL
    -- Create Dagster database and role
    CREATE DATABASE $SANDPIT_DB;
    CREATE ROLE $SANDPIT_USER WITH LOGIN PASSWORD '$SANDPIT_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE $SANDPIT_DB TO $SANDPIT_USER;

    -- Create a dedicated schema for Dagster
    \c $SANDPIT_DB
    CREATE SCHEMA IF NOT EXISTS dagster AUTHORIZATION $SANDPIT_USER;
EOSQL

echo "Dagster and Flink users and databases created and privileges granted successfully."


# # Create the SQLPad user and database
# echo "Creating SQLPad user and database..."

# execute_psql "$POSTGRES_DB" "$POSTGRES_USER" <<-EOSQL
#     CREATE USER $SQLPAD_USER WITH PASSWORD '$SQLPAD_PASSWORD';
#     CREATE DATABASE $SQLPAD_DB;
#     GRANT ALL PRIVILEGES ON DATABASE $SQLPAD_DB TO $SQLPAD_USER;
#     -- Create a dedicated schema for SQLPad
#     \c $SQLPAD_DB
#     CREATE SCHEMA IF NOT EXISTS sqlpad AUTHORIZATION $SQLPAD_USER;
# EOSQL

# echo "SQLPad user and database created successfully."

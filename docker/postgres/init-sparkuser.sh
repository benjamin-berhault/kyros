#!/bin/bash
set -e

# Create the sparkuser and grant privileges
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER sparkuser WITH PASSWORD 'sparkuser_password';
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO sparkuser;
EOSQL

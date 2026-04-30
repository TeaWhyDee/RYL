#!/bin/bash

# Set the database connection details
HOST="localhost"
PORT="5432"
USER="ryl_dev"
PASSWORD="ryl_dev1"
# DB="ryl_test"

# Function to execute a SQL query
function run_sql_query() {
    local query="$1"
    PGPASSWORD="$PASSWORD" psql -h $HOST -p $PORT -U $USER -c "$query"
}

psql -c "DROP DATABASE ryl_test;"
psql -c "CREATE DATABASE ryl_test;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE ryl_test TO ryl_dev;"
psql -c "ALTER DATABASE ryl_test OWNER to ryl_dev;"

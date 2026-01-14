#!/bin/bash

# Set the database connection details
HOST="localhost"
PORT="5432"
USER="ryl_dev"
PASSWORD="ryl_dev1"
DB="ryl_dev"

# Function to execute a SQL query
function run_sql_query() {
    local query="$1"
    PGPASSWORD="$PASSWORD" psql -h $HOST -p $PORT -U $USER -c "$query"
}


# run_sql_query "DROP DATABASE ryl_dev;"
# run_sql_query "CREATE DATABASE ryl_dev;"
# run_sql_query "GRANT ALL PRIVILEGES ON DATABASE ryl_dev TO ryl_dev;"
# run_sql_query "ALTER DATABASE ryl_dev OWNER to ryl_dev;"
psql -c "DROP DATABASE ryl_dev;"
psql -c "CREATE DATABASE ryl_dev;"                             
psql -c "GRANT ALL PRIVILEGES ON DATABASE ryl_dev TO ryl_dev;" 
psql -c "ALTER DATABASE ryl_dev OWNER to ryl_dev;"             






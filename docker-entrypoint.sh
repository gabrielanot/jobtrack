#!/bin/sh

# Default to /app/data/jobtrack.db if DATABASE_PATH is not set
DB_PATH=${DATABASE_PATH:-/app/data/jobtrack.db}
DB_DIR=$(dirname "$DB_PATH")

# Create the directory and the database file if they don't exist
mkdir -p "$DB_DIR"
touch "$DB_PATH"

# Execute the command passed to the script
exec "$@"

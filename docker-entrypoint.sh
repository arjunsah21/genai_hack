#!/bin/bash
set -e

# Run data import script if database is specified
if [ -n "$MARIA_DB" ] && [ -n "$MARIADB_HOST" ]; then
    echo "Waiting for MariaDB to be ready before importing data..."
    sleep 10  # Give MariaDB some time to initialize
    
    echo "Running data import script..."
    python /app/import_data.py
    
    echo "Data import completed"
fi

# Start Streamlit application
echo "Starting Streamlit application..."
streamlit run /app/app.py --server.address=0.0.0.0

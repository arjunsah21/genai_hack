#!/bin/bash

# Path to your virtual environment
VENV_PATH="/home/ekraumj/genai_demo/.myEnv"

# Flask application path and app name
APP_PATH="/home/ekraumj/genai_demo/"  # Adjust this path to where your app.py is located
APP_NAME="app"  # App instance is called `app` in `app.py`

# Port and host configuration
HOST="0.0.0.0"
PORT="8000"

# Number of workers (adjust as needed)
WORKERS=2

# Log file paths
ACCESS_LOG="/home/ekraumj/genai_demo/logs/access.log"
ERROR_LOG="/home/ekraumj/genai_demo/logs/error.log"
PID='/home/ekraumj/genai_demo/logs/pid'

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$ACCESS_LOG")"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Navigate to the app directory
cd "$APP_PATH"

# Run the Flask app with Gunicorn in the background, logging to files
gunicorn --workers $WORKERS --bind $HOST:$PORT $APP_NAME:app --access-logfile $ACCESS_LOG --error-logfile $ERROR_LOG --timeout 0 &

# Store the PID
PID=$!

# Save the PID to a file (optional)
echo $PID > $PID

# Deactivate the virtual environment after starting the server
deactivate

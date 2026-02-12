#!/bin/bash
# Start NAS Control Web Application

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Use virtual environment
source PythonEnv/bin/activate

# Run Flask application
echo "Starting NAS Control on http://0.0.0.0:5000"
python app.py

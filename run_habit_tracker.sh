#!/bin/bash

echo "Starting Habit Tracker..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.7+ using your package manager"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "habit_tracker_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv habit_tracker_env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source habit_tracker_env/bin/activate

# Install requirements if needed
echo "Checking requirements..."
pip install -r requirements.txt --quiet

# Run the application
echo "Starting Habit Tracker application..."
python main.py

# Deactivate virtual environment
deactivate

echo
echo "Application closed."

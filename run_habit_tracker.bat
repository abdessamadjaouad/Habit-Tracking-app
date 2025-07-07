@echo off
echo Starting Habit Tracker...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "habit_tracker_env" (
    echo Creating virtual environment...
    python -m venv habit_tracker_env
)

REM Activate virtual environment
echo Activating virtual environment...
call habit_tracker_env\Scripts\activate.bat

REM Install requirements if needed
echo Checking requirements...
pip install -r requirements.txt --quiet

REM Run the application
echo Starting Habit Tracker application...
python main.py

REM Deactivate virtual environment
deactivate

echo.
echo Application closed.
pause

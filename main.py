#!/usr/bin/env python3
"""
Habit Tracker Desktop Application

A desktop application for tracking daily habits with calendar view and progress charts.
Built with Python, Tkinter, and MySQL.

Author: Your Name
Date: 2025-01-07
"""

import sys
import os
import logging
from tkinter import messagebox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'mysql.connector',
        'matplotlib',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        error_msg = f"Missing required packages: {', '.join(missing_packages)}\n"
        error_msg += "Please install them using: pip install -r requirements.txt"
        print(error_msg)
        return False
    
    return True

def main():
    """Main entry point for the application."""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        from gui import HabitTrackerGUI
        
        # Create and run the application
        app = HabitTrackerGUI()
        app.run()
        
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

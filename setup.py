#!/usr/bin/env python3
"""
Setup script for Habit Tracker application.
This script helps users set up the database configuration and install dependencies.
"""

import os
import sys
import subprocess
import shutil

def install_requirements():
    """Install required Python packages."""
    print("Installing required Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False

def create_config_file():
    """Create configuration file from template."""
    config_template = "config_template.py"
    config_file = "config.py"
    
    if os.path.exists(config_file):
        print(f"✓ {config_file} already exists")
        return True
    
    if os.path.exists(config_template):
        shutil.copy(config_template, config_file)
        print(f"✓ Created {config_file} from template")
        print("  Please edit config.py with your MySQL database settings")
        return True
    else:
        print(f"✗ Template file {config_template} not found")
        return False

def test_mysql_connection():
    """Test if MySQL connector can be imported."""
    try:
        import mysql.connector
        print("✓ MySQL connector is available")
        return True
    except ImportError:
        print("✗ MySQL connector not found")
        print("  Please install it with: pip install mysql-connector-python")
        return False

def check_mysql_server():
    """Check if MySQL server is running (basic check)."""
    print("\n📋 MySQL Server Check:")
    print("  Please ensure MySQL server is running on your system")
    print("  Default connection settings:")
    print("    Host: localhost")
    print("    Port: 3306")
    print("    User: root")
    print("    Database: habit_tracker (will be created automatically)")
    
    response = input("\nIs MySQL server running? (y/n): ").lower().strip()
    return response in ['y', 'yes']

def main():
    """Main setup function."""
    print("🎯 Habit Tracker Setup")
    print("=" * 50)
    
    success = True
    
    # Install requirements
    print("\n1. Installing dependencies...")
    if not install_requirements():
        success = False
    
    # Test MySQL connector
    print("\n2. Checking MySQL connector...")
    if not test_mysql_connection():
        success = False
    
    # Create config file
    print("\n3. Setting up configuration...")
    if not create_config_file():
        success = False
    
    # Check MySQL server
    print("\n4. Checking MySQL server...")
    if not check_mysql_server():
        print("  ⚠️  Please start MySQL server before running the application")
    
    print("\n" + "=" * 50)
    
    if success:
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit config.py with your MySQL database credentials")
        print("2. Ensure MySQL server is running")
        print("3. Run the application: python main.py")
    else:
        print("❌ Setup completed with errors")
        print("Please fix the errors above before running the application")
    
    print("\n📖 For more help, see README.md")

if __name__ == "__main__":
    main()

# Installation Guide for Habit Tracker

## Prerequisites

### 1. Python Installation
- **Windows**: Download Python 3.7+ from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt-get install python3 python3-pip python3-tk`
- **macOS**: `brew install python3 python-tk`

### 2. MySQL Server Installation

#### Windows:
1. Download MySQL Installer from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)
2. Run the installer and choose "Developer Default"
3. Set root password during installation
4. Start MySQL service

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### macOS:
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

## Application Installation

### Step 1: Download the Application
```bash
# If using git
git clone <repository-url>
cd Habit-Tracking-app

# Or download and extract the ZIP file
```

### Step 2: Set Up Python Environment (Recommended)
```bash
# Create virtual environment
python -m venv habit_tracker_env

# Activate virtual environment
# Windows:
habit_tracker_env\Scripts\activate
# Linux/macOS:
source habit_tracker_env/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Step 4: Configure Database
```bash
# Run setup script (recommended)
python setup.py

# Or manually:
# 1. Copy config_template.py to config.py
# 2. Edit config.py with your MySQL settings
```

### Step 5: Test Installation
```bash
# Run test script to verify everything works
python test_app.py
```

### Step 6: Run the Application
```bash
python main.py
```

## Database Configuration

### Default Configuration
The application will try to connect to MySQL with these default settings:
- **Host**: localhost
- **Port**: 3306
- **User**: root
- **Password**: (empty)
- **Database**: habit_tracker (created automatically)

### Custom Configuration
1. Copy `config_template.py` to `config.py`
2. Edit the DATABASE_CONFIG dictionary:
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'habit_tracker',
    'user': 'your_username',
    'password': 'your_password',
    'port': 3306
}
```

### Creating a MySQL User (Optional)
```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create dedicated user for the application
CREATE USER 'habit_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON habit_tracker.* TO 'habit_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Troubleshooting

### Common Issues

#### 1. "mysql.connector not found"
```bash
pip install mysql-connector-python
```

#### 2. "matplotlib not found"
```bash
pip install matplotlib
```

#### 3. "Access denied for user 'root'"
- Reset MySQL root password
- Create a new user with proper permissions
- Check MySQL service is running

#### 4. "Can't connect to MySQL server"
- Verify MySQL service is running:
  - Windows: Check Services (services.msc)
  - Linux: `sudo systemctl status mysql`
  - macOS: `brew services list | grep mysql`

#### 5. GUI Issues
- **Linux**: Install tkinter: `sudo apt-get install python3-tk`
- **Windows**: Tkinter should be included with Python
- **macOS**: Install tkinter: `brew install python-tk`

### Database Issues

#### Reset Database
If you need to reset the database:
```sql
DROP DATABASE habit_tracker;
```
The application will recreate it on next run.

#### Manual Database Creation
```sql
CREATE DATABASE habit_tracker;
USE habit_tracker;

-- Tables will be created automatically by the application
```

### Permission Issues
If you get permission errors:
```bash
# Linux/macOS - run with proper permissions
sudo python main.py

# Or change file permissions
chmod +x main.py
```

## Quick Start Checklist

- [ ] Python 3.7+ installed
- [ ] MySQL Server installed and running
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database configuration set up (`config.py`)
- [ ] Test passed (`python test_app.py`)
- [ ] Application runs (`python main.py`)

## Getting Help

1. **Check logs**: The application logs errors to the console
2. **Run tests**: `python test_app.py` to diagnose issues
3. **Verify setup**: `python setup.py` to check configuration
4. **Check requirements**: Ensure all dependencies are installed
5. **Database access**: Verify MySQL credentials and permissions

## Next Steps

Once installed:
1. **Add your first habit** using the "Add Habit" button
2. **Track daily progress** by checking boxes in the calendar view
3. **View progress charts** in the "Progress Charts" tab
4. **Navigate months** using the arrow buttons

For detailed usage instructions, see the main README.md file.

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import configuration
try:
    from config import DATABASE_CONFIG
except ImportError:
    # Default configuration
    DATABASE_CONFIG = {
        'host': 'localhost',
        'database': 'habit_tracker',
        'user': 'root',
        'password': '',
        'port': 3306
    }
    logger.warning("No config.py found. Using default database configuration.")

class DatabaseManager:
    """Handles all database operations for the habit tracker application."""
    
    def __init__(self, config=None):
        """
        Initialize database connection parameters.
        
        Args:
            config (dict): Database configuration dictionary
        """
        if config is None:
            config = DATABASE_CONFIG
            
        self.host = config.get('host', 'localhost')
        self.database = config.get('database', 'habit_tracker')
        self.user = config.get('user', 'root')
        self.password = config.get('password', '')
        self.port = config.get('port', 3306)
        self.connection = None
        
    def connect(self) -> bool:
        """
        Establish connection to MySQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                cursor.close()
                
                self.connection.database = self.database
                self._create_tables()
                logger.info("Successfully connected to MySQL database")
                return True
            else:
                logger.error("Failed to connect to MySQL database")
                return False
                
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.connection.cursor()
        
        # Create habits table
        create_habits_table = """
        CREATE TABLE IF NOT EXISTS habits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            created_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        )
        """
        
        # Create habit_logs table
        create_logs_table = """
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            habit_id INT NOT NULL,
            completion_date DATE NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
            UNIQUE KEY unique_habit_date (habit_id, completion_date)
        )
        """
        
        try:
            cursor.execute(create_habits_table)
            cursor.execute(create_logs_table)
            self.connection.commit()
            logger.info("Database tables created successfully")
        except Error as e:
            logger.error(f"Error creating tables: {e}")
        finally:
            cursor.close()
    
    def add_habit(self, name: str, description: str = "") -> bool:
        """
        Add a new habit to the database.
        
        Args:
            name (str): Habit name
            description (str): Habit description
            
        Returns:
            bool: True if successful, False otherwise
        """
        cursor = self.connection.cursor()
        
        try:
            query = "INSERT INTO habits (name, description, created_date) VALUES (%s, %s, %s)"
            values = (name, description, date.today())
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"Habit '{name}' added successfully")
            return True
        except Error as e:
            logger.error(f"Error adding habit: {e}")
            return False
        finally:
            cursor.close()
    
    def get_all_habits(self) -> List[Dict]:
        """
        Retrieve all active habits from database.
        
        Returns:
            List[Dict]: List of habit dictionaries
        """
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = "SELECT * FROM habits WHERE is_active = TRUE ORDER BY name"
            cursor.execute(query)
            habits = cursor.fetchall()
            return habits
        except Error as e:
            logger.error(f"Error retrieving habits: {e}")
            return []
        finally:
            cursor.close()
    
    def update_habit(self, habit_id: int, name: str, description: str = "") -> bool:
        """
        Update an existing habit.
        
        Args:
            habit_id (int): Habit ID
            name (str): New habit name
            description (str): New habit description
            
        Returns:
            bool: True if successful, False otherwise
        """
        cursor = self.connection.cursor()
        
        try:
            query = "UPDATE habits SET name = %s, description = %s WHERE id = %s"
            values = (name, description, habit_id)
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"Habit ID {habit_id} updated successfully")
            return True
        except Error as e:
            logger.error(f"Error updating habit: {e}")
            return False
        finally:
            cursor.close()
    
    def delete_habit(self, habit_id: int) -> bool:
        """
        Soft delete a habit (mark as inactive).
        
        Args:
            habit_id (int): Habit ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        cursor = self.connection.cursor()
        
        try:
            query = "UPDATE habits SET is_active = FALSE WHERE id = %s"
            cursor.execute(query, (habit_id,))
            self.connection.commit()
            logger.info(f"Habit ID {habit_id} deleted successfully")
            return True
        except Error as e:
            logger.error(f"Error deleting habit: {e}")
            return False
        finally:
            cursor.close()
    
    def log_habit_completion(self, habit_id: int, completion_date: date, completed: bool) -> bool:
        """
        Log habit completion for a specific date.
        
        Args:
            habit_id (int): Habit ID
            completion_date (date): Date of completion
            completed (bool): Whether habit was completed
            
        Returns:
            bool: True if successful, False otherwise
        """
        cursor = self.connection.cursor()
        
        try:
            query = """
            INSERT INTO habit_logs (habit_id, completion_date, completed) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE completed = %s
            """
            values = (habit_id, completion_date, completed, completed)
            cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            logger.error(f"Error logging habit completion: {e}")
            return False
        finally:
            cursor.close()
    
    def get_habit_logs(self, habit_id: int, start_date: date, end_date: date) -> List[Dict]:
        """
        Get habit completion logs for a date range.
        
        Args:
            habit_id (int): Habit ID
            start_date (date): Start date
            end_date (date): End date
            
        Returns:
            List[Dict]: List of log dictionaries
        """
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = """
            SELECT * FROM habit_logs 
            WHERE habit_id = %s AND completion_date BETWEEN %s AND %s
            ORDER BY completion_date
            """
            values = (habit_id, start_date, end_date)
            cursor.execute(query, values)
            logs = cursor.fetchall()
            return logs
        except Error as e:
            logger.error(f"Error retrieving habit logs: {e}")
            return []
        finally:
            cursor.close()
    
    def get_habit_completion_status(self, habit_id: int, completion_date: date) -> bool:
        """
        Check if a habit was completed on a specific date.
        
        Args:
            habit_id (int): Habit ID
            completion_date (date): Date to check
            
        Returns:
            bool: True if completed, False otherwise
        """
        cursor = self.connection.cursor()
        
        try:
            query = "SELECT completed FROM habit_logs WHERE habit_id = %s AND completion_date = %s"
            cursor.execute(query, (habit_id, completion_date))
            result = cursor.fetchone()
            return result[0] if result else False
        except Error as e:
            logger.error(f"Error checking completion status: {e}")
            return False
        finally:
            cursor.close()
    
    def get_habit_statistics(self, habit_id: int, start_date: date, end_date: date) -> Dict:
        """
        Get statistics for a habit in a date range.
        
        Args:
            habit_id (int): Habit ID
            start_date (date): Start date
            end_date (date): End date
            
        Returns:
            Dict: Statistics dictionary
        """
        logs = self.get_habit_logs(habit_id, start_date, end_date)
        
        total_days = (end_date - start_date).days + 1
        completed_days = sum(1 for log in logs if log['completed'])
        completion_rate = (completed_days / total_days) * 100 if total_days > 0 else 0
        
        # Calculate current streak
        current_streak = 0
        for log in reversed(logs):
            if log['completed']:
                current_streak += 1
            else:
                break
        
        return {
            'total_days': total_days,
            'completed_days': completed_days,
            'completion_rate': completion_rate,
            'current_streak': current_streak
        }
    
    def close_connection(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")

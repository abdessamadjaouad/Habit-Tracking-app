from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import calendar
from database import DatabaseManager

class HabitManager:
    """Business logic for habit tracking operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize HabitManager with database manager.
        
        Args:
            db_manager (DatabaseManager): Database manager instance
        """
        self.db_manager = db_manager
    
    def add_new_habit(self, name: str, description: str = "") -> bool:
        """
        Add a new habit with validation.
        
        Args:
            name (str): Habit name
            description (str): Habit description
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not name or not name.strip():
            return False
        
        # Check if habit already exists
        existing_habits = self.db_manager.get_all_habits()
        for habit in existing_habits:
            if habit['name'].lower() == name.strip().lower():
                return False
        
        return self.db_manager.add_habit(name.strip(), description.strip())
    
    def get_habits(self) -> List[Dict]:
        """Get all active habits."""
        return self.db_manager.get_all_habits()
    
    def update_habit(self, habit_id: int, name: str, description: str = "") -> bool:
        """
        Update habit with validation.
        
        Args:
            habit_id (int): Habit ID
            name (str): New habit name
            description (str): New habit description
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not name or not name.strip():
            return False
        
        return self.db_manager.update_habit(habit_id, name.strip(), description.strip())
    
    def delete_habit(self, habit_id: int) -> bool:
        """
        Delete a habit with validation.
        
        Args:
            habit_id (int): Habit ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.db_manager.delete_habit(habit_id)
    
    def toggle_habit_completion(self, habit_id: int, completion_date: date) -> bool:
        """
        Toggle habit completion status for a specific date.
        
        Args:
            habit_id (int): Habit ID
            completion_date (date): Date to toggle
            
        Returns:
            bool: New completion status
        """
        current_status = self.db_manager.get_habit_completion_status(habit_id, completion_date)
        new_status = not current_status
        
        success = self.db_manager.log_habit_completion(habit_id, completion_date, new_status)
        return new_status if success else current_status
    
    def get_habit_completion_status(self, habit_id: int, completion_date: date) -> bool:
        """Check if habit was completed on a specific date."""
        return self.db_manager.get_habit_completion_status(habit_id, completion_date)
    
    def get_month_data(self, year: int, month: int) -> Dict[int, Dict[str, bool]]:
        """
        Get completion data for all habits for a specific month.
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            Dict: {day: {habit_id: completion_status}}
        """
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        habits = self.get_habits()
        month_data = {}
        
        # Initialize all days in month
        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            month_data[day] = {}
        
        # Get completion data for each habit
        for habit in habits:
            habit_id = habit['id']
            logs = self.db_manager.get_habit_logs(habit_id, start_date, end_date)
            
            # Create a lookup dictionary for logs with proper boolean conversion
            log_dict = {log['completion_date'].day: bool(log['completed']) for log in logs}
            
            # Fill in completion data for each day
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                month_data[day][habit_id] = log_dict.get(day, False)
        
        return month_data
    
    def get_habit_progress_data(self, habit_id: int, year: int, month: int) -> List[Tuple[int, bool]]:
        """
        Get progress data for a habit in a specific month.
        
        Args:
            habit_id (int): Habit ID
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            List[Tuple[int, bool]]: List of (day, completion_status) tuples
        """
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        logs = self.db_manager.get_habit_logs(habit_id, start_date, end_date)
        log_dict = {log['completion_date'].day: log['completed'] for log in logs}
        
        progress_data = []
        for day in range(1, calendar.monthrange(year, month)[1] + 1):
            progress_data.append((day, log_dict.get(day, False)))
        
        return progress_data
    
    def get_habit_statistics(self, habit_id: int, year: int, month: int) -> Dict:
        """Get statistics for a habit in a specific month."""
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        return self.db_manager.get_habit_statistics(habit_id, start_date, end_date)
    
    def get_habit_chart_data(self, habit_id: int, months_back: int = 12) -> List[Dict]:
        """
        Get habit completion data for the last N months for charting.
        
        Args:
            habit_id (int): Habit ID
            months_back (int): Number of months to go back (default: 12)
            
        Returns:
            List[Dict]: List of monthly data with completions and total days
        """
        chart_data = []
        current_date = datetime.now()
        
        for i in range(months_back, 0, -1):
            # Calculate the target month and year
            target_month = current_date.month - i + 1
            target_year = current_date.year
            
            # Handle year rollover
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            # Get the number of days in the target month
            days_in_month = calendar.monthrange(target_year, target_month)[1]
            
            # Get completion data for this month
            start_date = date(target_year, target_month, 1)
            end_date = date(target_year, target_month, days_in_month)
            
            logs = self.db_manager.get_habit_logs(habit_id, start_date, end_date)
            completed_days = sum(1 for log in logs if log['completed'])
            
            # Format month name
            month_name = f"{calendar.month_abbr[target_month]} {target_year}"
            
            chart_data.append({
                'month': month_name,
                'completions': completed_days,
                'total_days': days_in_month,
                'percentage': round((completed_days / days_in_month) * 100, 1) if days_in_month > 0 else 0
            })
        
        return chart_data
    
    def get_habit_by_id(self, habit_id: int) -> Optional[Dict]:
        """
        Get habit by ID.
        
        Args:
            habit_id (int): Habit ID
            
        Returns:
            Optional[Dict]: Habit data or None if not found
        """
        habits = self.get_habits()
        for habit in habits:
            if habit['id'] == habit_id:
                return habit
        return None

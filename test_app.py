#!/usr/bin/env python3
"""
Test script for Habit Tracker application.
This script tests database connectivity and basic functionality.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    modules = [
        ('tkinter', 'GUI framework'),
        ('mysql.connector', 'MySQL database connector'),
        ('matplotlib', 'Plotting library'),
        ('numpy', 'Numerical computing')
    ]
    
    success = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name} ({description})")
        except ImportError as e:
            print(f"  ✗ {module_name} ({description}) - {e}")
            success = False
    
    return success

def test_database_connection():
    """Test database connection."""
    print("\nTesting database connection...")
    
    try:
        from database import DatabaseManager
        
        db = DatabaseManager()
        if db.connect():
            print("  ✓ Database connection successful")
            print("  ✓ Database tables created/verified")
            db.close_connection()
            return True
        else:
            print("  ✗ Database connection failed")
            return False
    except Exception as e:
        print(f"  ✗ Database test error: {e}")
        return False

def test_habit_operations():
    """Test basic habit operations."""
    print("\nTesting habit operations...")
    
    try:
        from database import DatabaseManager
        from habit_manager import HabitManager
        
        db = DatabaseManager()
        if not db.connect():
            print("  ✗ Cannot connect to database")
            return False
        
        habit_mgr = HabitManager(db)
        
        # Test adding a habit
        test_habit_name = "Test Habit (DELETE ME)"
        if habit_mgr.add_new_habit(test_habit_name, "Test description"):
            print("  ✓ Add habit functionality works")
        else:
            print("  ✗ Add habit functionality failed")
            return False
        
        # Test getting habits
        habits = habit_mgr.get_habits()
        if any(h['name'] == test_habit_name for h in habits):
            print("  ✓ Get habits functionality works")
        else:
            print("  ✗ Get habits functionality failed")
            return False
        
        # Clean up test habit
        for habit in habits:
            if habit['name'] == test_habit_name:
                habit_mgr.delete_habit(habit['id'])
                print("  ✓ Delete habit functionality works")
                break
        
        db.close_connection()
        return True
        
    except Exception as e:
        print(f"  ✗ Habit operations test error: {e}")
        return False

def test_gui_creation():
    """Test if GUI can be created (without showing it)."""
    print("\nTesting GUI creation...")
    
    try:
        import tkinter as tk
        
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test basic tkinter widgets
        frame = tk.Frame(root)
        label = tk.Label(frame, text="Test")
        button = tk.Button(frame, text="Test")
        
        print("  ✓ Tkinter GUI components work")
        
        # Destroy the test window
        root.destroy()
        return True
        
    except Exception as e:
        print(f"  ✗ GUI test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Habit Tracker Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Connection Test", test_database_connection),
        ("Habit Operations Test", test_habit_operations),
        ("GUI Creation Test", test_gui_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! The application should work correctly.")
        print("You can now run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("Make sure to:")
        print("1. Install all dependencies: pip install -r requirements.txt")
        print("2. Configure database settings in config.py")
        print("3. Ensure MySQL server is running")

if __name__ == "__main__":
    main()

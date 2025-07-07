#!/usr/bin/env python3
"""
Quick fix script for installation issues
This script installs only the essential packages needed for the Habit Tracker
"""

import subprocess
import sys

def install_package(package_name, description=""):
    """Install a single package with error handling."""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}")
        return False

def test_import(module_name, package_name):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {package_name} is working")
        return True
    except ImportError:
        print(f"❌ {package_name} is not available")
        return False

def main():
    """Main function to fix installation issues."""
    print("🔧 Habit Tracker Quick Fix")
    print("=" * 40)
    
    # Essential packages for the app to work
    essential_packages = [
        ("mysql-connector-python", "mysql.connector", "MySQL Database"),
        ("matplotlib", "matplotlib.pyplot", "Charts and Graphs"),
        ("tkcalendar", "tkcalendar", "Calendar Widget")
    ]
    
    print("\n1. Testing existing packages...")
    missing_packages = []
    
    for package, module, description in essential_packages:
        if not test_import(module, description):
            missing_packages.append((package, description))
    
    if missing_packages:
        print(f"\n2. Installing {len(missing_packages)} missing packages...")
        for package, description in missing_packages:
            install_package(package, description)
    else:
        print("\n✅ All essential packages are already installed!")
    
    # Test if tkinter is available (should be built into Python)
    print("\n3. Testing GUI framework...")
    if test_import("tkinter", "GUI Framework"):
        print("✅ GUI framework is ready")
    else:
        print("❌ GUI framework not available - you may need to install tkinter")
    
    print("\n" + "=" * 40)
    print("🎉 Quick fix complete!")
    print("\nYou should now be able to run:")
    print("   python main.py")
    print("\nNote: Pillow was skipped as it's optional and caused build issues")

if __name__ == "__main__":
    main()

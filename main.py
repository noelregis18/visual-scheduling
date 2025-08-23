#!/usr/bin/env python3
"""
Timetable Management System
A modern, user-friendly application for managing academic timetables.

Author: AI Assistant
Version: 1.0
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the Timetable Management System"""
    try:
        # Import the main application
        from timetable_gui import ModernTimetableApp
        
        # Create and run the application
        app = ModernTimetableApp()
        print("Starting Timetable Management System...")
        print("Features:")
        print("• Create and manage multiple timetables")
        print("• Add, edit, and delete class sessions")
        print("• Subject management with color coding")
        print("• Weekly and daily views")
        print("• Import/Export functionality")
        print("• Modern dark/light theme support")
        print("\nApplication starting...")
        
        app.run()
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install customtkinter pillow tkcalendar")
        sys.exit(1)
    
    except Exception as e:
        print(f"An error occurred while starting the application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

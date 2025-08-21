"""
Data Manager for Timetable Management System
Handles saving and loading timetable data
"""
import json
import os
from pathlib import Path
from typing import List, Optional
from models import Timetable, Subject, ClassSession, TimeSlot

class DataManager:
    """Manages data persistence for the timetable application"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.timetables_file = self.data_dir / "timetables.json"
        self.subjects_file = self.data_dir / "subjects.json"
        self.settings_file = self.data_dir / "settings.json"
    
    def save_timetable(self, timetable: Timetable) -> bool:
        """Save a timetable to file"""
        try:
            timetables = self.load_all_timetables()
            
            # Update existing or add new timetable
            updated = False
            for i, existing in enumerate(timetables):
                if existing['name'] == timetable.name:
                    timetables[i] = timetable.to_dict()
                    updated = True
                    break
            
            if not updated:
                timetables.append(timetable.to_dict())
            
            with open(self.timetables_file, 'w', encoding='utf-8') as f:
                json.dump(timetables, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving timetable: {e}")
            return False
    
    def load_timetable(self, name: str) -> Optional[Timetable]:
        """Load a specific timetable by name"""
        try:
            timetables = self.load_all_timetables()
            for timetable_data in timetables:
                if timetable_data['name'] == name:
                    return Timetable.from_dict(timetable_data)
            return None
        except Exception as e:
            print(f"Error loading timetable: {e}")
            return None
    
    def load_all_timetables(self) -> List[dict]:
        """Load all timetables from file"""
        try:
            if self.timetables_file.exists():
                with open(self.timetables_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading timetables: {e}")
            return []
    
    def get_timetable_names(self) -> List[str]:
        """Get list of all timetable names"""
        try:
            timetables = self.load_all_timetables()
            return [timetable['name'] for timetable in timetables]
        except Exception as e:
            print(f"Error getting timetable names: {e}")
            return []
    
    def delete_timetable(self, name: str) -> bool:
        """Delete a timetable"""
        try:
            timetables = self.load_all_timetables()
            timetables = [t for t in timetables if t['name'] != name]
            
            with open(self.timetables_file, 'w', encoding='utf-8') as f:
                json.dump(timetables, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error deleting timetable: {e}")
            return False
    
    def save_subjects(self, subjects: List[Subject]) -> bool:
        """Save subjects to file"""
        try:
            subjects_data = [
                {
                    'name': subject.name,
                    'code': subject.code,
                    'credits': subject.credits,
                    'instructor': subject.instructor,
                    'color': subject.color
                }
                for subject in subjects
            ]
            
            with open(self.subjects_file, 'w', encoding='utf-8') as f:
                json.dump(subjects_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving subjects: {e}")
            return False
    
    def load_subjects(self) -> List[Subject]:
        """Load subjects from file"""
        try:
            if self.subjects_file.exists():
                with open(self.subjects_file, 'r', encoding='utf-8') as f:
                    subjects_data = json.load(f)
                
                return [Subject(**subject_data) for subject_data in subjects_data]
            return []
        except Exception as e:
            print(f"Error loading subjects: {e}")
            return []
    
    def save_settings(self, settings: dict) -> bool:
        """Save application settings"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_settings(self) -> dict:
        """Load application settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.get_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.get_default_settings()
    
    def get_default_settings(self) -> dict:
        """Get default application settings"""
        return {
            'theme': 'dark',
            'appearance_mode': 'dark',
            'color_theme': 'blue',
            'window_geometry': '1200x800',
            'auto_save': True,
            'show_weekend': False,
            'time_format': '24h',
            'default_session_duration': 60,
            'reminder_enabled': True,
            'reminder_minutes': 15
        }
    
    def export_to_json(self, timetable: Timetable, file_path: str) -> bool:
        """Export timetable to a JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(timetable.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting timetable: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> Optional[Timetable]:
        """Import timetable from a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Timetable.from_dict(data)
        except Exception as e:
            print(f"Error importing timetable: {e}")
            return None
    
    def export_to_csv(self, timetable: Timetable, file_path: str) -> bool:
        """Export timetable to CSV format"""
        try:
            import csv
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Day', 'Time', 'Subject', 'Code', 'Room', 'Type', 'Instructor', 'Notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for session in timetable.sessions:
                    writer.writerow({
                        'Day': session.day,
                        'Time': str(session.time_slot),
                        'Subject': session.subject.name,
                        'Code': session.subject.code,
                        'Room': session.room,
                        'Type': session.session_type,
                        'Instructor': session.subject.instructor,
                        'Notes': session.notes
                    })
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Create a backup of all data"""
        try:
            import shutil
            from datetime import datetime
            
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_{timestamp}.zip"
            
            shutil.make_archive(str(backup_file).replace('.zip', ''), 'zip', self.data_dir)
            
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

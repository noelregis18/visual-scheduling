"""
Data models for the Timetable Management System
"""
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime, time
import json

@dataclass
class TimeSlot:
    """Represents a time slot for a class"""
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"
    
    def __str__(self):
        return f"{self.start_time} - {self.end_time}"

@dataclass
class Subject:
    """Represents a subject/course"""
    name: str
    code: str
    credits: int = 3
    instructor: str = ""
    color: str = "#3b82f6"  # Default blue color
    
    def __str__(self):
        return f"{self.code}: {self.name}"

@dataclass
class ClassSession:
    """Represents a single class session"""
    subject: Subject
    day: str  # Monday, Tuesday, etc.
    time_slot: TimeSlot
    room: str = ""
    session_type: str = "Lecture"  # Lecture, Lab, Tutorial, etc.
    notes: str = ""
    
    def __str__(self):
        return f"{self.subject.name} ({self.time_slot}) - {self.room}"

@dataclass
class Timetable:
    """Main timetable containing all class sessions"""
    name: str
    semester: str
    sessions: List[ClassSession]
    created_date: str
    last_modified: str
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
    
    def add_session(self, session: ClassSession):
        """Add a new class session"""
        self.sessions.append(session)
        self.last_modified = datetime.now().isoformat()
    
    def remove_session(self, session: ClassSession):
        """Remove a class session"""
        if session in self.sessions:
            self.sessions.remove(session)
            self.last_modified = datetime.now().isoformat()
    
    def get_sessions_by_day(self, day: str) -> List[ClassSession]:
        """Get all sessions for a specific day"""
        return [session for session in self.sessions if session.day.lower() == day.lower()]
    
    def get_sessions_by_subject(self, subject_code: str) -> List[ClassSession]:
        """Get all sessions for a specific subject"""
        return [session for session in self.sessions if session.subject.code == subject_code]
    
    def to_dict(self):
        """Convert timetable to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'semester': self.semester,
            'created_date': self.created_date,
            'last_modified': self.last_modified,
            'sessions': [
                {
                    'subject': asdict(session.subject),
                    'day': session.day,
                    'time_slot': asdict(session.time_slot),
                    'room': session.room,
                    'session_type': session.session_type,
                    'notes': session.notes
                }
                for session in self.sessions
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create timetable from dictionary"""
        sessions = []
        for session_data in data.get('sessions', []):
            subject = Subject(**session_data['subject'])
            time_slot = TimeSlot(**session_data['time_slot'])
            session = ClassSession(
                subject=subject,
                day=session_data['day'],
                time_slot=time_slot,
                room=session_data.get('room', ''),
                session_type=session_data.get('session_type', 'Lecture'),
                notes=session_data.get('notes', '')
            )
            sessions.append(session)
        
        return cls(
            name=data['name'],
            semester=data['semester'],
            sessions=sessions,
            created_date=data.get('created_date', ''),
            last_modified=data.get('last_modified', '')
        )

# Predefined time slots for common schedules
COMMON_TIME_SLOTS = [
    TimeSlot("08:00", "09:00"),
    TimeSlot("09:00", "10:00"),
    TimeSlot("10:00", "11:00"),
    TimeSlot("11:00", "12:00"),
    TimeSlot("12:00", "13:00"),
    TimeSlot("13:00", "14:00"),
    TimeSlot("14:00", "15:00"),
    TimeSlot("15:00", "16:00"),
    TimeSlot("16:00", "17:00"),
    TimeSlot("17:00", "18:00"),
]

# Days of the week
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Session types
SESSION_TYPES = ["Lecture", "Lab", "Tutorial", "Seminar", "Workshop", "Practical"]

# Default subject colors
SUBJECT_COLORS = [
    "#3b82f6",  # Blue
    "#ef4444",  # Red
    "#10b981",  # Green
    "#f59e0b",  # Amber
    "#8b5cf6",  # Purple
    "#ec4899",  # Pink
    "#06b6d4",  # Cyan
    "#84cc16",  # Lime
    "#f97316",  # Orange
    "#6366f1",  # Indigo
]

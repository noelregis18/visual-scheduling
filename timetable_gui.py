"""
Modern GUI for Timetable Management System using CustomTkinter
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import threading

from models import Timetable, Subject, ClassSession, TimeSlot, WEEKDAYS, COMMON_TIME_SLOTS, SESSION_TYPES, SUBJECT_COLORS
from data_manager import DataManager

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ModernTimetableApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Timetable Management System")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 600)
        
        # Initialize data manager
        self.data_manager = DataManager()
        self.current_timetable: Optional[Timetable] = None
        self.subjects: List[Subject] = self.data_manager.load_subjects()
        self.settings = self.data_manager.load_settings()
        
        # Apply settings
        self.apply_settings()
        
        # Create main interface
        self.create_widgets()
        self.create_menu()
        
        # Load last opened timetable if any
        self.load_last_timetable()
    
    def apply_settings(self):
        """Apply saved settings"""
        ctk.set_appearance_mode(self.settings.get('appearance_mode', 'dark'))
        ctk.set_default_color_theme(self.settings.get('color_theme', 'blue'))
        
        geometry = self.settings.get('window_geometry', '1400x900')
        self.root.geometry(geometry)
    
    def create_widgets(self):
        """Create the main interface widgets"""
        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create top toolbar
        self.create_toolbar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
    
    def create_toolbar(self):
        """Create the top toolbar"""
        self.toolbar = ctk.CTkFrame(self.main_container)
        self.toolbar.pack(fill="x", padx=5, pady=(5, 10))
        
        # Left side buttons
        left_frame = ctk.CTkFrame(self.toolbar)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        ctk.CTkButton(left_frame, text="📋 New Timetable", 
                     command=self.new_timetable, width=120).pack(side="left", padx=5)
        ctk.CTkButton(left_frame, text="📂 Open", 
                     command=self.open_timetable, width=80).pack(side="left", padx=5)
        ctk.CTkButton(left_frame, text="💾 Save", 
                     command=self.save_timetable, width=80).pack(side="left", padx=5)
        
        # Middle - Timetable selector
        middle_frame = ctk.CTkFrame(self.toolbar)
        middle_frame.pack(side="left", fill="y", padx=20, pady=5)
        
        ctk.CTkLabel(middle_frame, text="Current Timetable:").pack(side="left", padx=5)
        self.timetable_var = ctk.StringVar(value="No timetable loaded")
        self.timetable_label = ctk.CTkLabel(middle_frame, textvariable=self.timetable_var,
                                          text_color=("gray70", "gray30"))
        self.timetable_label.pack(side="left", padx=5)
        
        # Right side buttons
        right_frame = ctk.CTkFrame(self.toolbar)
        right_frame.pack(side="right", fill="y", padx=5, pady=5)
        
        ctk.CTkButton(right_frame, text="➕ Add Class", 
                     command=self.add_class_dialog, width=100).pack(side="right", padx=5)
        ctk.CTkButton(right_frame, text="📚 Subjects", 
                     command=self.manage_subjects_dialog, width=100).pack(side="right", padx=5)
        ctk.CTkButton(right_frame, text="⚙️ Settings", 
                     command=self.settings_dialog, width=100).pack(side="right", padx=5)
    
    def create_main_content(self):
        """Create the main content area with tabview"""
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create tabs
        self.tabview.add("📅 Weekly View")
        self.tabview.add("📋 Daily View") 
        self.tabview.add("📊 Overview")
        
        # Setup tab content
        self.setup_weekly_view()
        self.setup_daily_view()
        self.setup_overview()
    
    def setup_weekly_view(self):
        """Setup the weekly timetable view"""
        weekly_frame = self.tabview.tab("📅 Weekly View")
        
        # Create scrollable frame for timetable
        self.weekly_scroll = ctk.CTkScrollableFrame(weekly_frame)
        self.weekly_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create timetable grid
        self.create_timetable_grid()
    
    def create_timetable_grid(self):
        """Create the visual timetable grid"""
        # Clear existing widgets
        for widget in self.weekly_scroll.winfo_children():
            widget.destroy()
        
        if not self.current_timetable:
            no_data_label = ctk.CTkLabel(self.weekly_scroll, 
                                       text="No timetable loaded. Create a new one or open an existing timetable.",
                                       font=ctk.CTkFont(size=16))
            no_data_label.pack(expand=True, fill="both", padx=20, pady=50)
            return
        
        # Create header
        header_frame = ctk.CTkFrame(self.weekly_scroll)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        # Time column header
        ctk.CTkLabel(header_frame, text="Time", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Day headers
        for i, day in enumerate(WEEKDAYS):
            if not self.settings.get('show_weekend', False) and day == 'Saturday':
                continue
            ctk.CTkLabel(header_frame, text=day, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=i+1, padx=5, pady=5, sticky="nsew")
        
        # Configure grid weights
        for i in range(len(WEEKDAYS) + 1):
            header_frame.grid_columnconfigure(i, weight=1)
        
        # Create time slots and class grid
        self.grid_frame = ctk.CTkFrame(self.weekly_scroll)
        self.grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create grid for each time slot
        for row, time_slot in enumerate(COMMON_TIME_SLOTS):
            # Time label
            time_frame = ctk.CTkFrame(self.grid_frame)
            time_frame.grid(row=row, column=0, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(time_frame, text=str(time_slot), 
                        font=ctk.CTkFont(size=12)).pack(expand=True, fill="both")
            
            # Day columns
            for col, day in enumerate(WEEKDAYS):
                if not self.settings.get('show_weekend', False) and day == 'Saturday':
                    continue
                
                cell_frame = ctk.CTkFrame(self.grid_frame)
                cell_frame.grid(row=row, column=col+1, padx=2, pady=2, sticky="nsew")
                
                # Find session for this time and day
                session = self.find_session(day, time_slot)
                if session:
                    self.create_session_widget(cell_frame, session)
                else:
                    # Empty cell - clickable to add class
                    empty_label = ctk.CTkLabel(cell_frame, text="", height=60)
                    empty_label.pack(expand=True, fill="both")
                    empty_label.bind("<Button-1>", 
                                   lambda e, d=day, t=time_slot: self.add_class_at_time(d, t))
        
        # Configure grid weights
        for i in range(len(WEEKDAYS) + 1):
            self.grid_frame.grid_columnconfigure(i, weight=1)
        for i in range(len(COMMON_TIME_SLOTS)):
            self.grid_frame.grid_rowconfigure(i, weight=1)
    
    def find_session(self, day: str, time_slot: TimeSlot) -> Optional[ClassSession]:
        """Find a session for given day and time"""
        if not self.current_timetable:
            return None
        
        for session in self.current_timetable.sessions:
            if (session.day == day and 
                session.time_slot.start_time == time_slot.start_time and
                session.time_slot.end_time == time_slot.end_time):
                return session
        return None
    
    def create_session_widget(self, parent, session: ClassSession):
        """Create a widget for a class session"""
        # Session frame with subject color
        session_frame = ctk.CTkFrame(parent, fg_color=session.subject.color, height=60)
        session_frame.pack(expand=True, fill="both", padx=2, pady=2)
        
        # Subject info
        subject_label = ctk.CTkLabel(session_frame, text=session.subject.code,
                                   font=ctk.CTkFont(weight="bold", size=12),
                                   text_color="white")
        subject_label.pack(anchor="n", pady=(5, 0))
        
        room_label = ctk.CTkLabel(session_frame, text=session.room,
                                font=ctk.CTkFont(size=10),
                                text_color="white")
        room_label.pack(anchor="n")
        
        type_label = ctk.CTkLabel(session_frame, text=session.session_type,
                                font=ctk.CTkFont(size=9),
                                text_color="white")
        type_label.pack(anchor="n")
        
        # Right-click context menu
        session_frame.bind("<Button-3>", lambda e: self.show_session_context_menu(e, session))
        subject_label.bind("<Button-3>", lambda e: self.show_session_context_menu(e, session))
        room_label.bind("<Button-3>", lambda e: self.show_session_context_menu(e, session))
        type_label.bind("<Button-3>", lambda e: self.show_session_context_menu(e, session))
        
        # Double-click to edit
        session_frame.bind("<Double-Button-1>", lambda e: self.edit_session_dialog(session))
    
    def setup_daily_view(self):
        """Setup the daily view tab"""
        daily_frame = self.tabview.tab("📋 Daily View")
        
        # Day selector
        day_selector_frame = ctk.CTkFrame(daily_frame)
        day_selector_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(day_selector_frame, text="Select Day:", 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        
        self.selected_day = ctk.StringVar(value="Monday")
        day_menu = ctk.CTkOptionMenu(day_selector_frame, variable=self.selected_day,
                                   values=WEEKDAYS, command=self.update_daily_view)
        day_menu.pack(side="left", padx=10)
        
        # Daily schedule area
        self.daily_scroll = ctk.CTkScrollableFrame(daily_frame)
        self.daily_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update_daily_view()
    
    def update_daily_view(self, *args):
        """Update the daily view for selected day"""
        # Clear existing widgets
        for widget in self.daily_scroll.winfo_children():
            widget.destroy()
        
        if not self.current_timetable:
            no_data_label = ctk.CTkLabel(self.daily_scroll, text="No timetable loaded")
            no_data_label.pack(expand=True, fill="both", padx=20, pady=50)
            return
        
        selected_day = self.selected_day.get()
        day_sessions = self.current_timetable.get_sessions_by_day(selected_day)
        
        if not day_sessions:
            no_classes_label = ctk.CTkLabel(self.daily_scroll, 
                                          text=f"No classes scheduled for {selected_day}")
            no_classes_label.pack(expand=True, fill="both", padx=20, pady=50)
            return
        
        # Sort sessions by time
        day_sessions.sort(key=lambda s: s.time_slot.start_time)
        
        # Create session cards
        for session in day_sessions:
            self.create_daily_session_card(session)
    
    def create_daily_session_card(self, session: ClassSession):
        """Create a detailed session card for daily view"""
        card = ctk.CTkFrame(self.daily_scroll)
        card.pack(fill="x", padx=10, pady=5)
        
        # Left side - Time and type
        left_frame = ctk.CTkFrame(card, width=150)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        ctk.CTkLabel(left_frame, text=str(session.time_slot),
                    font=ctk.CTkFont(weight="bold", size=16)).pack(pady=5)
        ctk.CTkLabel(left_frame, text=session.session_type,
                    font=ctk.CTkFont(size=12)).pack()
        
        # Right side - Subject details
        right_frame = ctk.CTkFrame(card)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Subject name and code
        subject_frame = ctk.CTkFrame(right_frame)
        subject_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(subject_frame, text=session.subject.name,
                    font=ctk.CTkFont(weight="bold", size=18)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(subject_frame, text=f"Code: {session.subject.code}",
                    font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10)
        
        # Details frame
        details_frame = ctk.CTkFrame(right_frame)
        details_frame.pack(fill="x", pady=5)
        
        details_text = f"Room: {session.room}\nInstructor: {session.subject.instructor}\nCredits: {session.subject.credits}"
        if session.notes:
            details_text += f"\nNotes: {session.notes}"
        
        ctk.CTkLabel(details_frame, text=details_text,
                    font=ctk.CTkFont(size=11), justify="left").pack(anchor="w", padx=10, pady=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(right_frame)
        button_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(button_frame, text="Edit", width=60,
                     command=lambda: self.edit_session_dialog(session)).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Delete", width=60,
                     command=lambda: self.delete_session(session)).pack(side="right", padx=5)
    
    def setup_overview(self):
        """Setup the overview tab with statistics"""
        overview_frame = self.tabview.tab("📊 Overview")
        
        # Create overview content
        self.overview_scroll = ctk.CTkScrollableFrame(overview_frame)
        self.overview_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update_overview()
    
    def update_overview(self):
        """Update the overview with current timetable statistics"""
        # Clear existing widgets
        for widget in self.overview_scroll.winfo_children():
            widget.destroy()
        
        if not self.current_timetable:
            no_data_label = ctk.CTkLabel(self.overview_scroll, text="No timetable loaded")
            no_data_label.pack(expand=True, fill="both", padx=20, pady=50)
            return
        
        # Timetable info
        info_frame = ctk.CTkFrame(self.overview_scroll)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text=f"Timetable: {self.current_timetable.name}",
                    font=ctk.CTkFont(weight="bold", size=20)).pack(pady=10)
        ctk.CTkLabel(info_frame, text=f"Semester: {self.current_timetable.semester}",
                    font=ctk.CTkFont(size=14)).pack(pady=5)
        ctk.CTkLabel(info_frame, text=f"Total Classes: {len(self.current_timetable.sessions)}",
                    font=ctk.CTkFont(size=14)).pack(pady=5)
        
        # Subject statistics
        stats_frame = ctk.CTkFrame(self.overview_scroll)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Subject Statistics",
                    font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)
        
        # Count sessions by subject
        subject_counts = {}
        total_credits = 0
        for session in self.current_timetable.sessions:
            subject_code = session.subject.code
            if subject_code not in subject_counts:
                subject_counts[subject_code] = {
                    'count': 0,
                    'subject': session.subject
                }
            subject_counts[subject_code]['count'] += 1
            
        # Calculate total credits (avoid duplicates)
        unique_subjects = set()
        for session in self.current_timetable.sessions:
            if session.subject.code not in unique_subjects:
                total_credits += session.subject.credits
                unique_subjects.add(session.subject.code)
        
        ctk.CTkLabel(stats_frame, text=f"Total Credits: {total_credits}",
                    font=ctk.CTkFont(size=14)).pack(pady=5)
        
        # Subject breakdown
        for subject_code, data in subject_counts.items():
            subject_info = ctk.CTkFrame(stats_frame)
            subject_info.pack(fill="x", padx=10, pady=5)
            
            info_text = f"{data['subject'].name} ({subject_code}): {data['count']} classes"
            ctk.CTkLabel(subject_info, text=info_text).pack(anchor="w", padx=10, pady=5)
        
        # Weekly distribution
        weekly_frame = ctk.CTkFrame(self.overview_scroll)
        weekly_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(weekly_frame, text="Weekly Distribution",
                    font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)
        
        for day in WEEKDAYS:
            day_sessions = self.current_timetable.get_sessions_by_day(day)
            day_info = ctk.CTkFrame(weekly_frame)
            day_info.pack(fill="x", padx=10, pady=2)
            
            ctk.CTkLabel(day_info, text=f"{day}: {len(day_sessions)} classes",
                        font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=3)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ctk.CTkFrame(self.main_container, height=30)
        self.status_bar.pack(fill="x", padx=5, pady=(0, 5))
        self.status_bar.pack_propagate(False)
        
        self.status_text = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(self.status_bar, textvariable=self.status_text)
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Right side - current time
        self.time_label = ctk.CTkLabel(self.status_bar, text="")
        self.time_label.pack(side="right", padx=10, pady=5)
        self.update_time()
    
    def update_time(self):
        """Update the current time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Timetable", command=self.new_timetable)
        file_menu.add_command(label="Open Timetable", command=self.open_timetable)
        file_menu.add_command(label="Save Timetable", command=self.save_timetable)
        file_menu.add_separator()
        file_menu.add_command(label="Import JSON", command=self.import_json)
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Class", command=self.add_class_dialog)
        edit_menu.add_command(label="Manage Subjects", command=self.manage_subjects_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Settings", command=self.settings_dialog)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Weekly View", command=lambda: self.tabview.set("📅 Weekly View"))
        view_menu.add_command(label="Daily View", command=lambda: self.tabview.set("📋 Daily View"))
        view_menu.add_command(label="Overview", command=lambda: self.tabview.set("📊 Overview"))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def new_timetable(self):
        """Create a new timetable"""
        dialog = NewTimetableDialog(self.root, self.data_manager)
        if dialog.result:
            self.current_timetable = dialog.result
            self.timetable_var.set(self.current_timetable.name)
            self.refresh_all_views()
            self.set_status(f"Created new timetable: {self.current_timetable.name}")
    
    def open_timetable(self):
        """Open an existing timetable"""
        dialog = OpenTimetableDialog(self.root, self.data_manager)
        if dialog.result:
            self.current_timetable = dialog.result
            self.timetable_var.set(self.current_timetable.name)
            self.refresh_all_views()
            self.set_status(f"Opened timetable: {self.current_timetable.name}")
    
    def save_timetable(self):
        """Save the current timetable"""
        if not self.current_timetable:
            messagebox.showwarning("Warning", "No timetable to save!")
            return
        
        success = self.data_manager.save_timetable(self.current_timetable)
        if success:
            self.set_status(f"Saved timetable: {self.current_timetable.name}")
            messagebox.showinfo("Success", "Timetable saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save timetable!")
    
    def add_class_dialog(self):
        """Open dialog to add a new class"""
        if not self.current_timetable:
            messagebox.showwarning("Warning", "Please create or open a timetable first!")
            return
        
        dialog = AddClassDialog(self.root, self.subjects)
        if dialog.result:
            self.current_timetable.add_session(dialog.result)
            self.refresh_all_views()
            self.set_status("Added new class session")
    
    def add_class_at_time(self, day: str, time_slot: TimeSlot):
        """Add a class at specific day and time"""
        if not self.current_timetable:
            messagebox.showwarning("Warning", "Please create or open a timetable first!")
            return
        
        dialog = AddClassDialog(self.root, self.subjects, day, time_slot)
        if dialog.result:
            self.current_timetable.add_session(dialog.result)
            self.refresh_all_views()
            self.set_status(f"Added class on {day} at {time_slot}")
    
    def edit_session_dialog(self, session: ClassSession):
        """Edit an existing session"""
        dialog = EditClassDialog(self.root, self.subjects, session)
        if dialog.result:
            # Remove old session and add updated one
            self.current_timetable.remove_session(session)
            self.current_timetable.add_session(dialog.result)
            self.refresh_all_views()
            self.set_status("Updated class session")
    
    def delete_session(self, session: ClassSession):
        """Delete a session"""
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete {session.subject.name} class?"):
            self.current_timetable.remove_session(session)
            self.refresh_all_views()
            self.set_status("Deleted class session")
    
    def manage_subjects_dialog(self):
        """Open dialog to manage subjects"""
        dialog = ManageSubjectsDialog(self.root, self.subjects, self.data_manager)
        if dialog.subjects_modified:
            self.subjects = dialog.subjects
            self.refresh_all_views()
            self.set_status("Updated subjects")
    
    def settings_dialog(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.root, self.settings, self.data_manager)
        if dialog.settings_modified:
            self.settings = dialog.settings
            self.apply_settings()
            self.refresh_all_views()
            self.set_status("Settings updated")
    
    def show_session_context_menu(self, event, session: ClassSession):
        """Show context menu for a session"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Edit", command=lambda: self.edit_session_dialog(session))
        context_menu.add_command(label="Delete", command=lambda: self.delete_session(session))
        context_menu.add_separator()
        context_menu.add_command(label="View Details", command=lambda: self.show_session_details(session))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_session_details(self, session: ClassSession):
        """Show detailed information about a session"""
        details = f"""Subject: {session.subject.name}
Code: {session.subject.code}
Day: {session.day}
Time: {session.time_slot}
Room: {session.room}
Type: {session.session_type}
Instructor: {session.subject.instructor}
Credits: {session.subject.credits}
Notes: {session.notes}"""
        
        messagebox.showinfo("Class Details", details)
    
    def import_json(self):
        """Import timetable from JSON file"""
        file_path = filedialog.askopenfilename(
            title="Import Timetable",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            timetable = self.data_manager.import_from_json(file_path)
            if timetable:
                self.current_timetable = timetable
                self.timetable_var.set(self.current_timetable.name)
                self.refresh_all_views()
                self.set_status(f"Imported timetable from {file_path}")
                messagebox.showinfo("Success", "Timetable imported successfully!")
            else:
                messagebox.showerror("Error", "Failed to import timetable!")
    
    def export_json(self):
        """Export current timetable to JSON"""
        if not self.current_timetable:
            messagebox.showwarning("Warning", "No timetable to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Timetable",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            success = self.data_manager.export_to_json(self.current_timetable, file_path)
            if success:
                self.set_status(f"Exported timetable to {file_path}")
                messagebox.showinfo("Success", "Timetable exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export timetable!")
    
    def export_csv(self):
        """Export current timetable to CSV"""
        if not self.current_timetable:
            messagebox.showwarning("Warning", "No timetable to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Timetable to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            success = self.data_manager.export_to_csv(self.current_timetable, file_path)
            if success:
                self.set_status(f"Exported timetable to {file_path}")
                messagebox.showinfo("Success", "Timetable exported to CSV successfully!")
            else:
                messagebox.showerror("Error", "Failed to export timetable!")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Timetable Management System v1.0

A modern, user-friendly application for managing academic timetables.

Features:
• Create and manage multiple timetables
• Add, edit, and delete class sessions
• Subject management with color coding
• Weekly and daily views
• Import/Export functionality
• Modern dark/light theme support

Developed using Python and CustomTkinter"""
        
        messagebox.showinfo("About", about_text)
    
    def load_last_timetable(self):
        """Load the last opened timetable"""
        timetable_names = self.data_manager.get_timetable_names()
        if timetable_names:
            # Load the first available timetable
            self.current_timetable = self.data_manager.load_timetable(timetable_names[0])
            if self.current_timetable:
                self.timetable_var.set(self.current_timetable.name)
                self.refresh_all_views()
                self.set_status(f"Loaded timetable: {self.current_timetable.name}")
    
    def refresh_all_views(self):
        """Refresh all views with current data"""
        self.create_timetable_grid()
        self.update_daily_view()
        self.update_overview()
    
    def set_status(self, message: str):
        """Set status bar message"""
        self.status_text.set(message)
        
        # Clear status after 5 seconds
        def clear_status():
            self.status_text.set("Ready")
        
        self.root.after(5000, clear_status)
    
    def on_closing(self):
        """Handle application closing"""
        # Save current window geometry
        self.settings['window_geometry'] = self.root.geometry()
        self.data_manager.save_settings(self.settings)
        
        # Auto-save current timetable if enabled
        if self.settings.get('auto_save', True) and self.current_timetable:
            self.data_manager.save_timetable(self.current_timetable)
        
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


# Dialog classes for various operations
class NewTimetableDialog:
    def __init__(self, parent, data_manager):
        self.result = None
        self.data_manager = data_manager
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Create New Timetable")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Create New Timetable", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=20)
        
        # Name field
        ctk.CTkLabel(main_frame, text="Timetable Name:").pack(anchor="w", padx=10, pady=(10, 5))
        self.name_entry = ctk.CTkEntry(main_frame, width=300, placeholder_text="e.g., Fall 2024 Schedule")
        self.name_entry.pack(padx=10, pady=(0, 10))
        
        # Semester field
        ctk.CTkLabel(main_frame, text="Semester:").pack(anchor="w", padx=10, pady=(10, 5))
        self.semester_entry = ctk.CTkEntry(main_frame, width=300, placeholder_text="e.g., Fall 2024")
        self.semester_entry.pack(padx=10, pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Create", command=self.create).pack(side="right", padx=5)
        
        # Focus on name entry
        self.name_entry.focus()
    
    def create(self):
        name = self.name_entry.get().strip()
        semester = self.semester_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a timetable name!")
            return
        
        if not semester:
            messagebox.showerror("Error", "Please enter a semester!")
            return
        
        # Check if timetable name already exists
        existing_names = self.data_manager.get_timetable_names()
        if name in existing_names:
            messagebox.showerror("Error", "A timetable with this name already exists!")
            return
        
        self.result = Timetable(name=name, semester=semester, sessions=[], 
                               created_date="", last_modified="")
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


class OpenTimetableDialog:
    def __init__(self, parent, data_manager):
        self.result = None
        self.data_manager = data_manager
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Open Timetable")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Open Timetable", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=20)
        
        # Timetable list
        self.timetable_listbox = tk.Listbox(main_frame, height=10)
        self.timetable_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load timetable names
        timetable_names = self.data_manager.get_timetable_names()
        for name in timetable_names:
            self.timetable_listbox.insert(tk.END, name)
        
        if not timetable_names:
            ctk.CTkLabel(main_frame, text="No saved timetables found.").pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel).pack(side="right", padx=5)
        if timetable_names:
            ctk.CTkButton(button_frame, text="Open", command=self.open_selected).pack(side="right", padx=5)
            ctk.CTkButton(button_frame, text="Delete", command=self.delete_selected).pack(side="right", padx=5)
        
        # Double-click to open
        self.timetable_listbox.bind("<Double-Button-1>", lambda e: self.open_selected())
    
    def open_selected(self):
        selection = self.timetable_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a timetable to open!")
            return
        
        name = self.timetable_listbox.get(selection[0])
        self.result = self.data_manager.load_timetable(name)
        if self.result:
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to load the selected timetable!")
    
    def delete_selected(self):
        selection = self.timetable_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a timetable to delete!")
            return
        
        name = self.timetable_listbox.get(selection[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            success = self.data_manager.delete_timetable(name)
            if success:
                self.timetable_listbox.delete(selection[0])
                messagebox.showinfo("Success", "Timetable deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete the timetable!")
    
    def cancel(self):
        self.dialog.destroy()


class AddClassDialog:
    def __init__(self, parent, subjects, default_day=None, default_time_slot=None):
        self.result = None
        self.subjects = subjects
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Add New Class")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.default_day = default_day
        self.default_time_slot = default_time_slot
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Add New Class", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=20)
        
        # Subject selection
        ctk.CTkLabel(main_frame, text="Subject:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        if self.subjects:
            subject_names = [f"{s.code}: {s.name}" for s in self.subjects]
            self.subject_var = ctk.StringVar(value=subject_names[0])
            self.subject_menu = ctk.CTkOptionMenu(main_frame, variable=self.subject_var, values=subject_names)
            self.subject_menu.pack(fill="x", padx=10, pady=(0, 10))
        else:
            ctk.CTkLabel(main_frame, text="No subjects available. Please add subjects first.").pack(padx=10, pady=10)
            ctk.CTkButton(main_frame, text="Cancel", command=self.cancel).pack(pady=20)
            return
        
        # Day selection
        ctk.CTkLabel(main_frame, text="Day:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        default_day = self.default_day if self.default_day else WEEKDAYS[0]
        self.day_var = ctk.StringVar(value=default_day)
        day_menu = ctk.CTkOptionMenu(main_frame, variable=self.day_var, values=WEEKDAYS)
        day_menu.pack(fill="x", padx=10, pady=(0, 10))
        
        # Time selection
        ctk.CTkLabel(main_frame, text="Time Slot:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        time_options = [str(ts) for ts in COMMON_TIME_SLOTS]
        default_time = str(self.default_time_slot) if self.default_time_slot else time_options[0]
        self.time_var = ctk.StringVar(value=default_time)
        time_menu = ctk.CTkOptionMenu(main_frame, variable=self.time_var, values=time_options)
        time_menu.pack(fill="x", padx=10, pady=(0, 10))
        
        # Room
        ctk.CTkLabel(main_frame, text="Room:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.room_entry = ctk.CTkEntry(main_frame, placeholder_text="e.g., Room 101, Lab A")
        self.room_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Session type
        ctk.CTkLabel(main_frame, text="Session Type:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.session_type_var = ctk.StringVar(value=SESSION_TYPES[0])
        session_type_menu = ctk.CTkOptionMenu(main_frame, variable=self.session_type_var, values=SESSION_TYPES)
        session_type_menu.pack(fill="x", padx=10, pady=(0, 10))
        
        # Notes
        ctk.CTkLabel(main_frame, text="Notes:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.notes_textbox = ctk.CTkTextbox(main_frame, height=80)
        self.notes_textbox.pack(fill="x", padx=10, pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Add Class", command=self.add_class).pack(side="right", padx=5)
    
    def add_class(self):
        if not self.subjects:
            return
        
        # Get selected subject
        subject_selection = self.subject_var.get()
        subject_code = subject_selection.split(":")[0]
        selected_subject = None
        for subject in self.subjects:
            if subject.code == subject_code:
                selected_subject = subject
                break
        
        if not selected_subject:
            messagebox.showerror("Error", "Invalid subject selection!")
            return
        
        # Parse time slot
        time_str = self.time_var.get()
        start_time, end_time = time_str.split(" - ")
        time_slot = TimeSlot(start_time, end_time)
        
        # Create class session
        self.result = ClassSession(
            subject=selected_subject,
            day=self.day_var.get(),
            time_slot=time_slot,
            room=self.room_entry.get(),
            session_type=self.session_type_var.get(),
            notes=self.notes_textbox.get("1.0", tk.END).strip()
        )
        
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


class EditClassDialog(AddClassDialog):
    def __init__(self, parent, subjects, session):
        self.session = session
        super().__init__(parent, subjects)
        self.dialog.title("Edit Class")
        self.populate_fields()
    
    def populate_fields(self):
        # Set values from existing session
        subject_name = f"{self.session.subject.code}: {self.session.subject.name}"
        self.subject_var.set(subject_name)
        self.day_var.set(self.session.day)
        self.time_var.set(str(self.session.time_slot))
        self.room_entry.insert(0, self.session.room)
        self.session_type_var.set(self.session.session_type)
        self.notes_textbox.insert("1.0", self.session.notes)


class ManageSubjectsDialog:
    def __init__(self, parent, subjects, data_manager):
        self.subjects = subjects.copy()
        self.data_manager = data_manager
        self.subjects_modified = False
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Manage Subjects")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        self.refresh_subjects_list()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Manage Subjects", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=20)
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Subject list
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(left_frame, text="Subjects:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.subjects_listbox = tk.Listbox(left_frame, height=15)
        self.subjects_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.subjects_listbox.bind("<<ListboxSelect>>", self.on_subject_select)
        
        # Right side - Subject details
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(right_frame, text="Subject Details:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        # Subject form
        form_frame = ctk.CTkFrame(right_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="Subject Name:").pack(anchor="w", padx=10, pady=(10, 5))
        self.name_entry = ctk.CTkEntry(form_frame, width=200)
        self.name_entry.pack(padx=10, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Subject Code:").pack(anchor="w", padx=10, pady=(10, 5))
        self.code_entry = ctk.CTkEntry(form_frame, width=200)
        self.code_entry.pack(padx=10, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Credits:").pack(anchor="w", padx=10, pady=(10, 5))
        self.credits_entry = ctk.CTkEntry(form_frame, width=200)
        self.credits_entry.pack(padx=10, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Instructor:").pack(anchor="w", padx=10, pady=(10, 5))
        self.instructor_entry = ctk.CTkEntry(form_frame, width=200)
        self.instructor_entry.pack(padx=10, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Color:").pack(anchor="w", padx=10, pady=(10, 5))
        self.color_var = ctk.StringVar(value=SUBJECT_COLORS[0])
        color_menu = ctk.CTkOptionMenu(form_frame, variable=self.color_var, values=SUBJECT_COLORS)
        color_menu.pack(padx=10, pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="Add", command=self.add_subject, width=80).pack(pady=5)
        ctk.CTkButton(button_frame, text="Update", command=self.update_subject, width=80).pack(pady=5)
        ctk.CTkButton(button_frame, text="Delete", command=self.delete_subject, width=80).pack(pady=5)
        
        # Bottom buttons
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(bottom_frame, text="Cancel", command=self.cancel).pack(side="right", padx=5)
        ctk.CTkButton(bottom_frame, text="Save Changes", command=self.save_changes).pack(side="right", padx=5)
    
    def refresh_subjects_list(self):
        self.subjects_listbox.delete(0, tk.END)
        for subject in self.subjects:
            self.subjects_listbox.insert(tk.END, f"{subject.code}: {subject.name}")
    
    def on_subject_select(self, event):
        selection = self.subjects_listbox.curselection()
        if selection:
            subject = self.subjects[selection[0]]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, subject.name)
            self.code_entry.delete(0, tk.END)
            self.code_entry.insert(0, subject.code)
            self.credits_entry.delete(0, tk.END)
            self.credits_entry.insert(0, str(subject.credits))
            self.instructor_entry.delete(0, tk.END)
            self.instructor_entry.insert(0, subject.instructor)
            self.color_var.set(subject.color)
    
    def add_subject(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        
        if not name or not code:
            messagebox.showerror("Error", "Name and code are required!")
            return
        
        # Check for duplicate code
        for subject in self.subjects:
            if subject.code == code:
                messagebox.showerror("Error", "Subject code already exists!")
                return
        
        try:
            credits = int(self.credits_entry.get() or "3")
        except ValueError:
            messagebox.showerror("Error", "Credits must be a number!")
            return
        
        new_subject = Subject(
            name=name,
            code=code,
            credits=credits,
            instructor=self.instructor_entry.get().strip(),
            color=self.color_var.get()
        )
        
        self.subjects.append(new_subject)
        self.refresh_subjects_list()
        self.clear_form()
        self.subjects_modified = True
    
    def update_subject(self):
        selection = self.subjects_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a subject to update!")
            return
        
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        
        if not name or not code:
            messagebox.showerror("Error", "Name and code are required!")
            return
        
        try:
            credits = int(self.credits_entry.get() or "3")
        except ValueError:
            messagebox.showerror("Error", "Credits must be a number!")
            return
        
        subject = self.subjects[selection[0]]
        subject.name = name
        subject.code = code
        subject.credits = credits
        subject.instructor = self.instructor_entry.get().strip()
        subject.color = self.color_var.get()
        
        self.refresh_subjects_list()
        self.subjects_modified = True
    
    def delete_subject(self):
        selection = self.subjects_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a subject to delete!")
            return
        
        subject = self.subjects[selection[0]]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{subject.name}'?"):
            self.subjects.pop(selection[0])
            self.refresh_subjects_list()
            self.clear_form()
            self.subjects_modified = True
    
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.code_entry.delete(0, tk.END)
        self.credits_entry.delete(0, tk.END)
        self.instructor_entry.delete(0, tk.END)
        self.color_var.set(SUBJECT_COLORS[0])
    
    def save_changes(self):
        if self.subjects_modified:
            success = self.data_manager.save_subjects(self.subjects)
            if success:
                messagebox.showinfo("Success", "Subjects saved successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save subjects!")
        else:
            self.dialog.destroy()
    
    def cancel(self):
        if self.subjects_modified:
            if messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Are you sure you want to cancel?"):
                self.dialog.destroy()
        else:
            self.dialog.destroy()


class SettingsDialog:
    def __init__(self, parent, settings, data_manager):
        self.settings = settings.copy()
        self.data_manager = data_manager
        self.settings_modified = False
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Settings", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=20)
        
        # Appearance settings
        appearance_frame = ctk.CTkFrame(main_frame)
        appearance_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(appearance_frame, text="Appearance", 
                    font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=10, pady=10)
        
        # Theme mode
        ctk.CTkLabel(appearance_frame, text="Theme Mode:").pack(anchor="w", padx=10, pady=(5, 0))
        self.theme_var = ctk.StringVar(value=self.settings.get('appearance_mode', 'dark'))
        theme_menu = ctk.CTkOptionMenu(appearance_frame, variable=self.theme_var, 
                                     values=["light", "dark", "system"])
        theme_menu.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Color theme
        ctk.CTkLabel(appearance_frame, text="Color Theme:").pack(anchor="w", padx=10, pady=(5, 0))
        self.color_theme_var = ctk.StringVar(value=self.settings.get('color_theme', 'blue'))
        color_theme_menu = ctk.CTkOptionMenu(appearance_frame, variable=self.color_theme_var,
                                           values=["blue", "green", "dark-blue"])
        color_theme_menu.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Display settings
        display_frame = ctk.CTkFrame(main_frame)
        display_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(display_frame, text="Display", 
                    font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=10, pady=10)
        
        # Show weekend
        self.show_weekend_var = ctk.BooleanVar(value=self.settings.get('show_weekend', False))
        weekend_check = ctk.CTkCheckBox(display_frame, text="Show Saturday in weekly view", 
                                      variable=self.show_weekend_var)
        weekend_check.pack(anchor="w", padx=10, pady=5)
        
        # Time format
        ctk.CTkLabel(display_frame, text="Time Format:").pack(anchor="w", padx=10, pady=(10, 0))
        self.time_format_var = ctk.StringVar(value=self.settings.get('time_format', '24h'))
        time_format_menu = ctk.CTkOptionMenu(display_frame, variable=self.time_format_var,
                                           values=["12h", "24h"])
        time_format_menu.pack(anchor="w", padx=10, pady=(0, 10))
        
        # General settings
        general_frame = ctk.CTkFrame(main_frame)
        general_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(general_frame, text="General", 
                    font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=10, pady=10)
        
        # Auto save
        self.auto_save_var = ctk.BooleanVar(value=self.settings.get('auto_save', True))
        auto_save_check = ctk.CTkCheckBox(general_frame, text="Auto-save timetables", 
                                        variable=self.auto_save_var)
        auto_save_check.pack(anchor="w", padx=10, pady=5)
        
        # Default session duration
        ctk.CTkLabel(general_frame, text="Default Session Duration (minutes):").pack(anchor="w", padx=10, pady=(10, 0))
        self.duration_entry = ctk.CTkEntry(general_frame, width=100)
        self.duration_entry.pack(anchor="w", padx=10, pady=(0, 10))
        self.duration_entry.insert(0, str(self.settings.get('default_session_duration', 60)))
        
        # Notification settings
        notification_frame = ctk.CTkFrame(main_frame)
        notification_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(notification_frame, text="Notifications", 
                    font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=10, pady=10)
        
        # Enable reminders
        self.reminder_var = ctk.BooleanVar(value=self.settings.get('reminder_enabled', True))
        reminder_check = ctk.CTkCheckBox(notification_frame, text="Enable class reminders", 
                                       variable=self.reminder_var)
        reminder_check.pack(anchor="w", padx=10, pady=5)
        
        # Reminder minutes
        ctk.CTkLabel(notification_frame, text="Reminder time (minutes before class):").pack(anchor="w", padx=10, pady=(10, 0))
        self.reminder_entry = ctk.CTkEntry(notification_frame, width=100)
        self.reminder_entry.pack(anchor="w", padx=10, pady=(0, 10))
        self.reminder_entry.insert(0, str(self.settings.get('reminder_minutes', 15)))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Apply", command=self.apply_settings).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side="left", padx=5)
    
    def apply_settings(self):
        try:
            # Update settings
            self.settings['appearance_mode'] = self.theme_var.get()
            self.settings['color_theme'] = self.color_theme_var.get()
            self.settings['show_weekend'] = self.show_weekend_var.get()
            self.settings['time_format'] = self.time_format_var.get()
            self.settings['auto_save'] = self.auto_save_var.get()
            self.settings['default_session_duration'] = int(self.duration_entry.get())
            self.settings['reminder_enabled'] = self.reminder_var.get()
            self.settings['reminder_minutes'] = int(self.reminder_entry.get())
            
            # Save settings
            success = self.data_manager.save_settings(self.settings)
            if success:
                self.settings_modified = True
                messagebox.showinfo("Success", "Settings applied successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings!")
        
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for duration and reminder time!")
    
    def reset_defaults(self):
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.settings = self.data_manager.get_default_settings()
            self.dialog.destroy()
            # Recreate dialog with default values
            SettingsDialog(self.dialog.master, self.settings, self.data_manager)
    
    def cancel(self):
        self.dialog.destroy()


if __name__ == "__main__":
    app = ModernTimetableApp()
    app.run()
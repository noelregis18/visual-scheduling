# 📅 Visual Scheduling

A modern, user-friendly desktop application for managing academic timetables with a beautiful and intuitive interface.

## ✨ Features

### 🎯 Core Features
- **Multiple Timetables**: Create and manage multiple timetables for different semesters
- **Visual Scheduling**: Drag-and-drop interface with color-coded subjects
- **Smart Time Management**: Pre-defined time slots with custom time support
- **Subject Management**: Complete subject database with instructors, credits, and color coding

### 📊 Views & Interface
- **📅 Weekly View**: Complete week overview with all classes
- **📋 Daily View**: Detailed daily schedule with session information
- **📊 Overview**: Statistics and analytics for your timetables
- **🌙 Modern UI**: Dark/Light theme support with customizable colors

### 💾 Data Management
- **Auto-Save**: Automatic saving of changes
- **Import/Export**: JSON and CSV export capabilities
- **Backup System**: Automatic backups of your data
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 🔧 Advanced Features
- **Search & Filter**: Quick search through classes and subjects
- **Conflict Detection**: Automatic detection of scheduling conflicts
- **Multiple Session Types**: Lectures, Labs, Tutorials, Seminars
- **Room Management**: Track classroom assignments
- **Notes System**: Add custom notes to any class session

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd timetable_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📖 How to Use

### Getting Started

1. **Create Your First Timetable**
   - Click "📋 New Timetable" in the toolbar
   - Enter a name (e.g., "Fall 2024 Schedule")
   - Enter the semester information
   - Click "Create"

2. **Add Subjects**
   - Click "📚 Subjects" in the toolbar
   - Add your subjects with codes, names, and instructors
   - Choose colors for easy identification
   - Save your subjects

3. **Schedule Classes**
   - Click "➕ Add Class" or click on any empty time slot
   - Select the subject, day, and time
   - Add room number and session type
   - Save the class

### Interface Overview

#### 🛠️ Toolbar
- **New/Open/Save**: Timetable management
- **Add Class**: Quick class addition
- **Subjects**: Manage your subject database
- **Settings**: Customize the application

#### 📑 Tabs
- **📅 Weekly View**: See your entire week at a glance
- **📋 Daily View**: Focus on a specific day
- **📊 Overview**: View statistics and summaries

### Managing Classes

#### Adding Classes
1. Use the "➕ Add Class" button or click empty time slots
2. Fill in the class details:
   - **Subject**: Choose from your subject list
   - **Day**: Select the day of the week
   - **Time**: Pick from common time slots
   - **Room**: Enter the classroom or location
   - **Type**: Lecture, Lab, Tutorial, etc.
   - **Notes**: Any additional information

#### Editing Classes
- **Double-click** any class to edit it
- **Right-click** for context menu with Edit/Delete options
- All changes are automatically saved

#### Color Coding
- Each subject has a unique color for easy identification
- Colors can be customized in the Subject Management dialog
- Visual consistency across all views

### Data Management

#### Saving & Loading
- **Auto-Save**: Changes are automatically saved (can be disabled in settings)
- **Manual Save**: Use Ctrl+S or the Save button
- **Multiple Timetables**: Switch between different semester schedules

#### Import & Export
- **Export to JSON**: Full timetable data export
- **Export to CSV**: Spreadsheet-compatible format
- **Import JSON**: Load timetables from other sources

#### Backup System
- Automatic backups are created periodically
- Backups stored in the `data/backups` folder
- Manual backup creation available

## ⚙️ Settings & Customization

### Appearance Settings
- **Theme Mode**: Light, Dark, or System
- **Color Themes**: Blue, Green, or Dark Blue
- **Weekend Display**: Show/hide Saturday

### Display Options
- **Time Format**: 12-hour or 24-hour format
- **Session Duration**: Default class length
- **Grid Layout**: Customize the weekly view

### General Settings
- **Auto-Save**: Enable/disable automatic saving
- **Reminders**: Class notification settings
- **Default Values**: Set preferred defaults for new classes

## 📁 File Structure

```
timetable_app/
├── main.py              # Application entry point
├── timetable_gui.py     # Main GUI interface
├── models.py            # Data models and structures
├── data_manager.py      # Data persistence layer
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
└── data/               # Application data (auto-created)
    ├── timetables.json # Saved timetables
    ├── subjects.json   # Subject database
    ├── settings.json   # User preferences
    └── backups/        # Automatic backups
```

## 🛡️ Data Safety

### Automatic Backups
- Backups created automatically
- Multiple backup versions maintained
- Easy restore functionality

### Data Storage
- All data stored in human-readable JSON format
- Data folder can be backed up separately
- No cloud dependencies - your data stays local

### Error Handling
- Graceful error recovery
- Data validation and integrity checks
- User-friendly error messages

## 🔧 Troubleshooting

### Common Issues

**Application won't start**
- Check Python version (3.8+ required)
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check console for error messages

**Interface looks broken**
- Update customtkinter: `pip install --upgrade customtkinter`
- Try resetting settings in the Settings dialog

**Data not saving**
- Check file permissions in the application directory
- Ensure the `data` folder is writable
- Check disk space availability

**Performance issues**
- Close unused applications
- Try switching to light theme
- Reduce the number of subjects and classes if very large

### Getting Help

1. Check the console output for error messages
2. Verify all dependencies are properly installed
3. Try resetting to default settings
4. Check the `data` folder for corruption

## 🎨 Customization Tips

### Subject Organization
- Use consistent naming conventions for subjects
- Choose contrasting colors for better visibility
- Include instructor names for reference

### Efficient Scheduling
- Use the weekly view for overall planning
- Use daily view for detailed session management
- Utilize notes for important reminders

### Workflow Optimization
- Set up subjects before creating timetables
- Use copy/paste functionality when available
- Take advantage of keyboard shortcuts

## 📋 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Timetable |
| Ctrl+O | Open Timetable |
| Ctrl+S | Save Timetable |
| Ctrl+E | Export Timetable |
| Ctrl+A | Add Class |
| Ctrl+, | Settings |
| F1 | Help/About |

## 🔄 Updates & Maintenance

### Regular Maintenance
- Periodically backup your data folder
- Clean up old backup files if needed
- Update dependencies occasionally

### Feature Requests
This application is designed to be extensible. Common enhancement areas:
- Additional export formats
- Calendar integration
- Mobile companion app
- Cloud synchronization

## 📞 Support

For technical support or feature requests, please refer to the application's Help menu or check the console output for diagnostic information.

---

**Enjoy managing your academic schedule with style! 📚✨**

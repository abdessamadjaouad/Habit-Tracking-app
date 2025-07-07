# Habit Tracker Desktop Application

A modern desktop application for tracking daily habits with visual calendar interface and progress analytics.

## Features

- **Calendar View**: Visual calendar grid showing habits as rows and days as columns with checkboxes
- **Habit Management**: Add, edit, and delete habits with descriptions
- **Progress Charts**: Visual charts showing completion patterns and statistics
- **Monthly Navigation**: Navigate between months to view historical data
- **Data Persistence**: All data stored in MySQL database
- **Statistics**: Track completion rates, streaks, and progress trends

## Requirements

- Python 3.7+
- MySQL Server 5.7+ or 8.0+
- Required Python packages (see requirements.txt)

## Installation

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd Habit-Tracking-app
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database:**
   - Install MySQL Server on your system
   - Create a new database (optional - the app will create it automatically)
   - Update database credentials in `database.py` if needed

4. **Configure database connection:**
   Open `database.py` and modify the connection parameters:
   ```python
   def __init__(self, host='localhost', database='habit_tracker', user='root', password=''):
   ```

## Usage

### Running the Application

```bash
python main.py
```

### First Time Setup

1. **Database Connection**: On first run, the application will create the necessary database tables automatically
2. **Add Habits**: Click "Add Habit" to create your first habit
3. **Track Progress**: Use checkboxes in the calendar view to mark daily completions
4. **View Charts**: Switch to the "Progress Charts" tab to see visual progress

### Main Features

#### Calendar View
- Each row represents a habit
- Each column represents a day of the month
- Click checkboxes to mark habit completion
- Navigate months using arrow buttons

#### Habit Management
- **Add Habit**: Create new habits with name and optional description
- **Edit Habit**: Modify existing habit details
- **Delete Habit**: Remove habits (data is preserved)

#### Progress Charts
- Select a habit from the dropdown
- View bar chart showing daily completion status
- See statistics including completion rate and current streak

## Project Structure

```
Habit-Tracking-app/
├── main.py              # Application entry point
├── gui.py               # GUI components and interface
├── database.py          # Database operations and management
├── habit_manager.py     # Business logic for habit operations
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Database Schema

### Tables

**habits**
- `id` (INT, PRIMARY KEY): Unique habit identifier
- `name` (VARCHAR): Habit name
- `description` (TEXT): Optional habit description
- `created_date` (DATE): When habit was created
- `is_active` (BOOLEAN): Whether habit is active

**habit_logs**
- `id` (INT, PRIMARY KEY): Unique log identifier
- `habit_id` (INT, FOREIGN KEY): Reference to habit
- `completion_date` (DATE): Date of completion
- `completed` (BOOLEAN): Whether habit was completed

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL server is running
   - Check database credentials in `database.py`
   - Verify user has permission to create databases

2. **Missing Dependencies**
   - Run: `pip install -r requirements.txt`
   - Ensure Python 3.7+ is installed

3. **GUI Issues**
   - On Linux, you may need: `sudo apt-get install python3-tk`
   - On Windows, Tkinter is included with Python

### Database Setup Issues

If you encounter database connection issues:

1. **Install MySQL Server**: Download from https://dev.mysql.com/downloads/mysql/
2. **Create User** (optional):
   ```sql
   CREATE USER 'habit_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON habit_tracker.* TO 'habit_user'@'localhost';
   ```
3. **Update connection settings** in `database.py`

## Development

### Code Structure

- **MVC Pattern**: Separation of concerns with GUI, business logic, and data layers
- **Error Handling**: Comprehensive error handling and logging
- **Data Validation**: Input validation for all user data
- **Type Hints**: Full type annotations for better code maintainability

### Extending the Application

To add new features:

1. **Database changes**: Modify `database.py` and add migration logic
2. **Business logic**: Add methods to `habit_manager.py`
3. **GUI components**: Extend `gui.py` with new interface elements

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review the code comments for implementation details
- Create an issue in the repository for bugs or feature requests
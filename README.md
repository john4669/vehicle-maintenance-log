# Vehicle Maintenance Log

A cross-platform desktop application for tracking vehicle maintenance, built with Python, PySide6 (Qt6), and SQLite.

## Features

- **Multi-vehicle support** — manage as many vehicles as you need
- **Spreadsheet-style table** — sortable columns, familiar layout
- **Maintenance categories** — oil changes, brakes, tires, and more
- **Cost tracking** — parts, labor, and total cost per record
- **Next-due reminders** — track upcoming maintenance by date or mileage
- **CSV export** — export any vehicle's history to a spreadsheet
- **Active/inactive vehicles** — archive old vehicles without losing data
- **Single-file database** — your data is one portable `.db` file

## Requirements

- Python 3.10 or newer
- PySide6

## Setup

1. **Clone or download** this project into a folder.

2. **(Recommended) Create a virtual environment:**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**

   ```bash
   python main.py
   ```

The database file (`vehicle_maintenance.db`) is created automatically in the project folder on first run.

## Usage

### Adding a Vehicle
Click **Add Vehicle** in the toolbar or use the **Vehicle** menu. Fill in the year, make, model, and optionally VIN and plate number.

### Adding Maintenance Records
Select a vehicle from the dropdown, then click **Add Record**. Fill in the date, mileage, category, description, location, and costs.

### Editing Records
Double-click a row in the table, or select a row and click **Edit Record**.

### Exporting
Select a vehicle and use **File → Export to CSV** (or the toolbar button) to save that vehicle's full history as a CSV file.

### Keyboard Shortcuts
| Shortcut   | Action            |
|------------|-------------------|
| Ctrl+N     | Add new record    |
| Ctrl+E     | Export to CSV     |
| Delete     | Delete record     |
| Ctrl+Q     | Quit              |

## Data Storage

All data is stored in a single SQLite file: `vehicle_maintenance.db`. To back up your data, simply copy this file. To move your data to another computer, copy the file along with the application.

## Project Structure

```
vehicle-maintenance-log/
├── main.py              # Application UI and entry point
├── database.py          # SQLite database operations
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── vehicle_maintenance.db  # Created on first run
```

## Future Ideas

- Import from CSV (migrate existing spreadsheet data)
- Dashboard with spending charts
- Reminder notifications for upcoming maintenance
- Dark/light theme toggle
- Fuel economy tracking
- Receipt photo attachments

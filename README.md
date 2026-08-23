# Vehicle Maintenance Log

A cross-platform desktop application for tracking vehicle maintenance, built with Python, PySide6 (Qt6), and SQLite.

## Features

- **Multi-vehicle support** — manage as many vehicles as you need
- **Spreadsheet-style table** — sortable columns with row numbers, familiar layout
- **Maintenance categories** — oil changes, brakes, tires, and more (plus custom categories)
- **Cost tracking** — parts, labor, and total cost per record
- **Next-due reminders** — track upcoming maintenance by date or mileage
- **CSV import** — migrate data from existing spreadsheets
- **CSV export** — export any vehicle's history to a spreadsheet
- **Active/inactive vehicles** — archive old vehicles without losing data
- **Color themes** — Light, Dark, Sky Blue, Sage Green, Warm Sand, Lavender, and Soft Rose
- **Configurable database location** — store your data on a shared drive to access from multiple computers
- **Auto-backup** — automatically backs up your database on close (keeps last 5)
- **File attachments** — attach receipts, photos, or PDFs to any record (auto-resized, stored in the database)
- **Search** — Ctrl+F or toolbar button opens an inline search bar with match count and prev/next navigation
- **Autocomplete** — Description and Location fields suggest previously entered values as you type
- **Smart field selection** — numeric fields select all text when clicked for easy overtyping
- **Desktop shortcuts** — scripts to create desktop shortcuts on Windows, Linux, and macOS
- **Single-file database** — your data is one portable `.db` file
- **Standalone Windows executable** — download and run, no Python install required

## Requirements

- Python 3.10 or newer (not needed if using the standalone `.exe`)

## Quick Start (Windows — Standalone)

1. Download **`VehicleMaintenanceLog.exe`** from the [Releases](../../releases) page.
2. Put it in any folder and double-click to run.

That's it! The database and settings are created automatically next to the `.exe`.

**Note:** Windows SmartScreen may show a "Windows protected your PC" warning. This is normal for unsigned open-source software — it does not mean the file is harmful. To proceed, click **"More info"** then **"Run anyway"**. The full source code is available in this repository if you prefer to review and run it yourself.

## Quick Start (Windows — From Source)

1. Install [Python](https://www.python.org/downloads/) — **check "Add Python to PATH"** during installation.
2. Clone or download this project.
3. Double-click **`setup.bat`** — this creates a virtual environment and installs dependencies.
4. Double-click **`VehicleLog.vbs`** to launch the app.

That's it! Use `VehicleLog.vbs` to launch the app anytime.

## Quick Start (macOS)

1. Install Python 3 if not already installed:
   ```bash
   brew install python3
   ```
2. Clone or download this project.
3. Make the scripts executable and run setup:
   ```bash
   chmod +x setup.sh VehicleLog.sh create-shortcut-macos.sh
   ./setup.sh
   ```
4. Create a desktop app shortcut (optional):
   ```bash
   ./create-shortcut-macos.sh
   ```
   This creates a **Vehicle Maintenance Log.app** on your Desktop. On first launch, macOS may prompt you to allow the app — right-click it and choose **Open**, or go to **System Settings → Privacy & Security → Open Anyway**.

5. Or launch directly from the terminal:
   ```bash
   ./VehicleLog.sh
   ```

## Quick Start (Linux)

1. Make sure Python 3 is installed:
   ```bash
   # Ubuntu / Mint
   sudo apt install python3 python3-venv python3-pip
   ```
2. Clone or download this project.
3. Make the scripts executable and run setup:
   ```bash
   chmod +x setup.sh VehicleLog.sh
   ./setup.sh
   ```
4. Launch the app:
   ```bash
   ./VehicleLog.sh
   ```

## Manual Setup (if you prefer)

If you'd rather not use the provided scripts:

```bash
cd vehicle-maintenance-log
python -m venv venv

# Activate the virtual environment
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
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

### Importing from CSV
Select a vehicle, then use **File → Import from CSV**. The importer auto-detects your column headers, shows a preview, and lets you confirm before importing. Supports common date formats and currency formatting.

### Exporting to CSV
Select a vehicle and use **File → Export to CSV** (or the toolbar button) to save that vehicle's full history as a CSV file.

### Changing the Theme
Use **View → Theme** to switch between color themes. Your choice is saved and remembered across restarts.

### Changing the Database Location
Use **File → Settings** to point the app at a database file on a shared drive. This lets you access the same data from multiple computers (Windows and Linux). The app can copy your existing data to the new location automatically.

### Keyboard Shortcuts
| Shortcut   | Action            |
|------------|-------------------|
| Ctrl+N     | Add new record    |
| Ctrl+I     | Import from CSV   |
| Ctrl+E     | Export to CSV     |
| Ctrl+P     | Print             |
| Delete     | Delete record     |
| Ctrl+Q     | Quit              |

## Data Storage

All data is stored in a single SQLite file: `vehicle_maintenance.db`. To back up your data, simply copy this file. The database location can be changed in **File → Settings**.

App preferences (theme, database path) are stored in `settings.json` in the project folder.

## Project Structure

```
vehicle-maintenance-log/
├── main.py                      # Application UI and entry point
├── database.py                  # SQLite database operations
├── config.py                    # Settings management
├── requirements.txt             # Python dependencies
├── setup.bat                    # Windows first-time setup
├── setup.sh                     # macOS / Linux first-time setup
├── VehicleLog.vbs               # Windows launcher (no terminal window)
├── VehicleLog.sh                # macOS / Linux launcher
├── create-shortcut-windows.vbs  # Creates Windows desktop shortcut
├── create-shortcut-macos.sh     # Creates macOS desktop app bundle
├── create-shortcut-linux.sh     # Creates Linux desktop shortcut
├── icon.ico                     # Windows app icon
├── icon_256.png                 # macOS / Linux app icon
├── icon.svg                     # Scalable vector icon (source)
├── VehicleLog.spec              # PyInstaller build configuration
├── build.bat                    # Build standalone .exe (Windows)
├── .gitignore                   # Git ignore rules
├── LICENSE                      # CC BY-NC-SA 4.0
├── README.md                    # This file
├── settings.json                # Created on first settings change
└── vehicle_maintenance.db       # Created on first run
```

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](LICENSE) (CC BY-NC-SA 4.0).

This application uses [PySide6/Qt](https://www.qt.io/) (LGPL-3.0). Source code is available in this repository, allowing you to rebuild with a modified Qt library.

## Future Ideas

- Dashboard with spending charts
- Reminder notifications for upcoming maintenance
- Fuel economy tracking

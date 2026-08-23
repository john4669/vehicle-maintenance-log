# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cross-platform desktop app for tracking vehicle maintenance records. Built with Python 3.10+, PySide6 (Qt6), and SQLite. Single-developer project, no automated tests or CI.

## Development Commands

```bash
# First-time setup (creates venv, installs deps)
./setup.sh

# Run the app
./VehicleLog.sh

# Or manually:
source venv/bin/activate
python main.py

# Build standalone Windows .exe
build.bat  # uses PyInstaller via VehicleLog.spec
```

Only dependency: `PySide6>=6.6.0`

## Architecture

Three-module structure — all application code lives in root:

- **main.py** — Entire UI layer. Contains `MainWindow`, all dialogs (`VehicleDialog`, `RecordDialog`, `SettingsDialog`, `ImportCSVDialog`), theme definitions, image processing, CSV import/export, and print support. ~2000 lines, monolithic by design.
- **database.py** — SQLite wrapper class `Database`. Handles schema creation/migration, CRUD for vehicles/records/attachments, CSV export, and vehicle summaries. Uses `sqlite3.Row` for dict-like access.
- **config.py** — JSON-based settings stored alongside the executable. Merges user settings with `_DEFAULTS` on every read. Config file location adapts for PyInstaller frozen builds via `sys._MEIPASS`.

## Cross-Platform Line Endings

A `.gitattributes` file enforces LF for all Python/text files and CRLF for `.bat`/`.vbs` scripts. Binary files (`.db`, `.exe`, `.png`, `.ico`) are marked binary. This prevents CRLF issues when building the Windows `.exe` via PyInstaller after pulling on Windows.

## Key Design Decisions

- **Single-file database**: All data including file attachments (images, PDFs) stored as BLOBs in SQLite. Images are auto-resized to max 1920px with JPEG thumbnails at 200px.
- **Portable app**: Config and database default to the app's own directory. No system-wide install paths.
- **PyInstaller bundling**: Resources (`icon_256.png`, `icon.ico`) resolved via `sys._MEIPASS` when frozen. The `.spec` file is the build config.
- **No category column in UI**: Category was removed from the table view but remains in the database schema for backward compatibility.
- **Foreign keys enabled**: `PRAGMA foreign_keys = ON` — cascading deletes are active.

## Workflow Notes

- Before committing, always ask whether README.md needs to be updated to reflect the change.

## UI Patterns

- Vehicle selector dropdown in toolbar controls which records are displayed
- Table is rebuilt from DB on most operations (no in-memory model sync)
- Themes are applied via `QPalette` manipulation, defined as dicts in `main.py`
- Dialogs return data via `dialog.exec()` + reading fields after acceptance

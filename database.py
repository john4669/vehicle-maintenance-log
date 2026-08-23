"""
database.py - SQLite database operations for Vehicle Maintenance Log
"""

import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_path="vehicle_maintenance.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                vin TEXT DEFAULT '',
                plate TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                mileage INTEGER,
                category TEXT DEFAULT '',
                description TEXT NOT NULL,
                location TEXT DEFAULT '',
                parts_cost REAL DEFAULT 0.0,
                labor_cost REAL DEFAULT 0.0,
                total_cost REAL DEFAULT 0.0,
                next_due_date TEXT DEFAULT '',
                next_due_mileage INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
            )
        """)

        # Add tax column if upgrading from older schema
        cursor.execute("PRAGMA table_info(maintenance_records)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "tax" not in existing_cols:
            cursor.execute(
                "ALTER TABLE maintenance_records ADD COLUMN tax REAL DEFAULT 0.0"
            )

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT DEFAULT '',
                file_size INTEGER DEFAULT 0,
                file_data BLOB NOT NULL,
                thumbnail BLOB,
                added_date TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (record_id) REFERENCES maintenance_records(id) ON DELETE CASCADE
            )
        """)

        self.conn.commit()

    # ── Vehicle Operations ──────────────────────────────────────────

    def add_vehicle(self, year, make, model, vin="", plate="", notes="", active=True):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO vehicles (year, make, model, vin, plate, notes, active)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (year, make, model, vin, plate, notes, int(active)),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_vehicle(self, vehicle_id, year, make, model, vin="", plate="", notes="", active=True):
        self.conn.execute(
            """UPDATE vehicles
               SET year=?, make=?, model=?, vin=?, plate=?, notes=?, active=?
               WHERE id=?""",
            (year, make, model, vin, plate, notes, int(active), vehicle_id),
        )
        self.conn.commit()

    def delete_vehicle(self, vehicle_id):
        self.conn.execute("DELETE FROM vehicles WHERE id=?", (vehicle_id,))
        self.conn.commit()

    def get_vehicles(self, active_only=True):
        query = "SELECT * FROM vehicles"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY year DESC, make, model"
        return self.conn.execute(query).fetchall()

    def get_vehicle(self, vehicle_id):
        return self.conn.execute(
            "SELECT * FROM vehicles WHERE id=?", (vehicle_id,)
        ).fetchone()

    # ── Maintenance Record Operations ───────────────────────────────

    def add_record(self, vehicle_id, date, mileage, category, description,
                   location="", parts_cost=0.0, labor_cost=0.0, tax=0.0,
                   total_cost=0.0, next_due_date="", next_due_mileage=0, notes=""):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO maintenance_records
               (vehicle_id, date, mileage, category, description, location,
                parts_cost, labor_cost, tax, total_cost,
                next_due_date, next_due_mileage, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (vehicle_id, date, mileage, category, description, location,
             parts_cost, labor_cost, tax, total_cost,
             next_due_date, next_due_mileage, notes),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_record(self, record_id, date, mileage, category, description,
                      location="", parts_cost=0.0, labor_cost=0.0, tax=0.0,
                      total_cost=0.0, next_due_date="", next_due_mileage=0, notes=""):
        self.conn.execute(
            """UPDATE maintenance_records
               SET date=?, mileage=?, category=?, description=?, location=?,
                   parts_cost=?, labor_cost=?, tax=?, total_cost=?,
                   next_due_date=?, next_due_mileage=?, notes=?
               WHERE id=?""",
            (date, mileage, category, description, location,
             parts_cost, labor_cost, tax, total_cost,
             next_due_date, next_due_mileage, notes, record_id),
        )
        self.conn.commit()

    def delete_record(self, record_id):
        self.conn.execute("DELETE FROM maintenance_records WHERE id=?", (record_id,))
        self.conn.commit()

    def get_records(self, vehicle_id, sort_column="date", sort_order="DESC"):
        allowed_columns = {"date", "mileage", "description",
                           "location", "total_cost"}
        if sort_column not in allowed_columns:
            sort_column = "date"
        if sort_order not in ("ASC", "DESC"):
            sort_order = "DESC"

        query = f"""SELECT * FROM maintenance_records
                    WHERE vehicle_id = ?
                    ORDER BY {sort_column} {sort_order}"""
        return self.conn.execute(query, (vehicle_id,)).fetchall()

    def get_record(self, record_id):
        return self.conn.execute(
            "SELECT * FROM maintenance_records WHERE id=?", (record_id,)
        ).fetchone()

    # ── Attachment Operations ─────────────────────────────────────────

    def add_attachment(self, record_id, filename, file_type, file_size, file_data, thumbnail=None):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO attachments
               (record_id, filename, file_type, file_size, file_data, thumbnail)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (record_id, filename, file_type, file_size, file_data, thumbnail),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_attachments(self, record_id):
        """Return attachments for a record (without file_data for performance)."""
        return self.conn.execute(
            """SELECT id, record_id, filename, file_type, file_size, thumbnail, added_date
               FROM attachments WHERE record_id = ? ORDER BY added_date""",
            (record_id,),
        ).fetchall()

    def get_attachment_data(self, attachment_id):
        """Return full file_data for a single attachment."""
        return self.conn.execute(
            "SELECT file_data, filename, file_type FROM attachments WHERE id = ?",
            (attachment_id,),
        ).fetchone()

    def delete_attachment(self, attachment_id):
        self.conn.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        self.conn.commit()

    def get_attachment_count(self, record_id):
        row = self.conn.execute(
            "SELECT COUNT(*) as count FROM attachments WHERE record_id = ?",
            (record_id,),
        ).fetchone()
        return row["count"]

    def get_distinct_values(self, field):
        """Return sorted distinct non-empty values for 'description' or 'location'."""
        if field not in {"description", "location"}:
            return []
        rows = self.conn.execute(
            f"SELECT DISTINCT {field} FROM maintenance_records "
            f"WHERE {field} != '' ORDER BY {field} COLLATE NOCASE"
        ).fetchall()
        return [row[0] for row in rows]

    # ── Summary / Stats ─────────────────────────────────────────────

    def get_vehicle_summary(self, vehicle_id):
        """Return total spent, record count, and mileage range for a vehicle."""
        row = self.conn.execute(
            """SELECT COUNT(*) as count,
                      COALESCE(SUM(total_cost), 0) as total_spent,
                      MIN(mileage) as min_mileage,
                      MAX(mileage) as max_mileage
               FROM maintenance_records WHERE vehicle_id = ?""",
            (vehicle_id,),
        ).fetchone()
        return dict(row)

    # ── Export ──────────────────────────────────────────────────────

    def export_vehicle_csv(self, vehicle_id, filepath):
        """Export all records for a vehicle to CSV."""
        import csv

        vehicle = self.get_vehicle(vehicle_id)
        records = self.get_records(vehicle_id, sort_order="ASC")

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Header with vehicle info
            writer.writerow([f"Vehicle: {vehicle['year']} {vehicle['make']} {vehicle['model']}"])
            writer.writerow([f"VIN: {vehicle['vin']}", f"Plate: {vehicle['plate']}"])
            writer.writerow([])
            # Column headers
            writer.writerow([
                "Date", "Mileage", "Description", "Location",
                "Parts Cost", "Labor Cost", "Tax", "Total Cost",
                "Next Due Date", "Next Due Mileage", "Notes"
            ])
            for r in records:
                writer.writerow([
                    r["date"], r["mileage"], r["description"],
                    r["location"], f"{r['parts_cost']:.2f}", f"{r['labor_cost']:.2f}",
                    f"{r['tax']:.2f}", f"{r['total_cost']:.2f}", r["next_due_date"],
                    r["next_due_mileage"], r["notes"],
                ])

        return filepath

    def close(self):
        self.conn.close()

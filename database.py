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
                   location="", parts_cost=0.0, labor_cost=0.0, total_cost=0.0,
                   next_due_date="", next_due_mileage=0, notes=""):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO maintenance_records
               (vehicle_id, date, mileage, category, description, location,
                parts_cost, labor_cost, total_cost, next_due_date, next_due_mileage, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (vehicle_id, date, mileage, category, description, location,
             parts_cost, labor_cost, total_cost, next_due_date, next_due_mileage, notes),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_record(self, record_id, date, mileage, category, description,
                      location="", parts_cost=0.0, labor_cost=0.0, total_cost=0.0,
                      next_due_date="", next_due_mileage=0, notes=""):
        self.conn.execute(
            """UPDATE maintenance_records
               SET date=?, mileage=?, category=?, description=?, location=?,
                   parts_cost=?, labor_cost=?, total_cost=?, next_due_date=?,
                   next_due_mileage=?, notes=?
               WHERE id=?""",
            (date, mileage, category, description, location,
             parts_cost, labor_cost, total_cost, next_due_date, next_due_mileage,
             notes, record_id),
        )
        self.conn.commit()

    def delete_record(self, record_id):
        self.conn.execute("DELETE FROM maintenance_records WHERE id=?", (record_id,))
        self.conn.commit()

    def get_records(self, vehicle_id, sort_column="date", sort_order="DESC"):
        allowed_columns = {"date", "mileage", "category", "description",
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
                "Date", "Mileage", "Category", "Description", "Location",
                "Parts Cost", "Labor Cost", "Total Cost",
                "Next Due Date", "Next Due Mileage", "Notes"
            ])
            for r in records:
                writer.writerow([
                    r["date"], r["mileage"], r["category"], r["description"],
                    r["location"], f"{r['parts_cost']:.2f}", f"{r['labor_cost']:.2f}",
                    f"{r['total_cost']:.2f}", r["next_due_date"],
                    r["next_due_mileage"], r["notes"],
                ])

        return filepath

    def close(self):
        self.conn.close()

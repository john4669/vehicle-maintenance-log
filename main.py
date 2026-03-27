"""
main.py - Vehicle Maintenance Log
A cross-platform desktop app built with PySide6 (Qt6) and SQLite.
"""

import sys
import os
import csv
import shutil
import re
from datetime import datetime, date

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QPushButton,
    QDialog, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit,
    QLabel, QMessageBox, QFileDialog, QToolBar, QStatusBar, QCheckBox,
    QDateEdit, QAbstractItemView, QGroupBox, QSplitter, QFrame,
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import (
    QAction, QActionGroup, QIcon, QFont, QColor, QPalette,
    QTextDocument, QPageLayout,
)
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog

from database import Database
import config


# ── Maintenance Categories ──────────────────────────────────────────

CATEGORIES = [
    "Oil Change",
    "Tires",
    "Brakes",
    "Battery",
    "Transmission",
    "Coolant/Radiator",
    "Air Filter",
    "Spark Plugs",
    "Belts/Hoses",
    "Suspension",
    "Exhaust",
    "Electrical",
    "Body/Paint",
    "Inspection/Emissions",
    "Wiper Blades",
    "Lights/Bulbs",
    "Alignment",
    "Fluid Top-Off",
    "Warranty Work",
    "Recall",
    "Other",
]


# ── Color Themes ────────────────────────────────────────────────────

def _make_palette(colors):
    """Build a QPalette from a dict of role → color hex values."""
    pal = QPalette()
    role_map = {
        "window":          QPalette.Window,
        "window_text":     QPalette.WindowText,
        "base":            QPalette.Base,
        "alt_base":        QPalette.AlternateBase,
        "text":            QPalette.Text,
        "button":          QPalette.Button,
        "button_text":     QPalette.ButtonText,
        "highlight":       QPalette.Highlight,
        "highlight_text":  QPalette.HighlightedText,
        "tooltip_base":    QPalette.ToolTipBase,
        "tooltip_text":    QPalette.ToolTipText,
        "bright_text":     QPalette.BrightText,
        "link":            QPalette.Link,
    }
    for key, role in role_map.items():
        if key in colors:
            pal.setColor(role, QColor(colors[key]))
    # Disabled text
    if "disabled_text" in colors:
        pal.setColor(QPalette.Disabled, QPalette.WindowText, QColor(colors["disabled_text"]))
        pal.setColor(QPalette.Disabled, QPalette.Text, QColor(colors["disabled_text"]))
        pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(colors["disabled_text"]))
    return pal


THEMES = {
    "system": None,  # Use default system palette
    "light": {
        "window": "#F7F7F7", "window_text": "#333333", "base": "#FFFFFF",
        "alt_base": "#F2F2F2", "text": "#333333", "button": "#EBEBEB",
        "button_text": "#333333", "highlight": "#88B8E0", "highlight_text": "#FFFFFF",
        "tooltip_base": "#FFFFF0", "tooltip_text": "#333333",
        "bright_text": "#D06050", "link": "#6699CC", "disabled_text": "#B0B0B0",
    },
    "dark": {
        "window": "#484C50", "window_text": "#E8E8E8", "base": "#52565A",
        "alt_base": "#5A5E62", "text": "#E8E8E8", "button": "#606468",
        "button_text": "#E8E8E8", "highlight": "#88B8E0", "highlight_text": "#FFFFFF",
        "tooltip_base": "#5A5E62", "tooltip_text": "#E8E8E8",
        "bright_text": "#F09080", "link": "#99C4E8", "disabled_text": "#909090",
    },
    "sky": {
        "window": "#E8F0F8", "window_text": "#3A4A5A", "base": "#F0F6FC",
        "alt_base": "#DCEAF5", "text": "#3A4A5A", "button": "#D0E2F0",
        "button_text": "#3A4A5A", "highlight": "#7AAED4", "highlight_text": "#FFFFFF",
        "tooltip_base": "#F0F6FC", "tooltip_text": "#3A4A5A",
        "bright_text": "#D06050", "link": "#5A90B8", "disabled_text": "#98AAB8",
    },
    "sage": {
        "window": "#EAF0E6", "window_text": "#3A4A3A", "base": "#F2F7F0",
        "alt_base": "#DEE8DA", "text": "#3A4A3A", "button": "#D2E0CC",
        "button_text": "#3A4A3A", "highlight": "#88B888", "highlight_text": "#FFFFFF",
        "tooltip_base": "#F2F7F0", "tooltip_text": "#3A4A3A",
        "bright_text": "#D06050", "link": "#608A60", "disabled_text": "#98A898",
    },
    "sand": {
        "window": "#F0EBE0", "window_text": "#4A4038", "base": "#F7F3EA",
        "alt_base": "#E8E0D4", "text": "#4A4038", "button": "#DED6C8",
        "button_text": "#4A4038", "highlight": "#C8A878", "highlight_text": "#FFFFFF",
        "tooltip_base": "#F7F3EA", "tooltip_text": "#4A4038",
        "bright_text": "#C06050", "link": "#A08050", "disabled_text": "#B0A898",
    },
    "lavender": {
        "window": "#EDE8F2", "window_text": "#403848", "base": "#F4F0F8",
        "alt_base": "#E2DCE8", "text": "#403848", "button": "#D8D0E0",
        "button_text": "#403848", "highlight": "#A088C0", "highlight_text": "#FFFFFF",
        "tooltip_base": "#F4F0F8", "tooltip_text": "#403848",
        "bright_text": "#D06050", "link": "#8870A8", "disabled_text": "#A098B0",
    },
    "rose": {
        "window": "#F2E8EA", "window_text": "#4A3838", "base": "#F8F0F2",
        "alt_base": "#E8DDE0", "text": "#4A3838", "button": "#E0D2D6",
        "button_text": "#4A3838", "highlight": "#C89098", "highlight_text": "#FFFFFF",
        "tooltip_base": "#F8F0F2", "tooltip_text": "#4A3838",
        "bright_text": "#C06050", "link": "#A87078", "disabled_text": "#B0A0A4",
    },
}


def apply_theme(app, theme_name):
    """Apply a color theme to the application."""
    if theme_name not in THEMES:
        theme_name = "system"
    colors = THEMES[theme_name]
    if colors is None:
        app.setPalette(app.style().standardPalette())
    else:
        app.setPalette(_make_palette(colors))


# ════════════════════════════════════════════════════════════════════
#  Vehicle Dialog
# ════════════════════════════════════════════════════════════════════

class VehicleDialog(QDialog):
    """Dialog for adding or editing a vehicle."""

    def __init__(self, parent=None, vehicle=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.setWindowTitle("Edit Vehicle" if vehicle else "Add Vehicle")
        self.setMinimumWidth(400)
        self._build_ui()

        if vehicle:
            self._populate(vehicle)

    def _build_ui(self):
        layout = QFormLayout(self)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2100)
        self.year_spin.setValue(date.today().year)
        layout.addRow("Year:", self.year_spin)

        self.make_edit = QLineEdit()
        self.make_edit.setPlaceholderText("e.g. Toyota")
        layout.addRow("Make:", self.make_edit)

        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("e.g. Camry")
        layout.addRow("Model:", self.model_edit)

        self.vin_edit = QLineEdit()
        self.vin_edit.setMaxLength(17)
        self.vin_edit.setPlaceholderText("17 characters")
        layout.addRow("VIN:", self.vin_edit)

        self.plate_edit = QLineEdit()
        self.plate_edit.setPlaceholderText("e.g. ABC-1234")
        layout.addRow("Plate #:", self.plate_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Color, trim, purchase date, etc.")
        layout.addRow("Notes:", self.notes_edit)

        self.active_check = QCheckBox("Vehicle is active")
        self.active_check.setChecked(True)
        layout.addRow("", self.active_check)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._validate_and_accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def _populate(self, v):
        self.year_spin.setValue(v["year"])
        self.make_edit.setText(v["make"])
        self.model_edit.setText(v["model"])
        self.vin_edit.setText(v["vin"] or "")
        self.plate_edit.setText(v["plate"] or "")
        self.notes_edit.setPlainText(v["notes"] or "")
        self.active_check.setChecked(bool(v["active"]))

    def _validate_and_accept(self):
        if not self.make_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Make is required.")
            return
        if not self.model_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Model is required.")
            return
        vin = self.vin_edit.text().strip()
        if vin and len(vin) != 17:
            QMessageBox.warning(self, "Validation",
                                "VIN must be exactly 17 characters (or leave blank).")
            return
        self.accept()

    def get_data(self):
        return {
            "year": self.year_spin.value(),
            "make": self.make_edit.text().strip(),
            "model": self.model_edit.text().strip(),
            "vin": self.vin_edit.text().strip().upper(),
            "plate": self.plate_edit.text().strip().upper(),
            "notes": self.notes_edit.toPlainText().strip(),
            "active": self.active_check.isChecked(),
        }


# ════════════════════════════════════════════════════════════════════
#  Maintenance Record Dialog
# ════════════════════════════════════════════════════════════════════

class RecordDialog(QDialog):
    """Dialog for adding or editing a maintenance record."""

    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("Edit Record" if record else "Add Maintenance Record")
        self.setMinimumWidth(450)
        self._build_ui()

        if record:
            self._populate(record)

    def _build_ui(self):
        layout = QFormLayout(self)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addRow("Date:", self.date_edit)

        self.mileage_spin = QSpinBox()
        self.mileage_spin.setRange(0, 9_999_999)
        self.mileage_spin.setSuffix(" mi")
        layout.addRow("Mileage:", self.mileage_spin)

        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES)
        self.category_combo.setEditable(True)
        layout.addRow("Category:", self.category_combo)

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("e.g. Full synthetic oil change, new filter")
        layout.addRow("Description:", self.desc_edit)

        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("e.g. Jiffy Lube - Main St")
        layout.addRow("Location:", self.location_edit)

        # ── Cost group ──
        cost_group = QGroupBox("Cost")
        cost_layout = QFormLayout(cost_group)

        self.parts_spin = QDoubleSpinBox()
        self.parts_spin.setRange(0, 999_999.99)
        self.parts_spin.setPrefix("$ ")
        self.parts_spin.setDecimals(2)
        self.parts_spin.valueChanged.connect(self._update_total)
        cost_layout.addRow("Parts:", self.parts_spin)

        self.labor_spin = QDoubleSpinBox()
        self.labor_spin.setRange(0, 999_999.99)
        self.labor_spin.setPrefix("$ ")
        self.labor_spin.setDecimals(2)
        self.labor_spin.valueChanged.connect(self._update_total)
        cost_layout.addRow("Labor:", self.labor_spin)

        self.total_spin = QDoubleSpinBox()
        self.total_spin.setRange(0, 999_999.99)
        self.total_spin.setPrefix("$ ")
        self.total_spin.setDecimals(2)
        cost_layout.addRow("Total:", self.total_spin)

        layout.addRow(cost_group)

        # ── Next Due group ──
        due_group = QGroupBox("Next Due (optional)")
        due_layout = QFormLayout(due_group)

        self.next_date_edit = QDateEdit()
        self.next_date_edit.setCalendarPopup(True)
        self.next_date_edit.setSpecialValueText("Not set")
        self.next_date_edit.setDate(self.next_date_edit.minimumDate())
        self.next_date_edit.setDisplayFormat("yyyy-MM-dd")
        due_layout.addRow("Date:", self.next_date_edit)

        self.next_mileage_spin = QSpinBox()
        self.next_mileage_spin.setRange(0, 9_999_999)
        self.next_mileage_spin.setSuffix(" mi")
        self.next_mileage_spin.setSpecialValueText("Not set")
        due_layout.addRow("Mileage:", self.next_mileage_spin)

        layout.addRow(due_group)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        self.notes_edit.setPlaceholderText("Additional notes...")
        layout.addRow("Notes:", self.notes_edit)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._validate_and_accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def _update_total(self):
        self.total_spin.setValue(self.parts_spin.value() + self.labor_spin.value())

    def _populate(self, r):
        self.date_edit.setDate(QDate.fromString(r["date"], "yyyy-MM-dd"))
        self.mileage_spin.setValue(r["mileage"] or 0)
        # Set category
        idx = self.category_combo.findText(r["category"])
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        else:
            self.category_combo.setEditText(r["category"] or "")
        self.desc_edit.setText(r["description"] or "")
        self.location_edit.setText(r["location"] or "")
        self.parts_spin.setValue(r["parts_cost"] or 0)
        self.labor_spin.setValue(r["labor_cost"] or 0)
        self.total_spin.setValue(r["total_cost"] or 0)
        if r["next_due_date"]:
            self.next_date_edit.setDate(QDate.fromString(r["next_due_date"], "yyyy-MM-dd"))
        if r["next_due_mileage"]:
            self.next_mileage_spin.setValue(r["next_due_mileage"])
        self.notes_edit.setPlainText(r["notes"] or "")

    def _validate_and_accept(self):
        if not self.desc_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Description is required.")
            return
        self.accept()

    def get_data(self):
        next_date = ""
        if self.next_date_edit.date() != self.next_date_edit.minimumDate():
            next_date = self.next_date_edit.date().toString("yyyy-MM-dd")

        return {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "mileage": self.mileage_spin.value(),
            "category": self.category_combo.currentText().strip(),
            "description": self.desc_edit.text().strip(),
            "location": self.location_edit.text().strip(),
            "parts_cost": self.parts_spin.value(),
            "labor_cost": self.labor_spin.value(),
            "total_cost": self.total_spin.value(),
            "next_due_date": next_date,
            "next_due_mileage": self.next_mileage_spin.value(),
            "notes": self.notes_edit.toPlainText().strip(),
        }


# ════════════════════════════════════════════════════════════════════
#  Settings Dialog
# ════════════════════════════════════════════════════════════════════

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(550)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ── Database Location ──
        db_group = QGroupBox("Database Location")
        db_layout = QVBoxLayout(db_group)

        current_path = config.get_db_path()
        info_label = QLabel(
            "Choose where the database file is stored. Use a shared drive\n"
            "to access your data from multiple computers."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray;")
        db_layout.addWidget(info_label)

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(current_path)
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_db)
        path_layout.addWidget(browse_btn)

        db_layout.addLayout(path_layout)

        self.copy_check = QCheckBox("Copy existing data to new location")
        self.copy_check.setChecked(False)
        self.copy_check.setEnabled(False)  # Enabled only when path changes
        db_layout.addWidget(self.copy_check)

        self.overwrite_warning = QLabel("")
        self.overwrite_warning.setStyleSheet("QLabel { color: #CC6600; padding: 2px; }")
        self.overwrite_warning.setWordWrap(True)
        self.overwrite_warning.setVisible(False)
        db_layout.addWidget(self.overwrite_warning)

        default_btn = QPushButton("Reset to Default (app folder)")
        default_btn.clicked.connect(self._reset_default)
        db_layout.addWidget(default_btn)

        layout.addWidget(db_group)

        # ── Current Info ──
        info_group = QGroupBox("Current Database Info")
        info_layout = QVBoxLayout(info_group)
        self.db_info_label = QLabel()
        self._update_db_info(current_path)
        info_layout.addWidget(self.db_info_label)
        layout.addWidget(info_group)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _browse_db(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Choose Database Location",
            self.path_edit.text(),
            "SQLite Database (*.db);;All Files (*)",
            options=QFileDialog.DontConfirmOverwrite,
        )
        if filepath:
            if not filepath.endswith(".db"):
                filepath += ".db"
            old_path = self.path_edit.text()
            self.path_edit.setText(filepath)
            path_changed = filepath != old_path
            self.copy_check.setEnabled(path_changed)
            if not path_changed:
                self.copy_check.setChecked(False)
            self._update_overwrite_warning(filepath)
            self._update_db_info(filepath)

    def _reset_default(self):
        default_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "vehicle_maintenance.db"
        )
        old_path = self.path_edit.text()
        self.path_edit.setText(default_path)
        path_changed = default_path != old_path
        self.copy_check.setEnabled(path_changed)
        if not path_changed:
            self.copy_check.setChecked(False)
        self._update_overwrite_warning(default_path)
        self._update_db_info(default_path)

    def _update_db_info(self, path):
        if os.path.exists(path):
            size_kb = os.path.getsize(path) / 1024
            self.db_info_label.setText(
                f"Path: {path}\n"
                f"Size: {size_kb:.1f} KB\n"
                f"Status: File exists"
            )
        else:
            self.db_info_label.setText(
                f"Path: {path}\n"
                f"Status: New file (will be created on save)"
            )

    def _update_overwrite_warning(self, new_path):
        """Show a warning if copying would overwrite an existing database."""
        if self.copy_check.isEnabled() and os.path.exists(new_path):
            self.overwrite_warning.setText(
                "⚠ A database already exists at this location. "
                "If you check 'Copy existing data', it will OVERWRITE that file."
            )
            self.overwrite_warning.setVisible(True)
        else:
            self.overwrite_warning.setVisible(False)

    def get_new_path(self):
        return self.path_edit.text()

    def should_copy(self):
        return self.copy_check.isChecked() and self.copy_check.isEnabled()


# ════════════════════════════════════════════════════════════════════
#  Import CSV Dialog
# ════════════════════════════════════════════════════════════════════

class ImportCSVDialog(QDialog):
    """Dialog for importing maintenance records from a CSV file."""

    # Column mapping: CSV header → (db field, type)
    KNOWN_HEADERS = {
        "date":               ("date", "date"),
        "mileage":            ("mileage", "int"),
        "repair description": ("description", "str"),
        "description":        ("description", "str"),
        "maintenance done":   ("description", "str"),
        "workshop":           ("location", "str"),
        "location":           ("location", "str"),
        "maintenance location": ("location", "str"),
        "labor cost":         ("labor_cost", "float"),
        "labour cost":        ("labor_cost", "float"),
        "material cost":      ("parts_cost", "float"),
        "parts cost":         ("parts_cost", "float"),
        "total cost":         ("total_cost", "float"),
        "total":              ("total_cost", "float"),
        "price":              ("total_cost", "float"),
        "cost":               ("total_cost", "float"),
        "category":           ("category", "str"),
        "notes":              ("notes", "str"),
    }

    # Common date formats to try when parsing
    DATE_FORMATS = [
        "%Y-%m-%d",      # 2024-01-15
        "%m/%d/%Y",      # 01/15/2024
        "%m/%d/%y",      # 01/15/24
        "%d/%m/%Y",      # 15/01/2024
        "%m-%d-%Y",      # 01-15-2024
        "%d-%m-%Y",      # 15-01-2024
        "%b %d, %Y",     # Jan 15, 2024
        "%B %d, %Y",     # January 15, 2024
        "%d %b %Y",      # 15 Jan 2024
        "%d %B %Y",      # 15 January 2024
        "%Y/%m/%d",      # 2024/01/15
    ]

    def __init__(self, parent=None, filepath=""):
        super().__init__(parent)
        self.setWindowTitle("Import CSV")
        self.setMinimumSize(800, 550)
        self.filepath = filepath
        self.parsed_rows = []
        self.header_row_idx = -1
        self.column_map = {}  # csv_col_index → db_field
        self.raw_rows = []
        self.csv_headers = []

        self._build_ui()
        if filepath:
            self._load_file(filepath)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File:"))
        self.file_label = QLabel(self.filepath or "No file selected")
        self.file_label.setStyleSheet("color: gray;")
        file_layout.addWidget(self.file_label, 1)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        # Info / instructions
        self.info_label = QLabel(
            "The importer will skip header rows at the top and auto-detect your columns.\n"
            "Review the preview below before importing."
        )
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: gray; padding: 4px;")
        layout.addWidget(self.info_label)

        # Detected mapping display
        self.mapping_label = QLabel("")
        self.mapping_label.setWordWrap(True)
        self.mapping_label.setStyleSheet(
            "QLabel { background-color: palette(alternate-base); "
            "padding: 8px; border-radius: 4px; }"
        )
        layout.addWidget(self.mapping_label)

        # Preview table
        layout.addWidget(QLabel("Preview (first 20 rows):"))
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.preview_table.verticalHeader().setVisible(False)
        layout.addWidget(self.preview_table)

        # Stats
        self.stats_label = QLabel("")
        layout.addWidget(self.stats_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import")
        self.import_btn.setDefault(True)
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _browse(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        if filepath:
            self._load_file(filepath)

    def _load_file(self, filepath):
        self.filepath = filepath
        self.file_label.setText(filepath)

        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                self.raw_rows = [row for row in reader]
        except UnicodeDecodeError:
            # Fallback for files saved with other encodings
            with open(filepath, "r", encoding="latin-1") as f:
                reader = csv.reader(f)
                self.raw_rows = [row for row in reader]
        except Exception as e:
            QMessageBox.critical(self, "Read Error", f"Could not read file:\n{e}")
            return

        if not self.raw_rows:
            QMessageBox.warning(self, "Empty File", "The file appears to be empty.")
            return

        self._detect_header_row()
        self._detect_columns()
        self._parse_data_rows()
        self._update_preview()

    def _detect_header_row(self):
        """Find the row that contains the column headers."""
        for idx, row in enumerate(self.raw_rows):
            lower_cells = [c.strip().lower() for c in row]
            # Look for rows that contain at least 2 known header names
            matches = sum(1 for c in lower_cells if c in self.KNOWN_HEADERS)
            if matches >= 2:
                self.header_row_idx = idx
                self.csv_headers = [c.strip() for c in row]
                return

        # Fallback: assume first non-empty row with enough columns
        for idx, row in enumerate(self.raw_rows):
            if len([c for c in row if c.strip()]) >= 3:
                self.header_row_idx = idx
                self.csv_headers = [c.strip() for c in row]
                return

    def _detect_columns(self):
        """Map CSV column indices to database fields."""
        self.column_map = {}
        for col_idx, header in enumerate(self.csv_headers):
            key = header.strip().lower()
            if key in self.KNOWN_HEADERS:
                db_field, _ = self.KNOWN_HEADERS[key]
                self.column_map[col_idx] = db_field

        # Show mapping
        if self.column_map:
            lines = []
            for col_idx, db_field in sorted(self.column_map.items()):
                lines.append(f'"{self.csv_headers[col_idx]}" → {db_field}')
            self.mapping_label.setText("Column mapping:  " + "   |   ".join(lines))
        else:
            self.mapping_label.setText("⚠ Could not auto-detect columns.")

    def _parse_date(self, text):
        """Try multiple date formats and return yyyy-MM-dd or the original text."""
        text = text.strip()
        if not text:
            return ""
        for fmt in self.DATE_FORMATS:
            try:
                dt = datetime.strptime(text, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return text  # Return as-is if no format matched

    def _parse_float(self, text):
        """Parse a currency/float value, stripping $, commas, etc."""
        text = text.strip()
        if not text:
            return 0.0
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.\-]', '', text)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _parse_int(self, text):
        """Parse an integer value, stripping commas, etc."""
        text = text.strip()
        if not text:
            return 0
        cleaned = re.sub(r'[^\d]', '', text)
        try:
            return int(cleaned)
        except ValueError:
            return 0

    def _parse_data_rows(self):
        """Parse all data rows after the header into record dicts."""
        self.parsed_rows = []
        if self.header_row_idx < 0 or not self.column_map:
            return

        for row in self.raw_rows[self.header_row_idx + 1:]:
            # Skip empty rows
            if not any(c.strip() for c in row):
                continue

            record = {
                "date": "",
                "mileage": 0,
                "category": "",
                "description": "",
                "location": "",
                "parts_cost": 0.0,
                "labor_cost": 0.0,
                "total_cost": 0.0,
                "next_due_date": "",
                "next_due_mileage": 0,
                "notes": "",
            }

            for col_idx, db_field in self.column_map.items():
                if col_idx >= len(row):
                    continue
                raw = row[col_idx]
                _, ftype = self.KNOWN_HEADERS.get(
                    self.csv_headers[col_idx].strip().lower(), (db_field, "str")
                )

                if ftype == "date":
                    record[db_field] = self._parse_date(raw)
                elif ftype == "float":
                    record[db_field] = self._parse_float(raw)
                elif ftype == "int":
                    record[db_field] = self._parse_int(raw)
                else:
                    record[db_field] = raw.strip()

            # Only include rows that have at least a date or description
            if record["date"] or record["description"]:
                self.parsed_rows.append(record)

    def _update_preview(self):
        """Show parsed data in the preview table."""
        columns = ["Date", "Mileage", "Category", "Description",
                    "Location", "Parts $", "Labor $", "Total $"]
        fields = ["date", "mileage", "category", "description",
                  "location", "parts_cost", "labor_cost", "total_cost"]

        self.preview_table.setColumnCount(len(columns))
        self.preview_table.setHorizontalHeaderLabels(columns)

        preview = self.parsed_rows[:20]
        self.preview_table.setRowCount(len(preview))

        for row_idx, record in enumerate(preview):
            for col_idx, field in enumerate(fields):
                val = record[field]
                if isinstance(val, float):
                    text = f"${val:,.2f}"
                elif isinstance(val, int) and field == "mileage":
                    text = f"{val:,}" if val else ""
                else:
                    text = str(val)
                self.preview_table.setItem(row_idx, col_idx, QTableWidgetItem(text))

        header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        # Stats
        total_rows = len(self.parsed_rows)
        skipped = len(self.raw_rows) - (self.header_row_idx + 1) - total_rows
        self.stats_label.setText(
            f"Found {total_rows} records to import"
            f"{f' ({skipped} empty rows skipped)' if skipped > 0 else ''}"
        )

        self.import_btn.setEnabled(total_rows > 0)

    def get_records(self):
        return self.parsed_rows


# ════════════════════════════════════════════════════════════════════
#  Main Window
# ════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.current_vehicle_id = None

        self.setWindowTitle("Vehicle Maintenance Log")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 700)

        self._build_menu()
        self._build_toolbar()
        self._build_central()
        self._build_statusbar()
        self._refresh_vehicle_list()

    # ── Menu Bar ────────────────────────────────────────────────────

    def _build_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        export_action = QAction("&Export to CSV...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_action)

        import_action = QAction("&Import from CSV...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_csv)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        print_action = QAction("&Print...", self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self._print_log)
        file_menu.addAction(print_action)

        file_menu.addSeparator()

        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self._open_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Vehicle menu
        vehicle_menu = menubar.addMenu("&Vehicle")

        add_v = QAction("&Add Vehicle...", self)
        add_v.triggered.connect(self._add_vehicle)
        vehicle_menu.addAction(add_v)

        edit_v = QAction("&Edit Vehicle...", self)
        edit_v.triggered.connect(self._edit_vehicle)
        vehicle_menu.addAction(edit_v)

        del_v = QAction("&Delete Vehicle", self)
        del_v.triggered.connect(self._delete_vehicle)
        vehicle_menu.addAction(del_v)

        vehicle_menu.addSeparator()

        self.show_inactive_action = QAction("Show &Inactive Vehicles", self)
        self.show_inactive_action.setCheckable(True)
        self.show_inactive_action.toggled.connect(self._refresh_vehicle_list)
        vehicle_menu.addAction(self.show_inactive_action)

        # Record menu
        record_menu = menubar.addMenu("&Record")

        add_r = QAction("&Add Record...", self)
        add_r.setShortcut("Ctrl+N")
        add_r.triggered.connect(self._add_record)
        record_menu.addAction(add_r)

        edit_r = QAction("&Edit Record...", self)
        edit_r.triggered.connect(self._edit_record)
        record_menu.addAction(edit_r)

        del_r = QAction("&Delete Record", self)
        del_r.setShortcut("Delete")
        del_r.triggered.connect(self._delete_record)
        record_menu.addAction(del_r)

        # View menu
        view_menu = menubar.addMenu("V&iew")
        theme_menu = view_menu.addMenu("&Theme")

        current_theme = config.get("theme") or "system"
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)

        theme_labels = {
            "system": "System Default",
            "light": "Light",
            "dark": "Dark",
            "sky": "Sky Blue",
            "sage": "Sage Green",
            "sand": "Warm Sand",
            "lavender": "Lavender",
            "rose": "Soft Rose",
        }
        for key, label in theme_labels.items():
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(key == current_theme)
            action.setData(key)
            action.triggered.connect(self._change_theme)
            theme_group.addAction(action)
            theme_menu.addAction(action)

    # ── Toolbar ─────────────────────────────────────────────────────

    def _build_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Vehicle selector
        toolbar.addWidget(QLabel("  Vehicle: "))
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.setMinimumWidth(250)
        self.vehicle_combo.currentIndexChanged.connect(self._on_vehicle_changed)
        toolbar.addWidget(self.vehicle_combo)

        toolbar.addSeparator()

        # Buttons
        add_v_btn = QPushButton(" Add Vehicle")
        add_v_btn.clicked.connect(self._add_vehicle)
        toolbar.addWidget(add_v_btn)

        toolbar.addSeparator()

        add_r_btn = QPushButton(" Add Record")
        add_r_btn.clicked.connect(self._add_record)
        toolbar.addWidget(add_r_btn)

        edit_r_btn = QPushButton(" Edit Record")
        edit_r_btn.clicked.connect(self._edit_record)
        toolbar.addWidget(edit_r_btn)

        del_r_btn = QPushButton(" Delete Record")
        del_r_btn.clicked.connect(self._delete_record)
        toolbar.addWidget(del_r_btn)

        toolbar.addSeparator()

        export_btn = QPushButton(" Export CSV")
        export_btn.clicked.connect(self._export_csv)
        toolbar.addWidget(export_btn)

    # ── Central Widget ──────────────────────────────────────────────

    def _build_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)

        # Vehicle info bar
        self.vehicle_info_label = QLabel("")
        self.vehicle_info_label.setStyleSheet(
            "QLabel { background-color: palette(alternate-base); "
            "padding: 8px; border-radius: 4px; }"
        )
        layout.addWidget(self.vehicle_info_label)

        # Summary bar
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("QLabel { color: gray; padding: 4px; }")
        layout.addWidget(self.summary_label)

        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self._edit_record)
        self.table.verticalHeader().setVisible(False)

        columns = [
            "#", "Date", "Mileage", "Category", "Description", "Location",
            "Parts $", "Labor $", "Total $", "Next Due", "Notes",
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # # column tight
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Description stretches
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Location stretches

        layout.addWidget(self.table)

    # ── Status Bar ──────────────────────────────────────────────────

    def _build_statusbar(self):
        self.statusBar().showMessage(f"Database: {self.db.db_path}")

    # ── Vehicle Operations ──────────────────────────────────────────

    def _refresh_vehicle_list(self):
        show_inactive = self.show_inactive_action.isChecked()
        vehicles = self.db.get_vehicles(active_only=not show_inactive)

        self.vehicle_combo.blockSignals(True)
        self.vehicle_combo.clear()

        if not vehicles:
            self.vehicle_combo.addItem("-- No vehicles. Add one! --", None)
            self.current_vehicle_id = None
            self._clear_table()
        else:
            for v in vehicles:
                label = f"{v['year']} {v['make']} {v['model']}"
                if not v["active"]:
                    label += " (inactive)"
                self.vehicle_combo.addItem(label, v["id"])

            # Restore selection if possible
            if self.current_vehicle_id is not None:
                for i in range(self.vehicle_combo.count()):
                    if self.vehicle_combo.itemData(i) == self.current_vehicle_id:
                        self.vehicle_combo.setCurrentIndex(i)
                        break

        self.vehicle_combo.blockSignals(False)
        self._on_vehicle_changed()

    def _on_vehicle_changed(self):
        vid = self.vehicle_combo.currentData()
        self.current_vehicle_id = vid
        if vid is None:
            self._clear_table()
            self.vehicle_info_label.setText("No vehicle selected.")
            self.summary_label.setText("")
            return
        self._refresh_vehicle_info()
        self._refresh_table()

    def _refresh_vehicle_info(self):
        v = self.db.get_vehicle(self.current_vehicle_id)
        if not v:
            return
        parts = [f"{v['year']} {v['make']} {v['model']}"]
        if v["vin"]:
            parts.append(f"VIN: {v['vin']}")
        if v["plate"]:
            parts.append(f"Plate: {v['plate']}")
        if v["notes"]:
            parts.append(f"Notes: {v['notes']}")
        self.vehicle_info_label.setText("   |   ".join(parts))

    def _add_vehicle(self):
        dlg = VehicleDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            new_id = self.db.add_vehicle(**data)
            self.current_vehicle_id = new_id
            self._refresh_vehicle_list()
            self.statusBar().showMessage("Vehicle added.", 3000)

    def _edit_vehicle(self):
        if self.current_vehicle_id is None:
            return
        vehicle = self.db.get_vehicle(self.current_vehicle_id)
        dlg = VehicleDialog(self, vehicle)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            self.db.update_vehicle(self.current_vehicle_id, **data)
            self._refresh_vehicle_list()
            self.statusBar().showMessage("Vehicle updated.", 3000)

    def _delete_vehicle(self):
        if self.current_vehicle_id is None:
            return
        v = self.db.get_vehicle(self.current_vehicle_id)
        reply = QMessageBox.question(
            self, "Delete Vehicle",
            f"Delete {v['year']} {v['make']} {v['model']} and ALL its records?\n\n"
            "This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.db.delete_vehicle(self.current_vehicle_id)
            self.current_vehicle_id = None
            self._refresh_vehicle_list()
            self.statusBar().showMessage("Vehicle deleted.", 3000)

    # ── Record Operations ───────────────────────────────────────────

    def _refresh_table(self):
        if self.current_vehicle_id is None:
            self._clear_table()
            return

        records = self.db.get_records(self.current_vehicle_id)
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(records))

        for row_idx, r in enumerate(records):
            # Row number column
            num_item = QTableWidgetItem()
            num_item.setData(Qt.DisplayRole, row_idx + 1)
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, num_item)

            # Store record ID in the date column's data
            date_item = QTableWidgetItem(r["date"])
            date_item.setData(Qt.UserRole, r["id"])
            self.table.setItem(row_idx, 1, date_item)

            # Mileage with comma formatting
            mileage_val = r["mileage"] or 0
            mileage_item = QTableWidgetItem(f"{mileage_val:,}" if mileage_val else "")
            mileage_item.setData(Qt.UserRole + 1, mileage_val)  # For sorting
            mileage_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 2, mileage_item)

            self.table.setItem(row_idx, 3, QTableWidgetItem(r["category"] or ""))
            self.table.setItem(row_idx, 4, QTableWidgetItem(r["description"] or ""))
            self.table.setItem(row_idx, 5, QTableWidgetItem(r["location"] or ""))

            for col, field in [(6, "parts_cost"), (7, "labor_cost"), (8, "total_cost")]:
                item = QTableWidgetItem(f"${r[field]:,.2f}")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row_idx, col, item)

            # Next due: show date or mileage or both
            next_parts = []
            if r["next_due_date"]:
                next_parts.append(r["next_due_date"])
            if r["next_due_mileage"]:
                next_parts.append(f"{r['next_due_mileage']:,} mi")
            self.table.setItem(row_idx, 9, QTableWidgetItem(" / ".join(next_parts)))

            self.table.setItem(row_idx, 10, QTableWidgetItem(r["notes"] or ""))

        self.table.setSortingEnabled(True)
        self._refresh_summary()

    def _clear_table(self):
        self.table.setRowCount(0)
        self.summary_label.setText("")

    def _refresh_summary(self):
        if self.current_vehicle_id is None:
            return
        s = self.db.get_vehicle_summary(self.current_vehicle_id)
        parts = [f"Records: {s['count']}"]
        parts.append(f"Total Spent: ${s['total_spent']:,.2f}")
        if s["min_mileage"] and s["max_mileage"]:
            parts.append(
                f"Mileage Range: {s['min_mileage']:,} – {s['max_mileage']:,}"
            )
        self.summary_label.setText("   |   ".join(parts))

    def _get_selected_record_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 1)  # Date column stores record ID
        return item.data(Qt.UserRole) if item else None

    def _add_record(self):
        if self.current_vehicle_id is None:
            QMessageBox.information(self, "No Vehicle",
                                    "Please add or select a vehicle first.")
            return
        dlg = RecordDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            self.db.add_record(self.current_vehicle_id, **data)
            self._refresh_table()
            self.statusBar().showMessage("Record added.", 3000)

    def _edit_record(self):
        record_id = self._get_selected_record_id()
        if record_id is None:
            QMessageBox.information(self, "No Selection",
                                    "Select a record to edit.")
            return
        record = self.db.get_record(record_id)
        dlg = RecordDialog(self, record)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            self.db.update_record(record_id, **data)
            self._refresh_table()
            self.statusBar().showMessage("Record updated.", 3000)

    def _delete_record(self):
        record_id = self._get_selected_record_id()
        if record_id is None:
            return
        reply = QMessageBox.question(
            self, "Delete Record",
            "Delete this maintenance record?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.db.delete_record(record_id)
            self._refresh_table()
            self.statusBar().showMessage("Record deleted.", 3000)

    # ── Export ──────────────────────────────────────────────────────

    def _export_csv(self):
        if self.current_vehicle_id is None:
            QMessageBox.information(self, "No Vehicle",
                                    "Select a vehicle to export.")
            return
        v = self.db.get_vehicle(self.current_vehicle_id)
        default_name = f"{v['year']}_{v['make']}_{v['model']}_maintenance.csv"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", default_name, "CSV Files (*.csv)"
        )
        if filepath:
            self.db.export_vehicle_csv(self.current_vehicle_id, filepath)
            self.statusBar().showMessage(f"Exported to {filepath}", 5000)

    # ── Print ──────────────────────────────────────────────────────

    def _print_log(self):
        if self.current_vehicle_id is None:
            QMessageBox.information(self, "No Vehicle",
                                    "Select a vehicle to print.")
            return

        v = self.db.get_vehicle(self.current_vehicle_id)
        records = self.db.get_records(self.current_vehicle_id)
        summary = self.db.get_vehicle_summary(self.current_vehicle_id)

        vehicle_name = f"{v['year']} {v['make']} {v['model']}"
        details = []
        if v["vin"]:
            details.append(f"VIN: {v['vin']}")
        if v["plate"]:
            details.append(f"Plate: {v['plate']}")

        # Build HTML
        html = (
            "<html><head><style>"
            "body { font-family: Arial, sans-serif; font-size: 10pt; }"
            "h2 { margin-bottom: 2px; }"
            ".details { color: #555; margin-bottom: 10px; }"
            "table { border-collapse: collapse; width: 100%; }"
            "th { background-color: #e0e0e0; text-align: left; "
            "padding: 4px 6px; border: 1px solid #999; font-size: 9pt; }"
            "td { padding: 3px 6px; border: 1px solid #ccc; font-size: 9pt; }"
            "tr:nth-child(even) { background-color: #f5f5f5; }"
            ".right { text-align: right; }"
            ".summary { margin-top: 10px; font-size: 9pt; color: #333; }"
            "</style></head><body>"
        )
        html += f"<h2>{vehicle_name}</h2>"
        if details:
            html += f"<div class='details'>{' &nbsp;|&nbsp; '.join(details)}</div>"

        html += (
            "<table><tr>"
            "<th>#</th><th>Date</th><th>Mileage</th><th>Category</th>"
            "<th>Description</th><th>Location</th>"
            "<th>Parts</th><th>Labor</th><th>Total</th>"
            "<th>Next Due</th><th>Notes</th>"
            "</tr>"
        )
        for i, r in enumerate(records, 1):
            mileage = f"{r['mileage']:,}" if r["mileage"] else ""
            next_parts = []
            if r["next_due_date"]:
                next_parts.append(r["next_due_date"])
            if r["next_due_mileage"]:
                next_parts.append(f"{r['next_due_mileage']:,} mi")
            html += (
                f"<tr>"
                f"<td class='right'>{i}</td>"
                f"<td>{r['date']}</td>"
                f"<td class='right'>{mileage}</td>"
                f"<td>{r['category'] or ''}</td>"
                f"<td>{r['description'] or ''}</td>"
                f"<td>{r['location'] or ''}</td>"
                f"<td class='right'>${r['parts_cost']:,.2f}</td>"
                f"<td class='right'>${r['labor_cost']:,.2f}</td>"
                f"<td class='right'>${r['total_cost']:,.2f}</td>"
                f"<td>{' / '.join(next_parts)}</td>"
                f"<td>{r['notes'] or ''}</td>"
                f"</tr>"
            )
        html += "</table>"

        # Summary line
        parts = [f"Records: {summary['count']}"]
        parts.append(f"Total Spent: ${summary['total_spent']:,.2f}")
        if summary["min_mileage"] and summary["max_mileage"]:
            parts.append(
                f"Mileage Range: {summary['min_mileage']:,} – {summary['max_mileage']:,}"
            )
        html += f"<div class='summary'>{' &nbsp;|&nbsp; '.join(parts)}</div>"
        html += "</body></html>"

        self._print_html = html

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        preview = QPrintPreviewDialog(printer, self)
        preview.setWindowTitle(f"Print — {vehicle_name}")
        preview.paintRequested.connect(self._render_print)
        preview.exec()

    def _render_print(self, printer):
        doc = QTextDocument()
        doc.setHtml(self._print_html)
        doc.setPageSize(printer.pageRect(QPrinter.Point).size())
        doc.print_(printer)

    # ── Import ─────────────────────────────────────────────────────

    def _import_csv(self):
        if self.current_vehicle_id is None:
            QMessageBox.information(
                self, "No Vehicle",
                "Please add or select a vehicle first.\n\n"
                "The imported records will be added to the currently selected vehicle."
            )
            return

        v = self.db.get_vehicle(self.current_vehicle_id)
        vehicle_name = f"{v['year']} {v['make']} {v['model']}"

        dlg = ImportCSVDialog(self)
        if dlg.exec() == QDialog.Accepted:
            records = dlg.get_records()
            if not records:
                return

            # Confirm before importing
            reply = QMessageBox.question(
                self, "Confirm Import",
                f"Import {len(records)} records into:\n{vehicle_name}?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
            )
            if reply != QMessageBox.Yes:
                return

            count = 0
            for r in records:
                try:
                    self.db.add_record(self.current_vehicle_id, **r)
                    count += 1
                except Exception as e:
                    print(f"Skipped record: {e}")

            self._refresh_table()
            self.statusBar().showMessage(
                f"Imported {count} records into {vehicle_name}.", 5000
            )
            QMessageBox.information(
                self, "Import Complete",
                f"Successfully imported {count} of {len(records)} records."
            )

    # ── Settings ─────────────────────────────────────────────────────

    def _open_settings(self):
        old_path = config.get_db_path()
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.Accepted:
            new_path = dlg.get_new_path()
            if new_path == old_path:
                return

            # Copy existing database to new location if requested
            if dlg.should_copy() and os.path.exists(old_path):
                # Warn if target already exists
                if os.path.exists(new_path):
                    reply = QMessageBox.warning(
                        self, "Overwrite Warning",
                        f"A database already exists at:\n{new_path}\n\n"
                        "Copying will OVERWRITE that file. Continue?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
                    )
                    if reply != QMessageBox.Yes:
                        return
                try:
                    # Make sure the target directory exists
                    os.makedirs(os.path.dirname(os.path.abspath(new_path)), exist_ok=True)
                    shutil.copy2(old_path, new_path)
                except OSError as e:
                    QMessageBox.critical(
                        self, "Copy Failed",
                        f"Could not copy database to new location:\n{e}\n\n"
                        "Settings were not changed."
                    )
                    return

            # Save the new path to config
            config.set("db_path", new_path)

            # Reopen with new database
            self.db.close()
            self.db = Database(new_path)
            self.current_vehicle_id = None
            self._refresh_vehicle_list()
            self.statusBar().showMessage(f"Database: {new_path}", 5000)

            QMessageBox.information(
                self, "Settings Saved",
                f"Database location updated to:\n{new_path}\n\n"
                "The app is now using the new database."
            )

    # ── Theme ──────────────────────────────────────────────────────

    def _change_theme(self):
        action = self.sender()
        theme_name = action.data()
        config.set("theme", theme_name)
        apply_theme(QApplication.instance(), theme_name)
        self.statusBar().showMessage(f"Theme changed to: {action.text()}", 3000)

    # ── Cleanup ─────────────────────────────────────────────────────

    def _backup_database(self):
        """Create a timestamped backup of the database file."""
        db_path = self.db.db_path
        if not os.path.exists(db_path):
            return

        backup_dir = os.path.join(os.path.dirname(db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_name = os.path.splitext(os.path.basename(db_path))[0]
        backup_path = os.path.join(backup_dir, f"{db_name}_backup_{timestamp}.db")

        try:
            shutil.copy2(db_path, backup_path)
        except OSError:
            return  # Silently fail on backup — don't block closing

        # Remove old backups beyond the max
        max_backups = config.get("max_backups") or 5
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.startswith(db_name) and f.endswith(".db")],
            reverse=True,
        )
        for old_backup in backups[max_backups:]:
            try:
                os.remove(os.path.join(backup_dir, old_backup))
            except OSError:
                pass

    def closeEvent(self, event):
        if config.get("auto_backup"):
            self._backup_database()
        self.db.close()
        event.accept()


# ════════════════════════════════════════════════════════════════════
#  Entry Point
# ════════════════════════════════════════════════════════════════════

def _resolve_db_path():
    """Validate the configured db path. Fall back to default if it's bad."""
    db_path = config.get_db_path()
    default_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "vehicle_maintenance.db"
    )

    # Check if the configured path's directory exists
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if os.path.exists(db_dir):
        return db_path

    # Directory doesn't exist — fall back to default
    print(f"Database path not accessible: {db_path}")
    print(f"Falling back to default: {default_path}")
    config.set("db_path", "")
    return default_path


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Vehicle Maintenance Log")
    app.setOrganizationName("VehicleLog")

    # Use the system style for native look
    app.setStyle("Fusion")

    # Apply saved color theme
    apply_theme(app, config.get("theme") or "system")

    # Load and validate database path
    db_path = _resolve_db_path()
    db = Database(db_path)

    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

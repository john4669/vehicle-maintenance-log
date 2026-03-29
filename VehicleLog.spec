# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Vehicle Maintenance Log."""

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon_256.png', '.'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VehicleMaintenanceLog',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon='icon.ico',         # .exe file icon
)

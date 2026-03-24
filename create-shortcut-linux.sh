#!/bin/bash
# Creates a desktop shortcut for Vehicle Maintenance Log
# Run this once from the project folder

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_FILE="$HOME/Desktop/VehicleLog.desktop"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Vehicle Maintenance Log
Comment=Track vehicle maintenance, costs, and service history
Exec=bash -c 'cd "$APP_DIR" && ./VehicleLog.sh'
Icon=$APP_DIR/icon_256.png
Terminal=false
Type=Application
Categories=Utility;Office;
EOF

chmod +x "$DESKTOP_FILE"

# Some Linux desktops require this to trust the shortcut
if command -v gio &> /dev/null; then
    gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null
fi

echo "Desktop shortcut created: $DESKTOP_FILE"
echo
echo "Note: Your desktop environment may ask you to 'Trust' or"
echo "'Allow Launching' when you first double-click the shortcut."

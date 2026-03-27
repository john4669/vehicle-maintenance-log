#!/bin/bash
# Creates a macOS .app bundle for Vehicle Maintenance Log
# Run this once from the project folder after running setup.sh

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Vehicle Maintenance Log"
APP_BUNDLE="$HOME/Desktop/${APP_NAME}.app"

echo "Creating macOS app bundle..."

# Create .app bundle structure
mkdir -p "${APP_BUNDLE}/Contents/MacOS"
mkdir -p "${APP_BUNDLE}/Contents/Resources"

# Create Info.plist
cat > "${APP_BUNDLE}/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.vehiclelog.app</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>VehicleLog</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create launcher script
cat > "${APP_BUNDLE}/Contents/MacOS/VehicleLog" << EOF
#!/bin/bash
cd "${APP_DIR}"

if [ ! -f "venv/bin/python" ]; then
    osascript -e 'display dialog "The app has not been set up yet.\nPlease run setup.sh first." buttons {"OK"} default button "OK" with icon stop with title "Vehicle Maintenance Log"'
    exit 1
fi

venv/bin/python main.py
EOF
chmod +x "${APP_BUNDLE}/Contents/MacOS/VehicleLog"

# Generate .icns icon from icon_256.png using macOS built-in tools
ICONSET_DIR=$(mktemp -d)/icon.iconset
mkdir -p "$ICONSET_DIR"

if command -v sips &> /dev/null && [ -f "${APP_DIR}/icon_256.png" ]; then
    sips -z 16 16     "${APP_DIR}/icon_256.png" --out "${ICONSET_DIR}/icon_16x16.png"      > /dev/null 2>&1
    sips -z 32 32     "${APP_DIR}/icon_256.png" --out "${ICONSET_DIR}/icon_16x16@2x.png"   > /dev/null 2>&1
    sips -z 32 32     "${APP_DIR}/icon_256.png" --out "${ICONSET_DIR}/icon_32x32.png"      > /dev/null 2>&1
    sips -z 64 64     "${APP_DIR}/icon_256.png" --out "${ICONSET_DIR}/icon_32x32@2x.png"   > /dev/null 2>&1
    sips -z 128 128   "${APP_DIR}/icon_256.png" --out "${ICONSET_DIR}/icon_128x128.png"    > /dev/null 2>&1
    sips -z 256 256   "${APP_DIR}/icon_256.png" --out "${ICONSET_DIR}/icon_128x128@2x.png" > /dev/null 2>&1
    sips -z 256 256   "${APP_DIR}/icon_256.png" --out "${ICONSET_DIR}/icon_256x256.png"    > /dev/null 2>&1

    iconutil -c icns "$ICONSET_DIR" -o "${APP_BUNDLE}/Contents/Resources/icon.icns" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "  App icon set."
    else
        echo "  Warning: Could not generate .icns icon. App will use default icon."
    fi
    rm -rf "$(dirname "$ICONSET_DIR")"
else
    echo "  Warning: icon_256.png not found or sips not available. App will use default icon."
fi

echo
echo "App bundle created: ${APP_BUNDLE}"
echo
echo "You can now double-click '${APP_NAME}' on your Desktop to launch."
echo
echo "Note: macOS may ask you to allow the app to run since it is from"
echo "an unidentified developer. Go to System Settings > Privacy & Security"
echo "and click 'Open Anyway', or right-click the app and choose 'Open'."

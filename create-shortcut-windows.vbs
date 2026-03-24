Set ws = WScript.CreateObject("WScript.Shell")
appDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\"
desktopPath = ws.SpecialFolders("Desktop")
shortcutPath = desktopPath & "\Vehicle Maintenance Log.lnk"

Set sc = ws.CreateShortcut(shortcutPath)
sc.TargetPath = appDir & "VehicleLog.bat"
sc.WorkingDirectory = appDir
sc.IconLocation = appDir & "icon.ico, 0"
sc.Description = "Track vehicle maintenance, costs, and service history"
sc.Save

MsgBox "Desktop shortcut created!", vbInformation, "Vehicle Maintenance Log"

Set ws = CreateObject("WScript.Shell")
appDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\"
ws.CurrentDirectory = appDir
ws.Run """" & appDir & "venv\Scripts\python.exe"" main.py", 0, False

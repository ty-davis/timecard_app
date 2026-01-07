Set objShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strPath
objShell.Run """" & strPath & "\venv\Scripts\python.exe"" """ & strPath & "\app.py""", 0, False

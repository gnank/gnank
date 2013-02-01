Dim fso, loc, cmd, wsh

Set fso = CreateObject("Scripting.FileSystemObject")
loc = fso.GetAbsolutePathName(".")
'WScript.Echo loc

' pythonw.exe runs a Python script without showing a console window
cmd = "pythonw " + loc + "\src\gnank"
'WScript.Echo cmd

Set wsh = CreateObject("WScript.Shell")
wsh.Run cmd

CreateObject("WScript.Shell").Run "http://localhost:5173", 1, False
CreateObject("WScript.Shell").Run "cmd /c ""cd /d """"d:\train2\frontend"""" && """"D:\下载\New Folder\npm.cmd"""" run dev -- --port 5173""", 0, False

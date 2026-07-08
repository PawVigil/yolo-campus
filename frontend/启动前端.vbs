' 先清理旧进程，防止端口占用
CreateObject("WScript.Shell").Run "cmd /c taskkill /f /im node.exe >nul 2>&1", 0, False

CreateObject("WScript.Shell").Run "cmd /c ""cd /d """"d:\train2\frontend"""" && """"D:\下载\New Folder\npm.cmd"""" run dev -- --port 3100""", 0, False
CreateObject("WScript.Shell").Run "http://localhost:3100", 1, False

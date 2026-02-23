pip freeze > requirements.lock.txt
python .\tools\build.py

Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*.spec" -Force -ErrorAction SilentlyContinue

.\.venv\Scripts\pyinstaller.exe DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.py --noconsole --onefile --collect-all customtkinter --collect-all selenium --icon assets\icons\DMMGamePlayerFastLauncher.ico

Copy-Item -Path "dist\DMMGamePlayerFastLauncher.exe" -Destination "windows" -Force
Copy-Item -Path "assets" -Destination "windows" -Force -Recurse

Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kira-96/Inno-Setup-Chinese-Simplified-Translation/refs/heads/main/ChineseSimplified.isl" -OutFile "C:\Users\yuki\AppData\Local\Programs\Inno Setup 6\Languages\ChineseSimplified.isl"
Start-Process "C:\Users\yuki\AppData\Local\Programs\Inno Setup 6\ISCC.exe" "setup.iss" -Wait -NoNewWindow

Compress-Archive -Path "windows\*" -DestinationPath "dist\DMMGamePlayerFastLauncher.zip" -Force

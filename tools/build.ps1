pip freeze > requirements-lock.txt
python .\tools\build.py


pyinstaller DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.py --noconsole --onefile --add-data ".venv\Lib\site-packages\customtkinter\;customtkinter" --icon assets\icons\DMMGamePlayerFastLauncher.ico

Copy-Item -Path "dist\DMMGamePlayerFastLauncher.exe" -Destination "windows" -Force
Copy-Item -Path "assets" -Destination "windows" -Force -Recurse

Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kira-96/Inno-Setup-Chinese-Simplified-Translation/refs/heads/main/ChineseSimplified.isl" -OutFile "C:\Users\yuki\AppData\Local\Programs\Inno Setup 6\Languages\ChineseSimplified.isl"
Start-Process "C:\Users\yuki\AppData\Local\Programs\Inno Setup 6\ISCC.exe" "setup.iss" -Wait -NoNewWindow

Compress-Archive -Path "windows\*" -DestinationPath "dist\DMMGamePlayerFastLauncher.zip" -Force
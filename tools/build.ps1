black *.py
pip freeze > requirements.txt
python .\tools\build.py


pyinstaller DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.py --noconsole --onefile --add-data ".venv\Lib\site-packages\customtkinter\;customtkinter" --icon assets\icons\DMMGamePlayerFastLauncher.ico

# pyinstaller DMMGamePlayerProductIdChecker.py --onefile
# pyinstaller Task.py --onefile --noconsole
New-Item "windows\tools" -ItemType Directory -Force

# Copy-Item -Path "dist\DMMGamePlayerProductIdChecker.exe" -Destination "windows\tools" -Force
# Copy-Item -Path "dist\Task.exe" -Destination "windows\tools" -Force


Copy-Item -Path "assets" -Destination "windows" -Force -Recurse
Start-Process "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "setup.iss"
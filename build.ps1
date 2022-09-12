black *.py
pip freeze > requirements.txt
pyinstaller DMMGamePlayerFastLauncher.py --onefile --noconsole
pyinstaller DMMGamePlayerProductIdChecker.py --onefile
New-Item "Z:\Project\Python\hack\DMMGamePlayerFastLauncher\windows\tools" -ItemType Directory
Copy-Item -Path "Z:\Project\Python\hack\DMMGamePlayerFastLauncher\dist\DMMGamePlayerProductIdChecker.exe" -Destination "Z:\Project\Python\hack\DMMGamePlayerFastLauncher\windows\tools" -Force
start "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "Z:\Project\Python\hack\DMMGamePlayerFastLauncher\setup.iss"
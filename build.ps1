black *.py
pip freeze > requirements.txt
pyinstaller DMMGamePlayerFastLauncher.py --onefile --noconsole
pyinstaller DMMGamePlayerProductIdChecker.py --onefile
Copy-Item -Path "C:\Project\Python\hack\DMMGamePlayerFastLauncher\dist\DMMGamePlayerProductIdChecker.exe" -Destination "C:\Project\Python\hack\DMMGamePlayerFastLauncher\windows\tools" -Force
start "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "C:\Project\Python\hack\DMMGamePlayerFastLauncher\setup.iss"
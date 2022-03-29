black *.py
pip freeze > requirements.txt
pyinstaller DMMGamePlayerFastLauncher.py --onefile --noconsole
pyinstaller DMMGamePlayerProductIdChecker.py --onefile
start "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "C:\Project\DMMGamePlayerFastLauncher\setup.iss"
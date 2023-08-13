black *.py
pip freeze > requirements.txt
python .\tools\build.py


pyinstaller DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.py --noconsole --onefile --add-data ".venv\Lib\site-packages\customtkinter\;customtkinter"

# pyinstaller DMMGamePlayerProductIdChecker.py --onefile
# pyinstaller Task.py --onefile --noconsole
New-Item "Z:\Project\python\DMMGamePlayerFastLauncher\windows\tools" -ItemType Directory -Force

# Copy-Item -Path "Z:\Project\python\DMMGamePlayerFastLauncher\dist\DMMGamePlayerProductIdChecker.exe" -Destination "Z:\Project\Python\DMMGamePlayerFastLauncher\windows\tools" -Force
# Copy-Item -Path "Z:\Project\Python\DMMGamePlayerFastLauncher\dist\Task.exe" -Destination "Z:\Project\Python\DMMGamePlayerFastLauncher\windows\tools" -Force


Copy-Item -Path "Z:\Project\python\DMMGamePlayerFastLauncher\assets" -Destination "Z:\Project\python\DMMGamePlayerFastLauncher\windows" -Force -Recurse
Start-Process "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "Z:\Project\Python\DMMGamePlayerFastLauncher\setup.iss"
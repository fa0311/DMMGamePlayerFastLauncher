pip freeze > requirements.txt
python .\tools\build.py


pyinstaller DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.py --noconsole --onefile --add-data ".venv\Lib\site-packages\customtkinter\;customtkinter" --icon assets\icons\DMMGamePlayerFastLauncher.ico

Copy-Item -Path "dist\DMMGamePlayerFastLauncher.exe" -Destination "windows" -Force


Copy-Item -Path "assets" -Destination "windows" -Force -Recurse
Start-Process "C:\Users\yuki\AppData\Local\Programs\Inno Setup 6\ISCC.exe" "setup.iss"

@ECHO OFF

echo NOTE: This will install the pyinstaller package via pip.
echo Press any key to begin the build, close this window to cancel
pause

@ECHO ON
python -m pip install pyinstaller

@ECHO ON
pyinstaller --onefile --noconsole ../src/ttsfront.py
copy start_app_noconsole.bat dist

pause
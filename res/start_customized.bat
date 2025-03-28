TITLE Streamutils (CONSOLE) (Default window title)
cd ..

call .venv\Scripts\activate.bat
@ECHO ON

python src/ttsfront.py youtube.com/watch?v=jfKfPfyJRdk

call .venv\Scripts\deactivate.bat

@ECHO OFF
ECHO.
ECHO.
ECHO The program exited!
ECHO.
ECHO The return code is %ERRORLEVEL%
ECHO zero means success, nonzero means error
ECHO.
ECHO Paused to inspect crash log
ECHO Press any key to close this window
PAUSE

CD RES
@ECHO OFF

TITLE Streamutils (CONSOLE) (MSWIN)

@ECHO ON
python src/ttsfront.py -C res/defaultconfig.ini youtube.com/watch?v=jfKfPfyJRdk

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

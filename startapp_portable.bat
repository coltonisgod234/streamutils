@ECHO OFF

TITLE Streamutils (CONSOLE) (MSWIN)

@ECHO ON
python3 src/ttsfront.py -C res/defaultconfig.ini youtube.com/watch?v=jfKfPfyJRdk

@ECHO OFF
ECHO.
ECHO.
ECHO The program exited!
ECHO.
ECHO The return code is %ERRORLEVEL%
ECHO zero means success, nonzero means error
PAUSE
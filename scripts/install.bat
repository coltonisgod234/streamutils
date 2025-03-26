@ECHO OFF
TITLE Streamutils Online Installer (MSWIN)
PROMPT $g
COLOR 0a

ECHO DO NOT RUN THIS AS ADMIN!
ECHO.
ECHO This script requires winget (Windows 10 or newer)
ECHO This script will install the following winget packages:
ECHO - Python.Python
ECHO - Git.Git
ECHO.
PAUSE

ECHO Begining install...
@ECHO ON

winget install python
winget install Git.Git

git clone -v "https://github.com/coltonisgod234/streamutils" "%LocalAppData%\streamutils"
cd "%LocalAppData%\streamutils"

python -m venv .venv
call .venv\Scripts\activate.bat
@ECHO ON

pip install -r requirements.txt

call .venv\Scripts\deactivate.bat
@ECHO ON

mkdir custom
copy res\defaultconfig.ini custom\config.ini

set shortcutDir="%appdata%\Microsoft\Windows\Start Menu\Programs\Streamutils"
mkdir %shortcutDir%

set shortcutPath=%shortcutDir%\Start Streamutils.lnk
set shortcutTarget=%localappdata%\streamutils\res\start_customized.bat
set shortcutWorkdir=%localappdata%\streamutils\res

powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%shortcutPath%'); $s.TargetPath='%shortcutTarget%'; $s.WorkingDirectory='%shortcutWorkdir%'; $s.save()"

pause

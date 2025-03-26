@ECHO OFF
TITLE Streamutils Online Installer (MSWIN)
PROMPT $g

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
git pull -v

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

set shortcutWorkdir=%localappdata%\streamutils\res

REM START APP
set shortcutPath=%shortcutDir%\Start Streamutils.lnk
set shortcutTarget=%localappdata%\streamutils\res\start_customized.bat
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%shortcutPath%'); $s.TargetPath='%shortcutTarget%'; $s.WorkingDirectory='%shortcutWorkdir%'; $s.save()"


REM EDIT CONFIGURATION
set shortcutPath=%shortcutDir%\Edit Configuration.lnk
set shortcutTarget=%localappdata%\streamutils\custom\config.ini
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%shortcutPath%'); $s.TargetPath='%shortcutTarget%'; $s.WorkingDirectory='%shortcutWorkdir%'; $s.save()"


REM OPEN PLUGINS DIRECTORY
set shortcutPath=%shortcutDir%\Open Plugins Directory.lnk
set shortcutTarget=%localappdata%\streamutils\src\plugins
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%shortcutPath%'); $s.TargetPath='%shortcutTarget%'; $s.WorkingDirectory='%shortcutWorkdir%';; $s.save()"


REM OPEN APP DIRECTORY
set shortcutPath=%shortcutDir%\Open Application Directory.lnk
set shortcutTarget=%localappdata%\streamutils
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%shortcutPath%'); $s.TargetPath='%shortcutTarget%'; $s.WorkingDirectory='%shortcutWorkdir%'; $s.save()"

REM RERUN INSTALLER
set shortcutPath=%shortcutDir%\Rerun Installer.lnk
set shortcutTarget=%localappdata%\streamutils\scripts\install.bat
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%shortcutPath%'); $s.TargetPath='%shortcutTarget%'; $s.WorkingDirectory='%shortcutWorkdir%'; $s.save()"

@ECHO OFF
ECHO.
ECHO.
ECHO Successfully installed to:
ECHO %localappdata%\streamutils
ECHO.
ECHO A start menu folder has been created with the following shortcuts:
ECHO Use the "Start Streamutils" shortcut to start the application
ECHO Use the "Edit Configuration" shortcut to edit the config file
ECHO Use the "Open Plugins Directory" shortcut to open the plugins folder
ECHO Use the "Open App Directory" shortcut to open the installation folder
ECHO Use the "Rerun Installer" shortcut to update the application
ECHO.
ECHO Continue to open the configuration file in notepad.
ECHO Ignore the warning, the installer has taken care of copying the
ECHO config.
pause

@ECHO ON
notepad %localappdata%\streamutils\custom\config.ini

@ECHO ON
PROMPT exec...  

if [%1]==[] goto default_installpath
:default_installpath
	SET installdir="%LocalAppData%\streamutils"
	GOTO start_splash

SET installdir=%1

:start_splash
	@ECHO OFF
	TITLE Streamutils Online Installer (MSWIN)

	ECHO Usage: ^<installdir^>
	ECHO.
	ECHO Will install to following directory:
	ECHO %installdir%
	ECHO.
	ECHO This script requires Windows 10 or newer (requires winget)
	ECHO This script will install the following winget packages:
	ECHO - Python.Python
	ECHO - Git.Git
	ECHO.
	PAUSE
	GOTO begin

:begin
	ECHO Begining install...
	@ECHO ON
	GOTO winget

:winget
	winget install python
	winget install Git.Git
	GOTO clone

:clone
	git clone -v "https://github.com/coltonisgod234/streamutils" "%installdir"
	CD "%installdir"
	git pull -v
	GOTO make_venv

:make_venv
	python -m venv .venv
	GOTO install_pip_packages

:install_pip_packages
	CALL .venv\Scripts\activate.bat
	@ECHO ON

	pip install -r requirements.txt

	CALL .venv\Scripts\deactivate.bat
	@ECHO ON
	GOTO create_custom_dir

:create_custom_dir
	MD custom
	COPY res\defaultconfig.ini custom\config.ini
	GOTO create_all_shortcuts

:create_all_shortcuts
	CALL setup_shortcuts
	CALL shortcut_start_app
	CALL shortcut_edit_config
	CALL shortcut_open_plugins
	CALL shortcut_open_installdir
	CALL shortcut_update
	GOTO success_splash

:setup_shortcuts
	SET shortcutDir="%appdata%\Microsoft\Windows\Start Menu\Programs\Streamutils"
	MD %shortcutDir%

:func_make_shortcut
	powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%shortcutPath%'); $s.TargetPath='%shortcutTarget%'; $s.WorkingDirectory='%shortcutWorkdir%'; $s.save()"

:shortcut_start_app
	SET shortcutWorkdir="%installdir%\res"
	SET shortcutPath="%shortcutDir%\Start Streamutils.lnk"
	SET shortcutTarget="%installdir%\res\start_customized.bat"
	CALL func_make_shortcut

:shortcut_edit_config
	SET shortcutWorkdir="%installdir%\custom"
	SET shortcutPath=%shortcutDir%\Edit Streamutils Config.lnk
	SET shortcutTarget=%localappdata%\streamutils\custom\config.ini
	CALL func_make_shortcut

:shortcut_open_plugins
	SET shortcutWorkdir="%installdir%\custom"
	SET shortcutPath=%shortcutDir%\Open Streamutils Plugin Folder.lnk
	SET shortcutTarget=%localappdata%\streamutils\src\plugins
	CALL func_make_shortcut

:shortcut_open_installdir
	SET shortcutWorkdir="%installdir%"
	SET shortcutPath=%shortcutDir%\Open Streamutils Install Folder.lnk
	SET shortcutTarget=%localappdata%\streamutils
	CALL func_make_shortcut

:shortcut_update
	SET shortcutWorkdir="%installdir%"
	SET shortcutPath=%shortcutDir%\Update Streamutils.lnk
	SET shortcutTarget=%localappdata%\streamutils\scripts\update.bat
	CALL func_make_shortcut

:success_splash
	@ECHO OFF
	ECHO.
	ECHO.
	ECHO Successfully installed to:
	ECHO %installdir%
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

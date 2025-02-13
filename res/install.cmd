@echo OFF

echo ABOUT TO INSTALL TO C:\Program Files\Streamutils\
pause

prompt "$G "
@echo ON

python3 -m pip install -r .\requirements.txt
md "C:\Program Files\Streamutils\"
md "C:\Program Files\Streamutils\code"
md "C:\Program Files\Streamutils\plugins"

:: Copy code
copy ".\src\*" "C:\Program Files\Streamutils\code"

:: Copy plugins
copy ".\src\plugins\*" "C:\program files\streamutils\plugins"

:: Copy root-level resources
copy ".\res\*" "C:\program files\streamutils\"
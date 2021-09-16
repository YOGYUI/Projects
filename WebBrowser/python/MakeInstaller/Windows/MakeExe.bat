set PROJ_NAME=YWebBrowser

:: Remove existing build result
rd /s /q .\dist
rd /s /q .\dist
rd /s /q .\build
rd /s /q .\Compile

python Clean.py

:: Compile
pyinstaller %PROJ_NAME%.spec
python Compile.py

:: Copy Core Files
xcopy /s .\Compile\*.*          .\dist\%PROJ_NAME%\
xcopy /s ..\..\Resource\*.*    .\dist\%PROJ_NAME%\Resource\

:: Remove existing core files
rd /s /q .\Compile

pause
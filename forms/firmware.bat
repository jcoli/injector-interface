SETLOCAL ENABLEEXTENSIONS

avrdude.exe -C avrdude.conf -v -patmega2560 -cwiring -P %1 -b115200 -D -Uflash:w:%2

echo %ERRORLEVEL%

EXIT /B %ERRORLEVEL%


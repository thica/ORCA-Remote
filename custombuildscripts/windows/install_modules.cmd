@echo off
set licz=0
setlocal
for /f %%a in ('copy /Z "%~dpf0" nul') do @set "ASCII_13=%%a"
for /F %%a in ('echo prompt $E ^| cmd') do @set "ESC=%%a"
setlocal enabledelayedexpansion

SET red=%ESC%[1;31m
SET grn=%ESC%[1;32m
SET yel=%ESC%[1;33m
SET blu=%ESC%[1;34m
SET mag=%ESC%[1;35m
SET cyn=%ESC%[1;36m
SET end=%ESC%[0m

set WORKDIR=c:\BUILDTMP
set LOGFILE=%WORKDIR%\logfile.txt

call :PIP_INSTALL "future"
call :PIP_INSTALL "plyer"
call :PIP_INSTALL "rsa"
call :PIP_INSTALL "pyasn1"
call :PIP_INSTALL "wakeonlan"
call :PIP_INSTALL "ws4py"
call :PIP_INSTALL "httplib2"
call :PIP_INSTALL "pycparser"
call :PIP_INSTALL "mwclient"
call :PIP_INSTALL "netifaces"
call :PIP_INSTALL "pillow"
call :PIP_INSTALL "demjson"
call :PIP_INSTALL "adb-shell"
call :PIP_INSTALL "ifaddr"


:: Functions

:printf
set /p "=%~1!ASCII_13!" <NUL
goto :eof

:ECHO
echo %end%[ %yel%Info%end% ] %~1!
echo [ Info ] %~1! >>  %LOGFILE%
rem call :printf  "[${yel} Info ${end}] %~1!"
rem echo "[--Info] %~1!" >> "$LOGFILE"
EXIT /B 0
rem goto :eof

:PIP_INSTALL
call :printf "%end%[%yel% Info %end%] Installing (pip3) %~1 %~2 %~3 ....."
pip install %~1 %~2 %~3 >>%LOGFILE%

IF %ERRORLEVEL% EQU 0 (
  call :printf "%end%[%grn%  OK  %end%] Installing (pip3) %~1 %~2 %~3         "
  echo [
  echo "[ OK ] Installed (pip3) %~1 %~2 %~3" >>%LOGFILE%
) ELSE (
  call :printf "%end%[%red%Failed%end%] Installing (pip3) %~1 %~2 %~3           "
  echo [
  echo "[Failed] Installing (pip3) %~1 %~2 %~3" >>%LOGFILE%
  goto ABORT
)
EXIT /B 0


:ABORT
pause
EXIT /B 999
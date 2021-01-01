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

call:GetORCAVersion
call:GetORCABranch
call:CleanPyInstallerDirs
call:MakeCopyOfSources
goto:eof

:GetORCAVersion

for /f "delims== tokens=2" %%v in ('findstr self.sVersion= %SOURCEDIR%\src\ORCA\App.py') do (
    set version=%%v
    goto endfindORCAVersion
)
:endfindORCAVersion
set version=%version:"=%
setx version %version% > nul
call :ECHO "Found ORCA Version: %version%"
goto:eof
rem **************************************************************************************************************************************

:GetORCABranch
for /f "delims== tokens=2" %%v in ('findstr self.sBranch= %SOURCEDIR%\src\ORCA\App.py') do (
    set branch=%%v
    goto endfindORCABranch
)
:endfindORCABranch
set branch=%branch:"=%
setx branch %branch% > nul
call :ECHO "Found ORCA Branch: %branch%"
goto:eof
rem **************************************************************************************************************************************

:CleanPyInstallerDirs
set zipsrcdir=%pyinstallerdir%\dist\ORCA
call :ECHO "Cleaning files and folder"
rem echo  ...(%TARGETDIR%%)
rem del %TARGETDIR%%\*.* /S /Q > nul
call :ECHO "...(%TARGETDIR%)"
rmdir "%TARGETDIR%"  /S /Q 1>nul 2>nul
mkdir "%TARGETDIR%"
call :ECHO "...(%BUILDDIR%\work)"
rmdir "%BUILDDIR%\src\work" /S /Q 1>nul 2>nul
call :ECHO "...(%BUILDDIR%\dist)"
rmdir "%BUILDDIR%\dist" /S /Q 1>nul 2>nul
call :ECHO "...(%BUILDDIR%\build)"
rmdir "%BUILDDIR%\build" /S /Q 1>nul 2>nul
rem mkdir %BUILDDIR%\work 1> nul 2>nul
call :ECHO "Cleaning files and folder (Done)"
goto:eof
rem **************************************************************************************************************************************

:MakeCopyOfSources
call :ECHO "Creating working copy of ORCA SRC files"
call :ECHO "... Copy files and creating folder structure (%SOURCEDIR% to %TARGETDIR%%)"
xcopy /Y %SOURCEDIR%\src\*.py %TARGETDIR% /q >> %LOGFILE%
xcopy /Y %SOURCEDIR%\src\*.txt %TARGETDIR% /q >> %LOGFILE%
mkdir %TARGETDIR%\languages
xcopy /Y %SOURCEDIR%\src\languages %TARGETDIR%\languages /S /q >> %LOGFILE%
mkdir %TARGETDIR%\actions
copy /Y %SOURCEDIR%\src\actions\actionsfallback.xml %TARGETDIR%\actions >> %LOGFILE%
mkdir %TARGETDIR%\ORCA
xcopy /Y %SOURCEDIR%\src\ORCA %TARGETDIR%\ORCA /S /q >> %LOGFILE%
rem mkdir %TARGETDIR%\interfacestmp
rem xcopy /Y %SOURCEDIR%\src\interfaces %TARGETDIR%\interfacestmp /S /q
rem mkdir %TARGETDIR%\scriptstmp
rem xcopy /Y %SOURCEDIR%\src\scripts %TARGETDIR%\scriptstmp /S /q
rem mkdir %TARGETDIR%\Platform
rem copy /Y %SOURCEDIR%\src\ORCA\utils\Platform %TARGETDIR%\Platform /S /q

copy /Y "%SOURCEDIR%\custombuildscripts\windows\orcafullscreen.cmd" %TARGETDIR% >> %LOGFILE%
call :ECHO "Finished copy files"
goto:eof

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
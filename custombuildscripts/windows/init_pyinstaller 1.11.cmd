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

if not EXIST "%WORKDIR%\" mkdir %WORKDIR%

call :ECHO "Logging to %LOGFILE%"

cd "%WORKDIR%"
set SOURCEDIR=%WORKDIR%\githubsources
set TARGETDIR=%WORKDIR%\buildsources
set BUILDDIR=%WORKDIR%\builddest
set SNAPSHOTDIR=\media\snapshots
set SECRETSDIR=\media\secrets

rem to bypass some pyinstaller __pycache__ errors
set PYTHONDONTWRITEBYTECODE=1

rem echo "Reading Secrets"
rem echo "Reading Secrets" >> %LOGFILE%
rem source "$SECRETSDIR/secrets.ini"

if EXIST "%BUILDDIR%\" (
    call :ECHO "Reusing existing build"
    set FROMSCRATCH=0
) ELSE (
    call :ECHO "Building from scratch"
    set FROMSCRATCH=1
)
if %FROMSCRATCH% EQU 1 (
    call :ECHO "Create Folder"
    mkdir "%SOURCEDIR%" >> %LOGFILE%
    mkdir "%TARGETDIR%" >> %LOGFILE%
    mkdir "%BUILDDIR%" >> %LOGFILE%
)

call :ECHO "Copy sources"
rem xcopy /E /S /Y /Q \media\Master "%SOURCEDIR%"  >> %LOGFILE%
robocopy /mir  /XD "\media\Master\.git" \media\Master "%SOURCEDIR%"


call :ECHO "Run custom script to prepare sources"
call "%SOURCEDIR%\custombuildscripts\windows\prepare_sources.cmd"

rem we always launch the python install, as it skips installation, but set the paths, if python is already installed
call :PYTHON_INSTALL

if %FROMSCRATCH% EQU 1 (
Rem Install Kivy Dependencies Upgrade pip
call :PIP_INSTALL --upgrade pip
REM Install/Upgrade Kivy Dependencies wheel Version 0.33.6
call :PIP_INSTALL --upgrade "wheel==0.33.6"
REM Install/Upgrade Kivy Dependencies setuptools Version 40.6.2
call :PIP_INSTALL --upgrade "setuptools==40.6.2"
rem Install Kivy Dependencies Upgrade virtualenv Version 16.7.8
call :PIP_INSTALL --upgrade "virtualenv==16.7.8"
rem Install Kivy Dependencies docutils Version 0.15.2
call :PIP_INSTALL "docutils==0.15.2"
rem Install Kivy Dependencies pygments Version 2.5.2
call :PIP_INSTALL "pygments==2.5.2"
rem Install Kivy Dependencies pypiwin32 Version 223
call :PIP_INSTALL "pypiwin32==223"
call :PIP_INSTALL "pywin32==227"
rem Install Kivy Dependencies kivy_deps.sdl2 Version 0.1.22
call :PIP_INSTALL "kivy_deps.sdl2==0.1.22"
rem Install Kivy Dependencies kivy_deps.glew
call :PIP_INSTALL "docutils"
call :PIP_INSTALL "kivy_deps.glew==0.1.12"
rem Install Kivy Dependencies kivy_deps.angle
call :PIP_INSTALL "kivy_deps.angle==0.1.9"
rem verify if we need this
rem Install ffpyplayer Version 4.3.0
call :PIP_INSTALL "ffpyplayer==4.3.0"
rem Install GStreamer Version 0.1.17
call :PIP_INSTALL "kivy_deps.gstreamer==0.1.17"
rem Install Kivy Version 1.11.0
call :PIP_INSTALL "kivy==1.11.0"

rem Install OpenCv (for testing)
pip3 install opencv-python >> %LOGFILE%
rem Install pyinstaller Version 3.5
call :PIP_INSTALL "pyinstaller==3.5"
call :ECHO "Run custom script to install further modules required by the app"
call "%SOURCEDIR%\custombuildscripts\windows\install_modules.cmd"
)

call :ECHO "Copy windows.spec file to target folder (root)  %SOURCEDIR%\custombuildscripts\windows\windows.spec to %BUILDDIR%\windows.spec "
copy "%SOURCEDIR%\custombuildscripts\windows\windows.spec" "%BUILDDIR%\windows.spec" >> %LOGFILE%

call :ECHO  "Delete __pychache__ folder those might confuse pyinstaller"
cd %TARGETDIR%
python -c "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"

call :ECHO  "Run PyInstaller"
cd %BUILDDIR%
python -B -m PyInstaller --name KivyAppAndroid windows.spec

call :ECHO "Finalize Binary"
call "%SOURCEDIR%\custombuildscripts\windows\prepare_binaries.cmd"

call :ECHO "Done/Finished"

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

:PYTHON_INSTALL
call :printf "%end%[%yel% Info %end%] Installing Python3 ....."
if not EXIST "%WORKDIR%\Python\" (
     mkdir %WORKDIR%\Python
     "%SNAPSHOTDIR%\python-3.7.4-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=%WORKDIR%\Python  >> %LOGFILE%
     echo %end%[%grn%  OK  %end%] Installed Python3
     echo "[  OK  ] Installed Python3         " >>%LOGFILE%
) ELSE (
     echo %end%[%grn%  OK  %end%] Skipped installing Python3
     echo "[  OK  ] Skipped installing Python3         " >>%LOGFILE%
)
set path=%path%;%WORKDIR%\Python
set path=%path%;%WORKDIR%\Python\scripts

EXIT /B 0


:ABORT
pause
EXIT /B 999
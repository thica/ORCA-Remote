@echo off
set WORKDIR=c:\BUILDTMP
set LOGFILE=%WORKDIR%\logfile.txt
mkdir %WORKDIR%

echo Logging to %LOGFILE%
echo "Start Log:" > %LOGFILE%

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

rem if [ -d "${BUILDDIR}" ]
rem then
rem     echo "Reusing existing build"
rem      export "FROMSCRATCH=0"
rem else
     echo Building from scratch
     set "FROMSCRATCH=1"
rem # fi

rem  if [ "$FROMSCRATCH" == "1" ]
rem then
    echo Create Folder
    echo "Create Folder" >> %LOGFILE%
    mkdir "%SOURCEDIR%" >> %LOGFILE%
    mkdir "%TARGETDIR%" >> %LOGFILE%
    mkdir "%BUILDDIR%" >> %LOGFILE%
rem fi

echo Copy sources
echo "Copy sources" >> %LOGFILE%
xcopy /E /S /Y /Q \media\Master "%SOURCEDIR%"  >> %LOGFILE%

echo Run custom script to prepare sources
echo "Run custom script to prepare sources" >> %LOGFILE%
call "%SOURCEDIR%\custombuildscripts\windows\prepare_sources.cmd"

echo we install python 3
mkdir Python
"%SNAPSHOTDIR%\python-3.7.4-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=%WORKDIR%\Python  >> %LOGFILE%
set path=%path%;%WORKDIR%\Python
set path=%path%;%WORKDIR%\Python\scripts

echo Install Kivy Dependencies Upgrade pip
pip3 install --upgrade pip  >> %LOGFILE%
COLOR

echo Install/Upgrade Kivy Dependencies wheel Version 0.33.6
pip3 install --upgrade wheel==0.33.6 >> %LOGFILE%

echo Install/Upgrade Kivy Dependencies setuptools Version 40.6.2
pip3 install --upgrade setuptools==40.6.2 >> %LOGFILE%

echo Install Kivy Dependencies Upgrade virtualenv Version 16.7.8
pip3 install --upgrade virtualenv==16.7.8 >> %LOGFILE%

echo Install Kivy Dependencies docutils Version 0.15.2
pip3 install docutils==0.15.2 >> %LOGFILE%

echo Install Kivy Dependencies pygments Version 2.5.2
pip3 install pygments==2.5.2 >> %LOGFILE%

echo Install Kivy Dependencies pypiwin32 Version 223
pip3 install pypiwin32==223 pywin32==227 >> %LOGFILE%

echo Install Kivy Dependencies kivy_deps.sdl2 Version 0.1.22
pip3 install kivy_deps.sdl2===0.1.22 >> %LOGFILE%

echo Install Kivy Dependencies kivy_deps.glew
pip3 install docutils kivy_deps.glew==0.1.12 >> %LOGFILE%

echo Install Kivy Dependencies kivy_deps.angle
pip3 install kivy_deps.angle==0.1.9 >> %LOGFILE%

rem verify if we need this
echo Install ffpyplayer Version 4.3.0
pip3 install ffpyplayer==4.3.0 >> %LOGFILE%

echo Install GStreamer Version 0.1.17
pip3 install kivy_deps.gstreamer==0.1.17 >> %LOGFILE%

echo Install Kivy Version 1.11.0
pip3 install kivy==1.11.0 >> %LOGFILE%

echo Install OpenCv (for testing)
pip3 install opencv-python >> %LOGFILE%

echo Install pyinstaller Version 3.5
pip3 install pyinstaller==3.5 >> %LOGFILE%

echo Run custom script to install further modules required by the app
echo "Run custom script to install further modules required by the app" >> %LOGFILE%
call "%SOURCEDIR%\custombuildscripts\windows\install_modules.cmd"

echo Copy windows.spec file to target folder (root)
copy %SOURCEDIR%\custombuildscripts\windows\windows.spec %BUILDDIR%\windows.spec >> %LOGFILE%

echo Delete __pychache__ folder those might confuse pyinstaller
cd %TARGETDIR%
python3 -c "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"


echo Run PyInstaller
cd %BUILDDIR%
python -B -m PyInstaller --name KivyAppAndroid windows.spec

echo Finalize Binary
echo "Finalize Binary" >> %LOGFILE%
call "%SOURCEDIR%\custombuildscripts\windows\prepare_binaries.cmd"

echo Done/Finished
echo "Done/Finished" >> %LOGFILE%


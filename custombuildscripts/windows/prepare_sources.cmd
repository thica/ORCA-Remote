rem SETLOCAL EnableDelayedExpansion

call:GetORCAVersion
call:GetORCABranch
call:CleanPyInstallerDirs
call:MakeCopyOfSources
echo "Finished copy"
goto:eof

:GetORCAVersion

for /f "delims== tokens=2" %%v in ('findstr self.sVersion= %SOURCEDIR%\src\ORCA\App.py') do (
    set version=%%v
    goto endfindORCAVersion
)
:endfindORCAVersion
set version=%version:"=%
setx version %version% > nul
echo Found ORCA Version: %version%
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
echo Found ORCA Branch: %branch%
goto:eof
rem **************************************************************************************************************************************

:CleanPyInstallerDirs
set zipsrcdir=%pyinstallerdir%\dist\ORCA
Echo Cleaning files and folder
rem echo  ...(%TARGETDIR%%)
rem del %TARGETDIR%%\*.* /S /Q > nul
echo  ...(%TARGETDIR%)
rmdir "%TARGETDIR% 1>nul 2>nul
mkdir "%TARGETDIR%
echo  ...(%BUILDDIR%\work)
rmdir "%BUILDDIR%\src\work" /S /Q 1>nul 2>nul
echo  ...(%BUILDDIR%\dist)
rmdir "%BUILDDIR%\dist" /S /Q 1>nul 2>nul
echo  ...(%BUILDDIR%\build)
rmdir "%BUILDDIR%\build" /S /Q 1>nul 2>nul
rem mkdir %BUILDDIR%\work 1> nul 2>nul
Echo Cleaning files and folder (Done)
goto:eof
rem **************************************************************************************************************************************

:MakeCopyOfSources
echo Creating working copy of ORCA SRC files
echo  ... Copy files and creating folder structure (%SOURCEDIR% to %TARGETDIR%%)
xcopy /Y %SOURCEDIR%\src\*.py %TARGETDIR% /q
xcopy /Y %SOURCEDIR%\src\*.txt %TARGETDIR%/q
mkdir %TARGETDIR%\languages
xcopy /Y %SOURCEDIR%\src\languages %TARGETDIR%\languages /S /q
mkdir %TARGETDIR%\actions
copy /Y %SOURCEDIR%\src\actions\actionsfallback.xml %TARGETDIR%\actions
mkdir %TARGETDIR%\ORCA
xcopy /Y %SOURCEDIR%\src\ORCA %TARGETDIR%\ORCA /S /q
rem /exclude:"%SOURCEDIR%\custombuildscripts\windows\exludepyc.txt
mkdir %TARGETDIR%\interfacestmp
xcopy /Y %SOURCEDIR%\src\interfaces %TARGETDIR%\interfacestmp /S /q
rem /exclude:"%SOURCEDIR%\custombuildscripts\windows\exludepyc.txt
mkdir %TARGETDIR%\scriptstmp
xcopy /Y %SOURCEDIR%\src\scripts %TARGETDIR%\scriptstmp /S /q
rem /exclude:"%SOURCEDIR%\custombuildscripts\windows\exludepyc.txt

mkdir %TARGETDIR%\Platform
xcopy /Y %SOURCEDIR%\src\ORCA\utils\Platform %TARGETDIR%\Platform /S /q

copy /Y "%SOURCEDIR%\custombuildscripts\windows\orcafullscreen.cmd" %TARGETDIR%
echo Finished copy files
goto:eof

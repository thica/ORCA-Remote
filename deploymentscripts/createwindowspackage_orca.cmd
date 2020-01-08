@echo off
SETLOCAL EnableDelayedExpansion

set KIVYVERSION=Kivy27

call:FindSourcesPath
call:FindPyInstaller
rem call:FindKivy
call:FindZIP
call:GetORCAVersion
call:GetORCABranch
call:CleanPyInstallerDirs
call:MakeCopyOfSources
call:CreatePyInstallerSpecFile
call:RunPyInstaller
call:CreateWindowsZipFile
pause
goto:eof
rem **************************************************************************************************************************************
:FindPyInstaller

for %%p in (c d e f g h i j k l m n o p q r s t u v w x y z) do if exist %%p:\dev\pyinstaller\nul (
set pyinstallerdir=%%p:\dev\pyinstaller
GOTO FOUNDPYINSTALLER
)
echo Can't find pyinstaller, creating at c:
mkdir c:\dev\pyinstaller
set pyinstallerdir=c:\dev\pyinstaller

:FOUNDPYINSTALLER
echo Found pyinstaller at %pyinstallerdir%
goto:eof
rem **************************************************************************************************************************************

:FindKivy
for %%p in (c d e f g h i j k l m n o p q r s t u v w x y z) do if exist %%p:\dev\%KIVYVERSION%\nul (
set kivypath=%%p:\dev\%KIVYVERSION%

if "%KIVYVERSION%" EQU "Kivy27" (
 set kivybat=!kivypath!\kivy-2.7.bat
 GOTO FOUNDKIVY
 )
if "%KIVYVERSION%" EQU "Kivy34" (
 set kivybat=!kivypath!\kivy-3.4.bat
 GOTO FOUNDKIVY
 )
)

echo Can't find kivy (%KIVYVERSION%)
pause 
exit

:FOUNDKIVY
echo Found Kivy at %kivypath% using %kivybat%
goto:eof
rem **************************************************************************************************************************************

:FindZIP
for %%p in (c d e f g h i j k l m n o p q r s t u v w x y z) do if exist "%%p:\Program Files\7-Zip\7z.exe" (
set zipprg=%%p:\Program Files\7-Zip\7z.exe
GOTO FOUNDZIP
)

for %%p in (c d e f g h i j k l m n o p q r s t u v w x y z) do if exist "%%p:\Program Files (x86)\7-Zip\7z.exe" (
set zipprg="%%p:\Program Files (x86)\7-Zip\7z.exe"
GOTO FOUNDZIP
)


pause Can't find 7ZIP
exit

:FOUNDZIP
echo Found 7ZIP at %zipprg%
goto:eof
rem **************************************************************************************************************************************
:GetORCAVersion

for /f "delims== tokens=2" %%v in ('findstr self.sVersion= %abspath%\src\ORCA\app.py') do (
    set version=%%v
    goto endfindORCAVersion
)

:endfindORCAVersion
set version=%version:"=%
echo Found ORCA Version: %version%
goto:eof
rem **************************************************************************************************************************************

:GetORCABranch
for /f "delims== tokens=2" %%v in ('findstr self.sBranch= %abspath%\src\ORCA\app.py') do (
    set branch=%%v
    goto endfindORCABranch
)

:endfindORCABranch
set branch=%branch:"=%

echo Found ORCA Branch: %branch%
goto:eof
rem **************************************************************************************************************************************

:FindSourcesPath
for %%A in ("%~dp0.\..") do set abspath=%%~fA
set srcgitdir=%abspath%\src
echo Sources Path is: %abspath% [%srcgitdir%]
goto:eof
rem **************************************************************************************************************************************
:CleanPyInstallerDirs
set zipsrcdir=%pyinstallerdir%\dist\ORCA
Echo Cleaning old PyInstaller files and folder 
echo  ...(%zipsrcdir%)
del %zipsrcdir%\*.* /S /Q > nul
echo  ...(%pyinstallerdir%\ORCA)
rmdir "%pyinstallerdir%\ORCA" /S /Q > nul
echo  ...(%pyinstallerdir%\work)
rmdir "%pyinstallerdir%\work" /S /Q > nul
echo  ...(%pyinstallerdir%\dist)
rmdir "%pyinstallerdir%\dist" /S /Q > nul
echo  ...(%pyinstallerdir%\build)
rmdir "%pyinstallerdir%\build" /S /Q > nul



rem echo  ...(%APPDATA%\pyinstaller\*.*)
rem del "%APPDATA%\pyinstaller\*.*" /S /Q > nul >>nul
rem echo ...(%APPDATA%\pyinstaller)
rem rmdir "%APPDATA%\pyinstaller" /S /Q >nul >>nul
rem mkdir %pyinstallerdir%\ORCA
mkdir %pyinstallerdir%\work
goto:eof
rem **************************************************************************************************************************************

:MakeCopyOfSources

Echo Creating working copy of ORCA SRC files 
set srcdir=%pyinstallerdir%\work
echo  ... Copy files and creating folder structure (%srcgitdir% to %srcdir%)
xcopy %srcgitdir%\*.py %srcdir% /q >nul
xcopy %srcgitdir%\*.txt %srcdir% /q >nul
mkdir %srcdir%\languages
xcopy %srcgitdir%\languages %srcdir%\languages /S /q >nul
mkdir %srcdir%\actions
copy %srcgitdir%\actions\actionsfallback.xml %srcdir%\actions > nul
mkdir %srcdir%\ORCA
echo .pyc >> %pyinstallerdir%\exludepyc.txt
xcopy %srcgitdir%\ORCA %srcdir%\ORCA /S /q /exclude:%pyinstallerdir%\exludepyc.txt>nul
mkdir %srcdir%\interfacestmp
xcopy %srcgitdir%\interfaces %srcdir%\interfacestmp /S /q /exclude:%pyinstallerdir%\exludepyc.txt>nul
mkdir %srcdir%\scriptstmp
xcopy %srcgitdir%\scripts %srcdir%\scriptstmp /S /q /exclude:%pyinstallerdir%\exludepyc.txt>nul

copy %abspath%\..\orcafullscreen.cmd %srcdir% >nul
echo Finished copy files
goto:eof
rem **************************************************************************************************************************************

:CreatePyInstallerSpecFile

set spec=%pyinstallerdir%\ORCA.spec
set pysrc=%srcdir%\main.py
set pysrc=%pysrc:\=\\%



set pysrcdir=%srcdir%/
set pysrcdir=%pysrcdir:\=/%
set pysrc2=%srcdir%
set pyinstallerdirpy=%pyinstallerdir%\ORCA
set pyinstallerdirpy=%pyinstallerdirpy:\=\\%


rem We create the spec file manually.
echo # -*- mode: python -*- > %spec%
echo from kivy.deps import sdl2, glew, gstreamer >> %spec%
echo from os import listdir  >> %spec%
echo from os.path import isdir  >> %spec%
echo from os.path import join  >> %spec%

echo def GetInterFaces():  >> %spec%
echo     oDirList = [] >> %spec%
echo     uRootDir = '%pysrcdir%'+'interfacestmp' >> %spec%
echo     for oItem in listdir(uRootDir): >> %spec%
echo         if isdir(join(uRootDir, oItem)): >> %spec%
echo             oDirList.append(uRootDir + '/' + oItem + '/interface.py' ) >> %spec%
echo     return oDirList >> %spec%
echo def GetScripts():  >> %spec%
echo     oDirList = [] >> %spec%
echo     uRootDir = '%pysrcdir%'+'scriptstmp' >> %spec%
echo     for oItem in listdir(uRootDir): >> %spec%
echo         if isdir(join(uRootDir, oItem)): >> %spec%
echo             oDirList.append(uRootDir + '/' + oItem + '/script.py' ) >> %spec%
echo     return oDirList >> %spec%
echo def GetPlatforms():  >> %spec%
echo     oDirList = [] >> %spec%
echo     uRootDir = '%pyinstallerdirpy%'+'utils/Flatform/generic*.*' >> %spec%
echo     for oItem in listdir(uRootDir): >> %spec%
echo         if not isdir(join(uRootDir, oItem)): >> %spec%
echo             oDirList.append('ORCA.utils.Platform.'+ oItem) >> %spec%
echo     uRootDir = '%pyinstallerdirpy%'+'utils/Flatform/generic*.*' >> %spec%
echo     for oItem in listdir(uRootDir): >> %spec%
echo         if not isdir(join(uRootDir, oItem)): >> %spec%
echo             oDirList.append(uRootDir + '/' + oItem + '/script.py' ) >> %spec%
echo     return oDirList >> %spec%


echo block_cipher = None >> %spec%
echo import kivy.core.video >> %spec%
echo a = Analysis(['%pysrc%'] + GetInterFaces()  + GetScripts(),  >> %spec%
echo               pathex=['%pyinstallerdirpy%'],binaries=[],datas=[], >> %spec%
echo               hiddenimports=['ORCA.utils.Platform.generic_cRotation', >> %spec% 
echo                              'ORCA.utils.Platform.generic_GetDefaultNetworkCheckMode', >> %spec%
echo                              'ORCA.utils.Platform.generic_GetDefaultStretchMode', >> %spec%
echo                              'ORCA.utils.Platform.generic_GetInstallationDataPath', >> %spec%
echo                              'ORCA.utils.Platform.generic_GetLocale', >> %spec%
echo                              'ORCA.utils.Platform.generic_GetSystemUserPath', >> %spec%
echo                              'ORCA.utils.Platform.generic_GetUserDataPath', >> %spec%
echo                              'ORCA.utils.Platform.generic_GetUserDownloadsDataPath', >> %spec%
echo                              'ORCA.utils.Platform.generic_Ping', >> %spec%
echo                              'ORCA.utils.Platform.generic_RegisterSoundProvider', >> %spec%
echo                              'ORCA.utils.Platform.generic_SystemIsOnline', >> %spec%
echo                              'ORCA.utils.Platform.generic_ToPath', >> %spec%
echo                              'ORCA.utils.Platform.generic_Vibrate', >> %spec%
echo                              'ORCA.utils.Platform.win_GetUserDataPath', >> %spec%
echo                              'ORCA.utils.Platform.win_GetUserDownloadsDataPath', >> %spec%
echo                              'ORCA.utils.Platform.win_Ping', >> %spec%
echo                              'ORCA.utils.Platform.win_ToPath', >> %spec%
echo                              'ORCA.utils.Platform.win_Vibrate', >> %spec%
echo                              ], >> %spec%
echo               hookspath=[],runtime_hooks=[],excludes=[],win_no_prefer_redirects=False,win_private_assemblies=False,cipher=block_cipher,noarchive=False) >> %spec%
echo pyz = PYZ(a.pure, a.zipped_data,cipher=block_cipher) >> %spec%
echo exe = EXE(pyz,a.scripts,[],exclude_binaries=True,name=os.path.join('build\\pyi.win32\\ORCA', 'ORCA.exe'),debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=True ) >> %spec%
echo coll = COLLECT(exe,Tree('%pyinstallerdir%\work'),a.binaries,a.zipfiles,a.datas,*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + gstreamer.dep_bins)],strip=False,upx=True,name=os.path.join('dist', 'ORCA'))  >> %spec%

rem echo coll = COLLECT(exe, Tree('%pysrcdir%'),a.binaries,a.zipfiles,a.datas,strip=None,upx=True,name=os.path.join('dist', 'ORCA')) >> %spec%
rem echo coll = COLLECT(exe, Tree('%pysrcdir%'),Tree([f for f in os.environ.get('KIVY_SDL2_PATH', '').split(';') if 'bin' in f][0]),Tree(gst_plugin_path),Tree(os.path.join(gst_plugin_path, 'bin')),a.binaries,a.zipfiles,a.datas,strip=None,upx=True,name=os.path.join('dist', 'ORCA')) >> %spec%
rem copy %spec% %pyinstallerdir%\ORCA
goto:eof
rem **************************************************************************************************************************************

:RunPyInstaller
pushd "%pyinstallerdir%"
rem python -m PyInstaller --name ORCA "%pysrc2%\main.py" --noconfirm 
python -m PyInstaller "%spec%" --noconfirm
popd
goto:eof
rem **************************************************************************************************************************************

:CreateWindowsZipFile
set zipdest=%abspath%\..\Deployment\orca-%branch%-%version%-windows.zip
set zippar=a -tzip -mx9 
echo Creating Windows Zip File: "%zipprg%" %zippar% "%zipdest%" "%zipsrcdir%"
del %zipdest%
"%zipprg%" %zippar% "%zipdest%" "%zipsrcdir%"
goto:eof

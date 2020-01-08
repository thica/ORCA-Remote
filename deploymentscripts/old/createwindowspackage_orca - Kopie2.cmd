@echo off
SETLOCAL EnableDelayedExpansion

set KIVYVERSION=Kivy27

call:FindSourcesPath
call:FindPyInstaller
call:FindKivy
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

for %%p in (c d e f g h i j k l m n o p q r s t u v w x y z) do if exist %%p:\dev\pyinstaller-2.1\nul (
set pyinstallerdir=%%p:\dev\pyinstaller-2.1
GOTO FOUNDPYINSTALLER
)

pause Can't find pyinstaller
exit
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

pause Can't find kivy (%KIVYVERSION%)
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
echo  ...(%APPDATA%\pyinstaller\*.*)
del "%APPDATA%\pyinstaller\*.*" /S /Q > nul >>nul
echo ...(%APPDATA%\pyinstaller)
rmdir "%APPDATA%\pyinstaller" /S /Q >nul >>nul
mkdir %pyinstallerdir%\ORCA
goto:eof
rem **************************************************************************************************************************************

:MakeCopyOfSources

Echo Creating working copy of ORCA SRC files 
set srcdir=%abspath%\..\work
echo  ... Cleaning old working folder (%srcdir%)
del %srcdir%\*.* /S /Q > nul
rmdir %srcdir% /S /Q > nul
mkdir %srcdir% > nul
echo  ... Copy files and creating folder structure (%srcgitdir% to %srcdir%)
xcopy %srcgitdir%\*.py %srcdir% /q >nul
xcopy %srcgitdir%\*.txt %srcdir% /q >nul
mkdir %srcdir%\languages
xcopy %srcgitdir%\languages %srcdir%\languages /S /q >nul
mkdir %srcdir%\actions
copy %srcgitdir%\actions\actionsfallback.xml %srcdir%\actions > nul
mkdir %srcdir%\ORCA
xcopy %srcgitdir%\ORCA %srcdir%\ORCA /S /q >nul
copy %abspath%\..\orcafullscreen.cmd %srcdir% >nul
goto:eof
rem **************************************************************************************************************************************

:CreatePyInstallerSpecFile

set spec=ORCA.spec
set pysrc=%srcdir%\main.py
set pysrc=%pysrc:\=\\%
set pysrcdir=%srcdir%/
set pysrcdir=%pysrcdir:\=/%
set pysrc2=%srcdir%
set pyinstallerdirpy=%pyinstallerdir%
set pyinstallerdirpy=%pyinstallerdirpy:\=\\%

			   
rem We create the spec file manual.
echo # -*- mode: python -*- > %spec%
echo import os >> %spec%
echo from kivy.tools.packaging.pyinstaller_hooks import install_hooks >> %spec%
echo import kivy.core.video >> %spec%
echo install_hooks(globals()) >> %spec%
echo gst_plugin_path = os.environ.get('GST_PLUGIN_PATH').split('lib')[0] >> %spec%
echo a = Analysis(['%pysrc%'],pathex=['%pyinstallerdirpy%'],hiddenimports=[]) >> %spec%
echo pyz = PYZ(a.pure) >> %spec%
echo exe = EXE(pyz,a.scripts,exclude_binaries=1,name=os.path.join('build\\pyi.win32\\ORCA', 'ORCA.exe'),debug=False,strip=None,upx=True,console=False ) >> %spec%

rem echo coll = COLLECT(exe, Tree('%pysrcdir%'),a.binaries,a.zipfiles,a.datas,strip=None,upx=True,name=os.path.join('dist', 'ORCA')) >> %spec%
echo coll = COLLECT(exe, Tree('%pysrcdir%'),Tree([f for f in os.environ.get('KIVY_SDL2_PATH', '').split(';') if 'bin' in f][0]),Tree(gst_plugin_path),Tree(os.path.join(gst_plugin_path, 'bin')),a.binaries,a.zipfiles,a.datas,strip=None,upx=True,name=os.path.join('dist', 'ORCA')) >> %spec%
copy %spec% %pyinstallerdir%\ORCA
del %spec%
goto:eof
rem **************************************************************************************************************************************

:RunPyInstaller
pushd "%pyinstallerdir%"
call "%kivybat%" "%kivypath%\Python27\Scripts\pyinstaller-script.py" --name ORCA "%pysrc2%\main.py" --noconfirm 
call "%kivybat%" "%kivypath%\Python27\Scripts\pyinstaller-script.py" "%pyinstallerdir%\ORCA\%spec%" --noconfirm
popd
goto:eof
rem **************************************************************************************************************************************

:CreateWindowsZipFile
set zipdest=%abspath%\..\Deployment\orca-%branch%-%version%-windows.zip
set zippar=a -r -tzip -mx9 
echo Creating Windows Zip File: "%zipprg%" %zippar% "%zipdest%" "%zipsrcdir%"
del %zipdest%
"%zipprg%" %zippar% "%zipdest%" "%zipsrcdir%"
goto:eof

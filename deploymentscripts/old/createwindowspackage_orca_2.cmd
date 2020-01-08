echo on

for %%A in ("%~dp0.\..") do set abspath=%%~fA
set pyinstallerdir=C:\dev\pyinstaller-2.1
set kivybat=C:\dev\Kivy\kivy.bat
set zipprg=C:\Program Files\7-Zip\7z.exe
set zippar=a -r -tzip -mx9 -x!*.pyc
rem set zipsrcdir=%pyinstallerdir%\ORCA\dist\ORCA
set zipsrcdir=%pyinstallerdir%\dist\ORCA
del %zipsrcdir%\*.* /S /Q

pause

for /f "delims== tokens=2" %%v in ('findstr self.sVersion= %abspath%\src\orca.py') do (
    set version=%%v
    goto endfind
)

:endfind
set version=%version:"=%


for /f "delims== tokens=2" %%v in ('findstr self.sBranch= %abspath%\src\orca.py') do (
    set branch=%%v
    goto endfind2
)

:endfind2
set branch=%branch:"=%

set srcgitdir=%abspath%\src
set srcdir=%abspath%\..\work
set spec=ORCA.spec

set zipdest=%abspath%\..\Deployment\orca-%branch%-%version%-windows.zip
del %zipdest%

echo %zipdest%
echo %zipsrcdir%
pause

set pysrc=%srcdir%\main.py
set pysrc=%pysrc:\=\\%
set pysrcdir=%srcdir%/
set pysrcdir=%pysrcdir:\=/%

set pysrc2=%srcdir%

set pyinstallerdirpy=%pyinstallerdir%
set pyinstallerdirpy=%pyinstallerdirpy:\=\\%


rem We create the spec file manual.
echo # -*- mode: python -*- > %spec%
echo from kivy.tools.packaging.pyinstaller_hooks import install_hooks  >> %spec%
echo install_hooks(globals()) >> %spec%
echo a = Analysis(['%pysrc%'],pathex=['%pyinstallerdirpy%'],hiddenimports=[]) >> %spec%
echo pyz = PYZ(a.pure) >> %spec%
echo exe = EXE(pyz,a.scripts,exclude_binaries=1,name=os.path.join('build\\pyi.win32\\ORCA', 'ORCA.exe'),debug=False,strip=None,upx=True,console=False ) >> %spec%
echo coll = COLLECT(exe, Tree('%pysrcdir%'),a.binaries,a.zipfiles,a.datas,strip=None,upx=True,name=os.path.join('dist', 'ORCA')) >> %spec%


del %srcdir%\*.* /S /Q
xcopy %srcgitdir%\*.py %srcdir%
xcopy %srcgitdir%\*.txt %srcdir%
mkdir %srcdir%\languages
xcopy %srcgitdir%\languages %srcdir%\languages /S

copy %abspath%\..\orcafullscreen.cmd %srcdir%

rmdir "%pyinstallerdir%\ORCA" /S /Q
del "%APPDATA%\pyinstaller\*.*" /S /Q
rmdir "%APPDATA%\pyinstaller" /S /Q


pushd "%pyinstallerdir%"
mkdir ORCA
call "%kivybat%" "%pyinstallerdir%\pyinstaller.py" --name ORCA "%pysrc2%\main.py" --noconfirm

popd
copy %spec% %pyinstallerdir%\ORCA
del %spec%


pushd "%pyinstallerdir%"
call "%kivybat%" "%pyinstallerdir%\pyinstaller.py" "%pyinstallerdir%\ORCA\%spec%" --noconfirm
popd


echo "%zipprg%" %zippar% "%zipdest%" "%zipsrcdir%"
pause
"%zipprg%" %zippar% "%zipdest%" "%zipsrcdir%"

pause


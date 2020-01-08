for %%A in ("%~dp0.\..") do set abspath=%%~fA
set srcgitdir=%abspath%\src
set zipprg=C:\Program Files\7-Zip\7z.exe
set zippar=a -tzip -mx0
set zippar2=a -r -tzip -mx9 -x!*.pyc
set zippardel=d 

for /f "delims== tokens=2" %%v in ('findstr self.sVersion= %abspath%\src\orca.py') do (
    set version=%%v
    goto endfind
)

:endfind

set version=%version:"=%
echo Version:%version%


for /f "delims== tokens=2" %%v in ('findstr self.sBranch= %abspath%\src\orca.py') do (
    set branch=%%v
    goto endfind2
)

:endfind2

set branch=%branch:"=%
echo Branch:%branch%


set srcdir=%abspath%\..\Deployment\work
set zipdest=%abspath%\..\Deployment\orca-%branch%-%version%-kivylauncher.zip

del %zipdest%
del %ziptmp%
rmdir %srcdir% /S /Q
mkdir %srcdir%
xcopy %srcgitdir%\*.* %srcdir% /S


rmdir %srcdir% /S /Q
mkdir %srcdir%
mkdir %srcdir%\ORCA

xcopy %srcgitdir%\*.py %srcdir%\ORCA
xcopy %srcgitdir%\*.txt %srcdir%\ORCA
mkdir %srcdir%\ORCA\languages
xcopy %srcgitdir%\languages %srcdir%\ORCA\languages /S


"%zipprg%" %zippar% "%zipdest%" "%srcdir%\ORCA"

echo "Create Zipfile"
set zipdest=c:\media\upload\ORCARemoteControl-%branch%-%version%-windows.zip
set zippar=-CompressionLevel Fastest
echo Clean up finals
rmdir "%BUILDDIR%\dist\ORCA\interfacestmp" /S /Q > nul
rmdir "%BUILDDIR%\dist\ORCA\scriptstmp" /S /Q > nul
rmdir "%BUILDDIR%\dist\ORCA\Platform" /S /Q > nul

rem echo Creating Windows Zip File:powershell Compress-Archive -Path %BUILDDIR%\dist\ORCA %zippar% -DestinationPath %zipdest%
del %zipdest% 1>nul 2>nul

rem powershell Compress-Archive -Path %BUILDDIR%\dist\ORCA\*.* %zippar% -DestinationPath %zipdest%
echo "%SNAPSHOTDIR%\7-zip\7z" a -r -mx9 %zipdest% %BUILDDIR%\dist\ORCA
"%SNAPSHOTDIR%\7-zip\7z" a -r -mx9 %zipdest% %BUILDDIR%\dist\ORCA
echo "Create Zipfile"
set zipdest=z:\Orca\Development\ORCA\Deployment\orca-%branch%-%version%-windows.zip
set zippar=-CompressionLevel Fastest
echo Clean up finals
rmdir "%BUILDDIR%\dist\ORCA\interfacestmp" /S /Q > nul
rmdir "%BUILDDIR%\dist\ORCA\scriptstmp" /S /Q > nul
rmdir "%BUILDDIR%\dist\ORCA\Platform" /S /Q > nul

echo Creating Windows Zip File:powershell Compress-Archive -Path %BUILDDIR%\dist\ORCA %zippar% -DestinationPath %zipdest%
del %zipdest% 1>nul 2>nul

powershell Compress-Archive -Path %BUILDDIR%\dist\ORCA\*.* %zippar% -DestinationPath %zipdest%
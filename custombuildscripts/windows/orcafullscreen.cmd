@echo off
Set "WMIC_Command=wmic path Win32_VideoController get VideoModeDescription^,CurrentHorizontalResolution^,CurrentVerticalResolution /format:Value"
Set "H=CurrentHorizontalResolution"
Set "V=CurrentVerticalResolution"
Call :GetResolution %H% HorizontalResolution
Call :GetResolution %V% VerticalResolution
goto Start

::****************************************************
:GetResolution
FOR /F "tokens=2 delims==" %%I IN (
  '%WMIC_Command% ^| find /I "%~1" 2^>^nul'
) DO FOR /F "delims=" %%A IN ("%%I") DO SET "%2=%%A"
Exit /b
::****************************************************

:Start
orca.exe --fullscreen --size=%HorizontalResolution%x%VerticalResolution%
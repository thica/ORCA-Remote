:: Exit any previous venv
call C:\Development\Python_venv\ORCA\Scripts\deactivate.bat
cd C:\Development
:: Install Python3 if required
IF NOT EXIST C:\Development\Python3\python.exe (
python-3.7.4-amd64.exe  /quiet TargetDir="C:\Development\Python3" Include_launcher=0 Include_symbols=1 SimpleInstall=1
)
cd C:\Development\Python3
:: Install virtual environment and some tools to install kivy
python -m pip install --upgrade pip wheel setuptools virtualenv
:: Create the virtual environment root folder
mkdir C:\Development\Python_venv
:: Create the virtual environment
python -m virtualenv C:\Development\Python_venv\ORCA
:: Activate the virtula environemnt
call C:\Development\Python_venv\ORCA\Scripts\activate.bat
:: Change the interpreter to the virtual environment
cd C:\Development\Python_venv\ORCA
:: Install all requiered packeages for ORCA
python -m pip install docutils pygments pypiwin32 kivy_deps.sdl2==0.1.22 kivy_deps.glew==0.1.12
python -m pip install kivy_deps.angle==0.1.9
python -m pip install kivy_deps.gstreamer==0.1.17
python -m pip install kivy==1.11.0
python -m pip install kivy_examples==1.11.0
python -m pip install future
python -m pip install plyer
python -m pip install rsa
python -m pip install pyasn1
python -m pip install wakeonlan
python -m pip install ws4py
python -m pip install httplib2
python -m pip install pycparser
python -m pip install mwclient
python -m pip install demjson

rem This fails on windows
rem python -m pip install openssl
rem This fails on windows
rem python -m pip install png
rem This fails on windows
rem This fails on windows
rem python -m pip install jpeg
rem This fails on windows
rem python -m pip install sdl2
rem This fails on windows
rem python -m pip install android
rem This fails on windows
rem python -m pip install pyjnius




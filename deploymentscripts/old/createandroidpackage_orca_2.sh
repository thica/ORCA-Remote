#!/bin/bash

#set +v
#set -v
#clear

# This script needs to be called from an Linux environment, within the /home/kivy folder
cd /home/kivy


fil="/mnt/ORCA/Development/ORCA/Master/src/ORCA/APP.py"

if [ -f $fil ]
then

  #read through the file looking for the word self.fVersion=

  while read line
  do
    echo $line | grep -q self.sVersion= >nul
    if [ $? == 0 ]; then
    varORCAVERSION=`echo $line  | cut -d = -f2 | cut -d : -f1`
    break
    fi
  done < $fil

fi


varORCAVERSION=`echo $varORCAVERSION | tr -d "\n"`
varORCAVERSION=`echo $varORCAVERSION | tr -d "\r"`
varORCAVERSION="${varORCAVERSION%\"}"
varORCAVERSION="${varORCAVERSION#\"}"

echo "Version Found: [$varORCAVERSION]"



if [ -f $fil ]
then

  #read through the file looking for the word self.sBranch=

  while read line
  do
    echo $line | grep -q self.sBranch= >nul
    if [ $? == 0 ]; then
    varORCABRANCH=`echo $line  | cut -d = -f2 | cut -d : -f1`
    break
    fi
  done < $fil

fi


varORCABRANCH=`echo $varORCABRANCH | tr -d "\n"`
varORCABRANCH=`echo $varORCABRANCH | tr -d "\r"`
varORCABRANCH="${varORCABRANCH%\"}"
varORCABRANCH="${varORCABRANCH#\"}"

echo "Branch Found: [$varORCABRANCH]"

#set -x verbose #echo on


# Title
varAPPNAME1="ORCA Open Remote Control Application"
# Automatic Created Filename, blanks excluded
varAPPNAME2="ORCAOpenRemoteControlApplication"
#varname for final package
varAPPNAME4="ORCARemoteControl"
#filename prefix for final zip
varAPPNAME3=orca
# Source Folder
varSOURCE="/mnt/ORCA/Development/ORCA/Master/src"
# Target Path on Android (must contain 2 dots ?)
varDOMAIN="org.orca.orcaremote"
#workdir for copy of ORCA python files
varWORKDIR="/home/kivy/work"
varDESTDIR="/mnt/ORCA/Development/Orca"


#Cleaning workdirs
mkdir -p "${varWORKDIR}" >nul 2>nul

echo "1" > "${varWORKDIR}"/stub.txt
rm -r "${varWORKDIR}"/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi

mkdir -p "${varWORKDIR}/src" >nul 2>nul


#copy python files
# read -p "Press [Enter] key to continue..."
cp -f "${varSOURCE}"/*.py "${varWORKDIR}"/src

cp -f "${varSOURCE}"/*.txt "${varWORKDIR}"/src
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi


cp -f -R "${varSOURCE}"/languages "${varWORKDIR}"/src
if [ "$?" -ne "0" ]; then
  echo "Copy sources languages failed"
  exit 1
fi

cp -f -R "${varSOURCE}"/ORCA "${varWORKDIR}"/src
if [ "$?" -ne "0" ]; then
  echo "Copy sources subs failed"
  exit 1
fi

mkdir "${varWORKDIR}"/src/actions
cp -f "${varSOURCE}"/actions/actionsfallback.xml "${varWORKDIR}"/src/actions
if [ "$?" -ne "0" ]; then
  echo "Copy actions subs failed"
  exit 1
fi


cd /home/kivy/python-for-android/dist/default


mkdir -p res/drawable-hdpi
mkdir -p res/drawable-xhdpi
mkdir -p res/drawable-xxhdpi
#mkdir res/drawable-xxxhdpi

cp /mnt/ORCA/Graphics/Android_Logo/Kivy_logo_replacements/kivy_icon_72.png res/drawable-hdpi/icon.png
cp /mnt/ORCA/Graphics/Android_Logo/Kivy_logo_replacements/kivy_icon_96.png res/drawable-xhdpi/icon.png
cp /mnt/ORCA/Graphics/Android_Logo/Kivy_logo_replacements/kivy_icon_144.png res/drawable-xxhdpi/icon.png
#cp /mnt/ORCA/Graphics/Android_Logo/Kivy_logo_replacements/kivy_icon_192.png res/drawable-xxxhdpi/icon.png

./build.py --dir ${varWORKDIR}/src --package ${varDOMAIN} --name "${varAPPNAME1}" --presplash /mnt/ORCA/Graphics/Android_Logo/orca-presplash.jpg  --icon /mnt/ORCA/Graphics/Android_Logo/ic_launcher_orca_lpi.png   --version ${varORCAVERSION} --permission INTERNET --permission VIBRATE --permission BLUETOOTH --permission WRITE_EXTERNAL_STORAGE --permission ACCESS_WIFI_STATE --permission ACCESS_NETWORK_STATE --orientation=sensor --install-location preferExternal release

rm ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk
cp /home/kivy/python-for-android/dist/default/bin/${varAPPNAME2}-${varORCAVERSION}-release-unsigned.apk ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk
jarsigner   -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore /home/kivy/orca-release-key.keystore  ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk -storepass myorcapwstore -keypass myorcapw  ORCAREL

rm /home/kivy/tmp.apk

#rm ${varDESTDIR}/${varAPPNAME2}/${varORCABRANCH}/android/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
#zipalign -v 4 ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk ${varDESTDIR}/${varAPPNAME2}/${varORCABRANCH}/android/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
/home/kivy/android-sdk-linux/build-tools/19.1.0/zipalign -v 4 ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk /home/kivy/tmp.apk


cp /home/kivy/tmp.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk


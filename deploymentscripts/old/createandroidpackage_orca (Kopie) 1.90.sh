#!/bin/bash

#set +v
#set -v
#clear

# This script needs to be called from an Linux environment, within the /home/kivy folder
cd /home/kivy


fil="/mnt/ORCA/Development/ORCA/Master/src/ORCA.py"

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
varDESTWORK="/mnt/ORCA/Development/Orca/work"


#Cleaning workdirs
mkdir "${varWORKDIR}" >nul

echo "1" > "${varWORKDIR}"/stub.txt
rm -R "${varWORKDIR}"/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi


mkdir "${varDESTWORK}" >nul
echo "1" > "${varDESTWORK}"/stub.txt
rm -R "${varDESTWORK}"/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi


#copy python files
# read -p "Press [Enter] key to continue..."
cp -f "${varSOURCE}"/*.py "${varWORKDIR}"

cp -f "${varSOURCE}"/*.txt "${varWORKDIR}"
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi


cp -f -R "${varSOURCE}"/languages "${varWORKDIR}"
if [ "$?" -ne "0" ]; then
  echo "Copy sources languages failed"
  exit 1
fi


cd /home/kivy/python-for-android/dist/default


mkdir res/drawable-hdpi
mkdir res/drawable-xhdpi
mkdir res/drawable-xxhdpi
#mkdir res/drawable-xxxhdpi

cp /mnt/ORCA/Graphics/Android_Logo/Kivy_logo_replacements/kivy_icon_72.png res/drawable-hdpi/icon.png
cp /mnt/ORCA/Graphics/Android_Logo/Kivy_logo_replacements/kivy_icon_96.png res/drawable-xhdpi/icon.png
cp /mnt/ORCA/Graphics/Android_Logo/Kivy_logo_replacements/kivy_icon_144.png res/drawable-xxhdpi/icon.png
#cp /mnt/ORCA/Graphics/Android_Logo/Kivy_logo_replacements/kivy_icon_192.png res/drawable-xxxhdpi/icon.png


./build.py --dir ${varWORKDIR} --package ${varDOMAIN} --name "${varAPPNAME1}" --presplash /mnt/ORCA/Graphics/Android_Logo/orca-presplash.jpg  --icon /mnt/ORCA/Graphics/Android_Logo/ic_launcher_orca_lpi.png   --window --version ${varORCAVERSION} --permission INTERNET --permission VIBRATE --permission BLUETOOTH --permission WRITE_EXTERNAL_STORAGE --permission ACCESS_WIFI_STATE --permission ACCESS_NETWORK_STATE --orientation=sensor --install-location preferExternal release


rm ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk
cp ./bin/${varAPPNAME2}-${varORCAVERSION}-release-unsigned.apk ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk


jarsigner   -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore /home/kivy/orca-release-key.keystore  ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk -storepass myorcapwstore -keypass myorcapw  ORCAREL


rm /home/kivy/tmp.apk


#rm ${varDESTDIR}/${varAPPNAME2}/${varORCABRANCH}/android/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
#zipalign -v 4 ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk ${varDESTDIR}/${varAPPNAME2}/${varORCABRANCH}/android/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
#/home/kivy/Android/android-sdk-linux/tools/zipalign -v 4 ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk /home/kivy/tmp.apk
/home/kivy/Android/android-sdk-linux/build-tools/21.1.2/zipalign -v 4 ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk /home/kivy/tmp.apk


# cp /home/kivy/tmp.apk ${varDESTWORK}/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
cp /home/kivy/tmp.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk


#!/bin/bash


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
varWORKDIRBD="/home/kivy/workbd"
varDESTDIR="/mnt/ORCA/Development/Orca"
varDESTWORK="/mnt/ORCA/Development/Orca/work"


#Cleaning workdirs
mkdir -p "${varWORKDIR}"/src >nul
mkdir -p "${varWORKDIR}"/bin >nul
mkdir -p "${varWORKDIRBD}" >nul
mkdir -p "${varWORKDIRBD}"/bin >nul

echo "1" > "${varWORKDIR}"/src/stub.txt
rm -R "${varWORKDIR}"/src/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi


mkdir "${varDESTWORK}/src" >nul
echo "1" > "${varDESTWORK}"/src/stub.txt
rm -R "${varDESTWORK}"/src/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi

rm /home/kivy/workbd/.buildozer/android/platform/python-for-android/dist/orca/bin/*.apk

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


cp -f -R "${varSOURCE}"/../deploymentscripts/buildozer/*.spec "${varWORKDIRBD}"

cd "${varWORKDIRBD}"
#buildozer -v android debug  > buildozer.log 2>&1
buildozer -v android debug
buildozer -v android release

#rm ${varWORKDIR}/bin/*.*
#rm ${varWORKDIRBD}/bin/*.*


cp /home/kivy/workbd/.buildozer/android/platform/python-for-android/dist/orca/bin/ORCA-OpenRemoteControlApplication-${varORCAVERSION}-release-unsigned.apk ${varWORKDIR}/bin/orca-unsigned.apk
#cp /home/kivy/workbd/.buildozer/android/platform/python-for-android/dist/orca/bin/ORCA-OpenRemoteControlApplication-1.1.0-debug.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}_debug.apk


#jarsigner   -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore /home/kivy/orca-release-key.keystore  ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk -storepass myorcapwstore -keypass myorcapw  ORCAREL
jarsigner   -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore /home/kivy/orca-release-key.keystore  ${varWORKDIR}/bin/orca-unsigned.apk -storepass myorcapwstore -keypass myorcapw  ORCAREL


rm /home/kivy/tmp.apk


#/home/kivy/Android/android-sdk-linux/build-tools/21.1.2/zipalign -v 4 ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk /home/kivy/tmp.apk
#${varWORKDIR}/../.buildozer/android/platform/android-sdk-21/build-tools/19.1.0/zipalign -v 4 ${varWORKDIR}/bin/orca-unsigned.apk /home/kivy/tmp.apk
${varWORKDIR}/../.buildozer/android/platform/android-sdk-21/build-tools/19.1.0/zipalign -v 4 ${varWORKDIR}/bin/orca-unsigned.apk /home/kivy/tmp.apk

# cp /home/kivy/tmp.apk ${varDESTWORK}/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
cp /home/kivy/tmp.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk


#remove
#./build.py --dir /home/kivy/work/src --package org.orca.orcaremote --name "ORCA Open Remote Control Application" --presplash /mnt/ORCA/Graphics/Android_Logo/orca-presplash.jpg  --icon /mnt/ORCA/Graphics/Android_Logo/ic_launcher_orca_lpi.png   --version 1.1.0 --permission INTERNET --permission VIBRATE --permission BLUETOOTH --permission WRITE_EXTERNAL_STORAGE --permission ACCESS_WIFI_STATE --permission ACCESS_NETWORK_STATE --orientation=sensor --install-location preferExternal release
#!/bin/bash


# This script needs to be called from an LinuxOSX environment, within the /home/kivy (UBUNTU) folder

export P4A_RELEASE_KEYSTORE=~/keystores/orca-release-key.keystore
export P4A_RELEASE_KEYSTORE_PASSWD=android
export P4A_RELEASE_KEYALIAS_PASSWD=android
export P4A_RELEASE_KEYALIAS=orca-release-key

# Source Folder
varSOURCEROOT="/mnt/ORCA"
varUSERDIR="/home/kivy"

#OSX
if [[ "$OSTYPE" == "darwin"* ]]; then
    varUSERDIR="/Users/kivy"
	varSOURCEROOT="/Volumes/c$/CTPrivat/Orca"
fi

varSOURCE="${varSOURCEROOT}"/Development/ORCA/Master/src
#workdir for copy of ORCA python files
varWORKDIR="${varUSERDIR}"/work
varWORKDIRBD="${varUSERDIR}"/workbd
varDESTDIR="${varSOURCEROOT}"/Development/Orca
varDESTWORK="${varSOURCEROOT}"/Development/Orca/work


cd "${varUSERDIR}"
fil="${varSOURCE}"/ORCA/APP.py

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

# Target Path on Android (must contain 2 dots ?)
varDOMAIN="org.orca.orcaremote"
# Title
varAPPNAME1="ORCA Open Remote Control Application"
# Automatic Created Filename, blanks excluded
varAPPNAME2="ORCAOpenRemoteControlApplication"
#varname for final package
varAPPNAME4="ORCARemoteControl"
#filename prefix for final zip
varAPPNAME3=orca


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

if [[ "$OSTYPE" == "linux-gnu" ]]; then
	rm "${varWORKDIRBD}"/bin/*.apk
fi

#copy python files
# read -p "Press [Enter] key to continue..."
cp -L -f "${varSOURCE}"/*.py "${varWORKDIR}"/src

cp -L -f "${varSOURCE}"/*.txt "${varWORKDIR}"/src
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi


cp -L -f -R "${varSOURCE}"/languages "${varWORKDIR}"/src
if [ "$?" -ne "0" ]; then
  echo "Copy sources languages failed"
  exit 1
fi

cp -L -f -R "${varSOURCE}"/ORCA "${varWORKDIR}"/src
if [ "$?" -ne "0" ]; then
  echo "Copy sources subs failed"
  exit 1
fi

mkdir "${varWORKDIR}"/src/actions
cp -L -f "${varSOURCE}"/actions/actionsfallback.xml "${varWORKDIR}"/src/actions
cp -L -f "${varSOURCE}"/actions/actionsearly.xml "${varWORKDIR}"/src/actions
if [ "$?" -ne "0" ]; then
  echo "Copy actions subs failed"
  exit 1
fi

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    cp -f -R "${varSOURCE}"/../deploymentscripts/buildozer/*.spec "${varWORKDIRBD}"
	cd "${varWORKDIRBD}"
	#buildozer -v android debug
	buildozer -v android release

	# Manual sign
	# cp "${varWORKDIRBD}"/.buildozer/android/platform/build/dists/orca/bin/ORCA-OpenRemoteControlApplication-${varORCAVERSION}-release-unsigned.apk ${varWORKDIR}/bin/orca-unsigned.apk
	# jarsigner   -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore ~/keystores/orca-release-key.keystore  ${varWORKDIR}/bin/orca-unsigned.apk -storepass myorcapw -keypass myorcapw  ORCAREL
	# rm "${varUSERDIR}"/tmp.apk
	# ~/.buildozer/android/platform/android-sdk-20/build-tools/19.1.0/zipalign -v 4 ${varWORKDIR}/bin/orca-unsigned.apk /home/kivy/tmp.apk
	# cp "${varUSERDIR}"/tmp.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk

	# automatic sign
	cp "${varWORKDIRBD}"/bin/orca-${varORCAVERSION}-release.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk
	
fi

read -p "Press any Key to continue"

#OSX
if [[ "$OSTYPE" == "darwin"* ]]; then
	cd "${varUSERDIR}"/packaging/kivy-sdk-packager/osx
	rm -rf "${varUSERDIR}"/packaging/kivy-sdk-packager/osx/src.dmg
	rm -rf "${varUSERDIR}"/packaging/kivy-sdk-packager/osx/src
	rm -rf "${varUSERDIR}"/packaging/kivy-sdk-packager/osx/Orca.dmg
	rm -rf "${varUSERDIR}"/packaging/kivy-sdk-packager/osx/Orca
	rm -rf "${varUSERDIR}"/packaging/kivy-sdk-packager/osx/Orca.app
    ./package-app.sh "${varWORKDIR}"/src
	#todo_ check some tidy up and copy actions
	mv src.app Orca.app
	./create-osx-dmg.sh Orca.app
	cp "${varUSERDIR}"/packaging/kivy-sdk-packager/osx/Orca.dmg ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.dmg
fi

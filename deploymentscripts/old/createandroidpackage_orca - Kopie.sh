#!/bin/bash

set -x


# This script needs to be called from an LinuxOSX environment, within the /home/kivy (UBUNTU) folder

export P4A_RELEASE_KEYSTORE=orca-release-key.keystore
export P4A_RELEASE_KEYSTORE_PASSWD=myorcapw
export P4A_RELEASE_KEYALIAS_PASSWD=myorcapw
export P4A_RELEASE_KEYALIAS=ORCAKEY
#keytool -genkey -v -keystore ./keystores/orca-release-key.keystore -alias ORCAKEY -keyalg RSA -keysize 2048 -validity 10000


varTARGET="ANDROID"
echo "$OSTYPE"

if [[ $OSTYPE == darwin ]]; then
    varTARGET="OSX"
fi

if [[ $1 == ubuntu* ]]; then
    varTARGET="UBUNTU"
fi

if [[ $OSTYPE == linux-gnu ]]; then
    echo Compiling for Android
fi


# Source Folder
varSOURCEROOT="/mnt/ORCA"
varUSERDIR="/home/kivy"
# varUSERDIR="~"

#OSX
if [[ $varTARGET == OSX ]]; then
    varSOURCEROOT="/Users/carsten/Orca"
    varUSERDIR="/Users/carsten"
fi


if [[ $varTARGET == UBUNTU ]]; then
    varUSERDIR="/home/kivy/ubuntubuid"
    mkdir -p "${varUSERDIR}" >nul
fi


varSOURCE="${varSOURCEROOT}"/Development/ORCA/Master/src

#workdir for copy of ORCA python files
varWORKDIR="${varUSERDIR}"/work
varWORKDIRBD="${varUSERDIR}"/workbd
varDESTDIR="${varSOURCEROOT}"/Development/Orca
varDESTWORK="${varUSERDIR}"/work2


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

mkdir -p "${varDESTWORK}" >nul
mkdir -p "${varDESTWORK}/src" >nul
echo "1" > "${varDESTWORK}"/src/stub.txt
rm -R "${varDESTWORK}"/src/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi

if [[ $varTARGET == ANDROID ]]; then
	rm "${varWORKDIRBD}"/.buildozer/android/platform/python-for-android/dist/orca/bin/*.apk
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
# cp -L -f "${varSOURCE}"/actions/actionsearly.xml "${varWORKDIR}"/src/actions
if [ "$?" -ne "0" ]; then
  echo "Copy actions subs failed"
  exit 1
fi

if [[ $varTARGET == ANDROID ]]; then
    cp -f -R "${varSOURCE}"/../deploymentscripts/buildozer/*.spec "${varWORKDIRBD}"
	cd "${varWORKDIRBD}"
	#buildozer -v android debug
	buildozer -v android release

	# cp "${varWORKDIRBD}"/.buildozer/android/platform/python-for-android/dist/orca/bin/ORCA-OpenRemoteControlApplication-${varORCAVERSION}-release-unsigned.apk ${varWORKDIR}/bin/orca-unsigned.apk
	# jarsigner   -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore /home/kivy/orca-release-key.keystore  ${varWORKDIR}/bin/orca-unsigned.apk -storepass myorcapwstore -keypass myorcapw  ORCAREL
	# rm "${varUSERDIR}"/tmp.apk
	# ${varWORKDIR}/../.buildozer/android/platform/android-sdk-20/build-tools/19.1.0/zipalign -v 4 ${varWORKDIR}/bin/orca-unsigned.apk /home/kivy/tmp.apk

	# cp "${varUSERDIR}"/tmp.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk
	#cp "${varWORKDIRBD}"/.buildozer/android/platform/build/dists/orca/bin/ORCA-OpenRemoteControlApplication-${varORCAVERSION}-release.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk
	cp "${varWORKDIRBD}"/.buildozer/android/platform/python-for-android-new-toolchain/orca-${varORCAVERSION}-release.apk ${varDESTDIR}/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk
fi

#OSX
if [[ $varTARGET == OSX ]]; then
    cp -f -R "${varSOURCE}"/../deploymentscripts/buildozer/*.spec "${varWORKDIRBD}"
	cd "${varWORKDIRBD}"
    buildozer -v osx debug
fi

#ubuntu
if [[ $varTARGET == UBUNTU ]]; then
# We create the spec file manually.
spec="$(varWORKDIRBD)"/ORCA.spec
echo "Create Spec File: %spec%" 
echo "# -*- mode: python -*-" > %spec%
echo "from kivy.deps import sdl2, glew, gstreamer" >> %spec%
echo "from kivy.tools.packaging.pyinstaller_hooks import install_hooks"  >> %spec%
echo "install_hooks(globals())"  >> %spec%
echo "block_cipher = None" >> %spec%
echo "import kivy.core.video" >> %spec%
echo "a = Analysis(['"${varWORKDIR}"/src'],pathex=[],binaries=[],datas=[]," >> %spec%
echo "              hiddenimports=['ORCA.utils.Platform.generic_cRotation'," >> %spec% 
echo "                             'ORCA.utils.Platform.generic_GetDefaultNetworkCheckMode'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_GetDefaultStretchMode'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_GetInstallationDataPath'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_GetLocale'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_GetSystemUserPath'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_GetUserDataPath'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_GetUserDownloadsDataPath'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_Ping'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_RegisterSoundProvider'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_SystemIsOnline'," >> %spec%
echo "                             'ORCA.utils.Platform.generic_ToPath',"° >> %spec%
echo "                             'ORCA.utils.Platform.generic_Vibrate']," >> %spec%
echo "              hookspath=[],runtime_hooks=[],excludes=[],win_no_prefer_redirects=False,win_private_assemblies=False,cipher=block_cipher,noarchive=False)" >> %spec%
echo "pyz = PYZ(a.pure, a.zipped_data,cipher=block_cipher)" >> %spec%
echo "exe = EXE(pyz,a.scripts,[],exclude_binaries=True,name=os.path.join('build\\pyi.win32\\ORCA', 'ORCA.exe'),debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=True )" >> %spec%
echo "coll = COLLECT(exe,Tree('%pyinstallerdir%\work'),a.binaries,a.zipfiles,a.datas,*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + gstreamer.dep_bins)],strip=False,upx=True,name=os.path.join('dist', 'ORCA'))"  >> %spec%
fi


#OSX
if [[ $varTARGET == OSX_OLD ]]; then
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
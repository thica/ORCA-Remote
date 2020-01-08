#!/bin/bash

set +v
clear

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
varAPPNAME2=ORCARemoteControl
#filename prefix for final zip
varAPPNAME3=orca
# Source Folder
varSOURCE="/mnt/ORCA/Development/ORCA/Master/src"
# Target Path on Android (must contain 2 dots ?)
varDOMAIN="org.orca.orcaremote"
#workdir for copy of ORCA python files
varWORKDIR="/home/kivy/work"
#workdir for copy of ORCA data files
varWORKDIRDATA="/home/kivy/work2"
# Workdir to create final Zip
varWORKDIRZIP="/home/kivy/workzip"

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
mkdir "${varWORKDIRDATA}" >nul
echo "1" > "${varWORKDIRDATA}"/stub.txt
rm -R "${varWORKDIRDATA}"/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi

mkdir "${varWORKDIRZIP}" >nul
echo "1" > "${varWORKDIRZIP}"/stub.txt
rm -R "${varWORKDIRZIP}"/*
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
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi


cp -f "${varSOURCE}"/*.txt "${varWORKDIR}"
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi
#copy data files
cp -f -R "${varSOURCE}"/* "${varWORKDIRDATA}"
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi

rm "${varWORKDIRDATA}"/*.py
rm "${varWORKDIRDATA}"/*.pyc
rm "${varWORKDIRDATA}"/*.log
rm "${varWORKDIRDATA}"/*.ini

#delete all interface settings, with the exception of those, we mark as to be included
IFS=$(echo -en "\n\b")
for file in  $(find "${varWORKDIRDATA}" -name "config.ini") 
   do
      dir="${file%/*}"
      filename="${file##*/}"
      testfile="$dir/include.txt"
   
      if test -f $testfile;
      then
         echo Include: "$file"
      else
         rm $file
      fi
   done


cp -f -R "${varWORKDIRDATA}"/* "${varDESTWORK}"
if [ "$?" -ne "0" ]; then
  echo "Copy sources to tmp failed"
  exit 1
fi


# create the version file
echo ${varORCAVERSION} >  "${varWORKDIRDATA}"/dataversion_${varORCAVERSION}.txt

# Create Data Package

cd "${varWORKDIRDATA}"
zip -r -D -9  ${varWORKDIRZIP}/datapackage_${varORCAVERSION}.zip .
cd /home/kivy/android/python-for-android/dist/default


# copy packagezip into apk package folder
cp  ${varWORKDIRZIP}/datapackage_${varORCAVERSION}.zip ${varWORKDIR}


#find  "${varWORKDIR}"/interfaces -name "interface.txt" -exec rm {} \;
#find  "${varWORKDIR}"/interfaces -name "interface.py" -exec rename -v 's/\.py$/\.txt/i' {} \;

./build.py --dir ${varWORKDIR} --package ${varDOMAIN} --name "${varAPPNAME1}" --icon /mnt/ORCA/Graphics/Android_Logo/ic_launcher_orca_lpi.png  --version ${varORCAVERSION} --permission INTERNET --permission VIBRATE --permission BLUETOOTH --permission WRITE_EXTERNAL_STORAGE  --install-location preferExternal release

rm ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk
cp ./bin/${varAPPNAME2}-${varORCAVERSION}-release-unsigned.apk ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk

jarsigner   -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore /home/kivy/orca-release-key.keystore  ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk -storepass myorcapwstore -keypass myorcapw  ORCAREL


rm /home/kivy/tmp.apk


#rm ${varDESTDIR}/${varAPPNAME2}/${varORCABRANCH}/android/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
#zipalign -v 4 ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk ${varDESTDIR}/${varAPPNAME2}/${varORCABRANCH}/android/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
/home/kivy/android/android-sdk-linux/tools/zipalign -v 4 ./bin/${varAPPNAME2}-${varORCAVERSION}-release-signed.apk /home/kivy/tmp.apk

# cp /home/kivy/tmp.apk ${varDESTWORK}/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
# cp /home/kivy/tmp.apk ${varWORKDIRZIP}/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk
cp /home/kivy/tmp.apk ${varDESTDIR}/Deployment/${varAPPNAME2}-${varORCABRANCH}-${varORCAVERSION}.apk


cd "${varWORKDIRZIP}"
# zip -r -D -9  ${varDESTDIR}/${varORCABRANCH}/android/${varAPPNAME3}-${varORCABRANCH}-${varORCAVERSION}-"android".zip .



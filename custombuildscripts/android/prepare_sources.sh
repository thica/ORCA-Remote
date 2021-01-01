#!/bin/bash

# set -x

cd "${HOME}"
ECHO "Preparing sources ...."

# Source Folder
varSOURCE="${SOURCEDIR}/src"
varWORKDIR="${TARGETDIR}"


ECHO "Removing work-copy of sources in ${varWORKDIR}"
rm -r -f ${varWORKDIR}/* >> "$LOGFILE"

ECHO "Copy from ${varSOURCE} to ${varWORKDIR}"

# mkdir "${varSOURCE}

fil="${varSOURCE}"/ORCA/App.py
if [ -f $fil ]
then
  #read through the file looking for the word self.fVersion=
  while read line
  do
    echo $line | grep -q self.sVersion= >/dev/null
    if [ $? == 0 ]; then
    varORCAVERSION=`echo $line  | cut -d = -f2 | cut -d : -f1`
    break
    fi
  done < $fil
fi


varORCAVERSION=`echo $varORCAVERSION | tr -d "\n"`
varORCAVERSION=`echo $varORCAVERSION | tr -d "\r"`
varORCAVERSION="${varORCAVERSION%\"}"
export varORCAVERSION="${varORCAVERSION#\"}"

ECHO "Version Found: [$varORCAVERSION]"

if [ -f $fil ]
then
  #read through the file looking for the word self.sBranch=
  while read line
  do
    echo $line | grep -q self.sBranch= >/dev/null
    if [ $? == 0 ]; then
    varORCABRANCH=`echo $line  | cut -d = -f2 | cut -d : -f1`
    break
    fi
  done < $fil
fi


varORCABRANCH=`echo $varORCABRANCH | tr -d "\n"`
varORCABRANCH=`echo $varORCABRANCH | tr -d "\r"`
varORCABRANCH="${varORCABRANCH%\"}"
export varORCABRANCH="${varORCABRANCH#\"}"

ECHO "Branch Found: [$varORCABRANCH]"

#set -x verbose #echo on

# Target Path on Android (must contain 2 dots ?)
varDOMAIN="org.orca.orcaremote"
# Title
varAPPNAME1="ORCA Open Remote Control Application"
# Automatic Created Filename, blanks excluded
varAPPNAME2="ORCAOpenRemoteControlApplication"
#varname for final package
export varAPPNAME4="ORCARemoteControl"
#filename prefix for final zip
varAPPNAME3=orca


# if [[ $varTARGET == ANDROID ]]; then
# 	rm "${varWORKDIRBD}"\.buildozer\android\platform\python-for-android\*.apk
# fi

cp -L -f "${varSOURCE}"/*.py "${varWORKDIR}"

cp -L -f "${varSOURCE}"/*.txt "${varWORKDIR}"
if [ "$?" -ne "0" ]; then
  ECHO "Copy sources failed"
  exit 1
fi


cp -L -f -R "${varSOURCE}"/languages "${varWORKDIR}"
if [ "$?" -ne "0" ]; then
  ECHO "Copy sources languages failed"
  exit 1
fi

cp -L -f -R "${varSOURCE}"/ORCA "${varWORKDIR}"
if [ "$?" -ne "0" ]; then
  ECHO "Copy sources subs failed"
  exit 1
fi
find ${varWORKDIR}/. -name "*.ini" -type f -delete

mkdir -p "${varWORKDIR}"/actions
cp -L -f "${varSOURCE}"/actions/actionsfallback.xml "${varWORKDIR}"/actions
# cp -L -f "${varSOURCE}"\actions\actionsearly.xml "${varWORKDIR}"\src\actions
if [ "$?" -ne "0" ]; then
  ECHO "Copy actions subs failed"
  exit 1
fi

printf  "\r%s\n" "[${grn}  OK  ${end}] Prepared sources           "

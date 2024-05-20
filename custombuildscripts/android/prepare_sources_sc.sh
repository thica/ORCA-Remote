#!/bin/bash

# set -x

cd "${HOME}"
ECHO "Preparing sources ...."

# Source Folder
varSOURCE="${SOURCEDIR}"
varWORKDIR="${TARGETDIR}"


ECHO "Removing work-copy of sources in ${varWORKDIR}"
rm -r -f ${varWORKDIR}/* >> "$LOGFILE"

ECHO "Copy from ${varSOURCE} to ${varWORKDIR}"


#set -x verbose #echo on

# Target Path on Android (must contain 2 dots ?)
varDOMAIN="kivy.kivy.showcase"
# Title
varAPPNAME1="Kivy Showcase"
# Automatic Created Filename, blanks excluded
varAPPNAME2="KivyShowcase"
#varname for final package
export varAPPNAME4="kivyshowcase"
#filename prefix for final zip
varAPPNAME3=kivyshowcase


# if [[ $varTARGET == ANDROID ]]; then
# 	rm "${varWORKDIRBD}"\.buildozer\android\platform\python-for-android\*.apk
# fi

cp -L -f "${varSOURCE}"/*.py "${varWORKDIR}"
cp -L -f "${varSOURCE}"/*.txt "${varWORKDIR}"
cp -L -f "${varSOURCE}"/*.kv "${varWORKDIR}"
cp -r "${varSOURCE}"/. "${varWORKDIR}"/


printf  "\r%s\n" "[${grn}  OK  ${end}] Prepared sources           "

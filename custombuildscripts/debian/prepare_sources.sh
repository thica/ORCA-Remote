#!/bin/bash

. "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"  >> "$LOGFILE"

# mkdir "${TARGETDIR}/interfacestmp"
# cp -L -f -R  "${SOURCEDIR}/src/interfaces" "${TARGETDIR}/interfacestmp"
# cp -L -f -R  "${SOURCEDIR}/src/interfaces" "${TARGETDIR}"

# mkdir "${TARGETDIR}/scriptstmp"
# cp -L -f -R  "${SOURCEDIR}/src/scripts" "${TARGETDIR}/scriptstmp"
# cp -L -f -R  "${SOURCEDIR}/src/scripts" "${TARGETDIR}"

mkdir "${TARGETDIR}/Platform"
# cp -L -f -R  "${SOURCEDIR}/src/ORCA/utils/Platform" "${TARGETDIR}/Platform"
cp -L -f -R  "${SOURCEDIR}/src/ORCA/utils/Platform" "${TARGETDIR}"

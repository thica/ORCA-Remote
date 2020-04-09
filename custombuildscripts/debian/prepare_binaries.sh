#!/bin/bash

# rm -r -f "${BUILDDIR}/dist/ORCA/interfacestmp"
# rm -r -f "${BUILDDIR}/dist/ORCA/scriptstmp"
# rm -r -f "${BUILDDIR}/dist/ORCA/Platform"

cd $BUILD_ZIP
cd /home/kivy/builddest/dist
# zip -r "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}-Debian.zip" ORCA
rm "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}-Debian.7z"
7z a -r "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}-Debian.7z" ORCA

# echo "Copy $BUILD_ZIP to /media/sf_Orca/Development/ORCA/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.zip"
# cp "$BUILD_ZIP" "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.zip"




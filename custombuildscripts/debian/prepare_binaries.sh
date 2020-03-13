#!/bin/bash

rm -r -f "${BUILDDIR}/dist/ORCA/interfaces"
rm -r -f "${BUILDDIR}/dist/ORCA/scripts"
rm -r -f "${BUILDDIR}/dist/ORCA/Platform"

zip -r "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}-Debian.zip" $BUILD_ZIP

# echo "Copy $BUILD_ZIP to /media/sf_Orca/Development/ORCA/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.zip"
# cp "$BUILD_ZIP" "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.zip"




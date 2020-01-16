#!/bin/bash

echo "Copy $BUILD_APK to /media/sf_Orca/Development/ORCA/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk"
cp "$BUILD_APK" "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk"




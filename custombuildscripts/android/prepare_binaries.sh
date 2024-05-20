#!/bin/bash

ECHO "Copy APK"
ECHO "Copy $BUILD_APK to /media/sf_Orca/Development/ORCA/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk"
cp "$BUILD_APK" "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk"
ECHO "Copy AAB"
ECHO "Copy $BUILD_AAB to /media/sf_Orca/Development/ORCA/Deployment/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.aab"
cp "$BUILD_AAB" "/media/upload/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.aab"


# java -jar <PATH_TO_JAR> ...
#for Debug apk command,
#
#bundletool build-apks --bundle=/MyApp/my_app.aab --output=/MyApp/my_app.apks
#For Release apk command,
#
#bundletool build-apks --bundle=/MyApp/my_app.aab --output=/MyApp/my_app.apks
#--ks=/MyApp/keystore.jks
#--ks-pass=file:/MyApp/keystore.pwd
#--ks-key-alias=MyKeyAlias
#--key-pass=file:/MyApp/key.pwd
#Edit:
#
#I have been using following commands while testing my release build for aab(I hope it helps others too):
#
#Download bundletool jar file from Github Repository (Latest release > Assets > bundletool-all-version.jar file). Rename that file to bundletool.jar
#
#Generate your aab file from Android Studio eg: myapp-release.aab
#
#Run following command:
#
#java -jar "path/to/bundletool.jar" build-apks --bundle=myapp-release.aab --output=myapp.apks --ks="/path/to/myapp-release.keystore" --ks-pass=pass:myapp-keystore-pass --ks-key-alias=myapp-alias --key-pass=pass:myapp-alias-pass
#myapp.apks file will be generated
#
#Make sure your device is connected to your machine
#
#Now run following command to install it on your device:
#
#java -jar "path/to/bundletool.jar" install-apks --apks=myapp.apks
#Edit 2:
#
#If you need to extract a single .apk file from the .aab file, you can add a extra param --mode=universal to the bundletool command:
#
#bundletool build-apks --bundle=/MyApp/my_app.aab --output=/MyApp/my_app.apks \
#    --mode=universal \
#    --ks=/MyApp/keystore.jks \
#    --ks-pass=file:/MyApp/keystore.pwd \
#    --ks-key-alias=MyKeyAlias \
#    --key-pass=file:/MyApp/key.pwd
#and execute
#
#unzip -p /MyApp/my_app.apks universal.apk > /MyApp/my_app.apk
#this will generate a single a /MyApp/my_app.apk file that can be shared an installed by any device app installer



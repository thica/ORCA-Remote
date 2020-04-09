#!/bin/bash

# set -x

function ECHO ()
{
  echo -e "$1"
  echo "$1" >> "$LOGFILE"
}


function APT_INSTALL ()
{
  ECHO "\033[1;37mInstall (apt) $1$2  \033[s "
  sudo apt install -y $1$2 >> "$LOGFILE" 2>>"$LOGFILE"
  if [ $? -eq 0 ]; then
    ECHO '\033[u \033[1;32m -> OK\033[1;37m'
  else
    ECHO '\033[u \033[1;31m -> FAIL\033[1;37m'
    exit 1
  fi
}

function PIP_INSTALL ()
{
  ECHO "Install (pip3) $1$2 \033[s"
  pip3 install $3 $1$2  >> "$LOGFILE" 2>>"$LOGFILE"
  if [ $? -eq 0 ]; then
    ECHO '\033[u \033[1;32m -> OK\033[1;37m'
  else
    ECHO '\033[u \033[1;31m -> FAIL\033[1;37m'
    exit 1
  fi

}

# just to activate sudo
sudo ls > /dev/null

export LOGFILE=${HOME}/logfile.txt
# export LOGFILE=/dev/tty

ECHO "Logging to $LOGFILE"
ECHO "Start Log"


cd "${HOME}"
export SOURCEDIR="${HOME}/githubsources"
export TARGETDIR="${HOME}/buildsources"
export BUILDDIR="${HOME}/builddest"
export SNAPSHOTDIR="/media/snapshots"
export SECRETSDIR="/media/secrets"

# Some Versions
# do not change =/== as they belong to apt/pip syntax
export VERSION_CYTHON="==0.29.10"
export VERSION_SETUPTOOLS="==42.0.2"
export VERSION_GIT="=1:2.17.1-1ubuntu0.5"
export VERSION_ZIP="=3.0-11build1"
export VERSION_UNZIP="=6.0-21ubuntu1"
export VERSION_AUTOCONF="=2.69-11"
export VERSION_LIBTOOL="=2.4.6-2"
export VERSION_PKG_CONFIG="=0.29.1*"
export VERSION_ZLIB1G_DEV="=1:1.2.11.dfsg-0ubuntu2"
export VERSION_LIBNCURSES5_DEV="=6.1-1ubuntu1.18.04"
export VERSION_LIBTINFO5="=6.1-1ubuntu1.18.04"
export VERSION_CMAKE="=3.10.2-1ubuntu2.18.04.1"
export VERSION_LIBFFI_DEV="=3.2.1-8"

export VERSION_GIT=""
export VERSION_ZIP=""
export VERSION_UNZIP=""
export VERSION_ZLIB1G_DEV=""
export VERSION_LIBNCURSES5_DEV=""
export VERSION_LIBTINFO5=""
export VERSION_CMAKE=""
export VERSION_LIBFFI_DEV=""
export VERSION_AUTOCONF=""
export VERSION_LIBTOOL=""

ECHO "Reading Secrets"
set -o allexport
source "$SECRETSDIR/secrets.ini"
set +o allexport

echo "Update repositories"
echo "Update repositories" >> "$LOGFILE"
sudo apt update >> "$LOGFILE" 2>>"$LOGFILE"

# Path to Keystore (we create it, if it does not exist)
export P4A_RELEASE_KEYSTORE="$SECRETSDIR/release-key.keystore"


if [ -d "${BUILDDIR}" ]
then
    ECHO "Reusing existing build"
    export "FROMSCRATCH=0"
else
    ECHO "Building from scratch"
    export "FROMSCRATCH=1"
fi

if [ "$FROMSCRATCH" == "1" ]
then
    ECHO "Create Folder"
    mkdir "${SOURCEDIR}" >> "$LOGFILE"
    mkdir "${TARGETDIR}" >> "$LOGFILE"
    mkdir "${BUILDDIR}" >> "$LOGFILE"
fi

ECHO "Copy sources"
cp -R /media/Master/. "${SOURCEDIR}" >> "$LOGFILE"
# rsync -vazCq  /media/Master/. "${SOURCEDIR}" >> $LOGFILE

ECHO "Run custom script to prepare sources"
# 'Prepare/Copy sources (Make the script excutable)'
chmod +x "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"
# do not remove the leading dot
. "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"  >> "$LOGFILE"

ECHO "Copy buildozer.spec"
# Copy buildozer.spec file to target folder (root)'
cp "${SOURCEDIR}/custombuildscripts/android/buildozer.spec" "${BUILDDIR}/buildozer.spec"  >> "$LOGFILE"

if [ "$FROMSCRATCH" == "1" ]
then

  APT_INSTALL "p7zip-full"
  # APT_INSTALL "python3.7"
  APT_INSTALL "python3-pip"

  # make Python3 the default for all calls
  # cd /usr/bin >> $LOGFILE
  # sudo ln -s python3.7 python >> $LOGFILE
  # sudo ln -s python3.7 python3
  cd "${HOME}"

  PIP_INSTALL "setuptools" "$VERSION_SETUPTOOLS"

  ECHO "Unzip buildozer"
  7z x "$SNAPSHOTDIR/buildozer.zip" >> "$LOGFILE"
  mv "${HOME}/buildozer-master" "${HOME}/buildozer" >> "$LOGFILE"
  cd "${HOME}/buildozer"
  ECHO "Build buildozer"
  python setup.py build >> "$LOGFILE" 2>>"$LOGFILE"
  sudo pip3 install -e . >> "$LOGFILE" 2>>"$LOGFILE"
  export PATH="${HOME}/.local/bin:$PATH"

  cd "${HOME}"

  APT_INSTALL "git"             "$VERSION_GIT"
  APT_INSTALL "zip"             "$VERSION_ZIP"
  APT_INSTALL "unzip"           "$VERSION_UNZIP"
  APT_INSTALL "openjdk-8-jdk"
  APT_INSTALL "autoconf"        "$VERSION_AUTOCONF"
  APT_INSTALL "libtool"         "$VERSION_LIBTOOL"
  APT_INSTALL "pkg-config"      "$VERSION_PKG_CONFIG"
  APT_INSTALL "zlib1g-dev"      "$VERSION_ZLIB1G_DEV"
  APT_INSTALL "libncurses5-dev" "$VERSION_LIBNCURSES5_DEV"
  APT_INSTALL "libtinfo5"       "$VERSION_LIBTINFO5"
  APT_INSTALL "python3-venv"
  APT_INSTALL "cmake"           "$VERSION_CMAKE"
  PIP_INSTALL "cython"          "$VERSION_CYTHON"
  APT_INSTALL "cython"
  APT_INSTALL "libffi-dev"      "$VERSION_LIBFFI_DEV"


  # we install the Android SDK manually, as buildozer fails to accept the licenses
  ECHO "Installing Android SDK"
  # download
  wget http://dl.google.com/android/repository/sdk-tools-linux-4333796.zip >> "$LOGFILE"
  mkdir android-sdk >> "$LOGFILE"
  cd android-sdk
  # unzip
  unzip  ~/sdk-tools-linux-4333796.zip >> "$LOGFILE"
  # This is the weakest point: Buildozer seatrches for the latest available build tools version, which might change
  yes|tools/bin/sdkmanager --licenses >> "$LOGFILE"
  yes|tools/bin/sdkmanager "build-tools;30.0.0-rc2" >> "$LOGFILE"

  # we install the ndk as well
  cd ~
  ECHO "Installing Android NDK"
  wget http://dl.google.com/android/repository/android-ndk-r19b-linux-x86_64.zip >> "$LOGFILE"
  unzip ~/android-ndk-r19b-linux-x86_64.zip >> "$LOGFILE"
  # will be extracted to android-ndk-r19b

  # lets use the sdk manager to istall further android tools
  cd ~/android-sdk/tools/bin
  ./sdkmanager tools >> "$LOGFILE"
  yes|./sdkmanager platform-tools >> "$LOGFILE"
  ./sdkmanager --update >> "$LOGFILE"
  ./sdkmanager  "platforms;android-27" >> "$LOGFILE"


  ECHO "Run Buildozer First Time (this will fail ,buildozer bug)"
  # 'Run Buildozer First Time (this will fail (buildozer bug), but shown as succeed)'
  cd "${BUILDDIR}"
  buildozer -v android release

  # Temporary: We now have to remove the broken openssl down and patch the receipe
  rm -rf "${BUILDDIR}"/.buildozer/android/platform/build-armeabi-v7a/packages/openssl
  sed -i 's/1.1.1/1.1.1f/'  "${BUILDDIR}"/.buildozer/android/platform/python-for-android/pythonforandroid/recipes/openssl/__init__.py

  if [ -f $P4A_RELEASE_KEYSTORE ]
  then
    echo ""
    echo "Reusing existing Key/Keystore"
    echo "Reusing existing" >> "$LOGFILE"
  else
    # 'Create Keystore'
    echo ""
    echo "Create Key/Keystore"
    echo "Create Key/Keystore" >> "$LOGFILE"
    keytool -genkey -v -keystore "$P4A_RELEASE_KEYSTORE" -alias "$P4A_RELEASE_KEYALIAS" -keyalg RSA -keysize 2048 -validity 10000 -storepass "$P4A_RELEASE_KEYSTORE_PASSWD" -keypass "$P4A_RELEASE_KEYALIAS_PASSWD" -dname "CN=$ANDROID_KEYSTORE_NAME, OU=$ANDROID_KEYSTORE_ORGANISATION_UNIT, O=$AANDROID_KEYSTORE_ORGANISATION, L=$ANDROID_KEYSTORE_CITY, ST=$ANDROID_KEYSTORE_REGION, C=$ANDROID_KEYSTORE_COUNTRYCODE" >> "$LOGFILE" 2>>"$LOGFILE"
  fi

  # Buildozer installs ths SDK to /home/kivy
  # echo "Install Android Build Tools after failed build (this should be done by buildozer, but the bug has not been removed)"
  # echo "Install Android Build Tools after failed build (this should be done by buildozer, but the bug has not been removed)" >> "$LOGFILE"
  # yes|"${HOME}/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager" "build-tools;29.0.2"  >> "$LOGFILE" 2>>"$LOGFILE"

  # 'Remove the old buildozer app build folder'
  # cd "${BUILDDIR}"
  # rm -r -f "${BUILDDIR}/.buildozer"
fi


echo "Remove any old Build"
echo "Remove any old Build" >> "$LOGFILE"
rm "${BUILDDIR}/bin/*.apk" >> "$LOGFILE" >/dev/null 2>/dev/null

echo "Run buildozer (this should work)"
echo "Run buildozer (this should work)" >> "$LOGFILE"
# 'Run buildozer second time (this should work)'
cd "${BUILDDIR}"
buildozer -v android release

# find the apk
echo "Searching for APK"
echo "Searching for APK" >> "$LOGFILE"
export BUILD_APK=$(find "${BUILDDIR}/bin/" -type f -name "*.apk")
echo "Found APK: $BUILD_APK"
echo "Found APK: $BUILD_APK" >> "$LOGFILE"


# 'Prepare/Copy Binray (Make the script excutable)'
echo "Finalize Binary"
echo "Finalize Binary" >> "$LOGFILE"
chmod +x "${SOURCEDIR}/custombuildscripts/android/prepare_binaries.sh"
. "${SOURCEDIR}/custombuildscripts/android/prepare_binaries.sh"

echo "Done/Finished"
echo "Done/Finished" >> "$LOGFILE"




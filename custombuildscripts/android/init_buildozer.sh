#!/bin/bash

# set -x

function APT_INSTALL ()
{
  echo "Install $1$2"
  echo "Install $1$2" >> $LOGFILE
  sudo apt install -y $1$2 >> $LOGFILE 2>>$LOGFILE
  if [ $? -eq 0 ]; then
    echo OK >> $LOGFILE
  else
    echo FAIL
    echo FAIL >> $LOGFILE
    exit 1
  fi
}

function PIP_INSTALL ()
{
  echo "Install $1$2"
  echo "Install $1$2" >> $LOGFILE
  pip3 install $3 $1$2  >> $LOGFILE 2>>$LOGFILE
  if [ $? -eq 0 ]; then
    echo OK >> $LOGFILE
  else
    echo FAIL
    echo FAIL >> $LOGFILE
    exit 1
  fi

}


# just to activate sudo
sudo ls > /dev/null

export LOGFILE=${HOME}/logfile.txt
# export LOGFILE=/dev/tty

echo "Logging to $LOGFILE"
echo "Start Log" > $LOGFILE


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
export VERSION_PKG_CONFIG="=0.29.1-0ubuntu2"
export VERSION_ZLIB1G_DEV="=1:1.2.11.dfsg-0ubuntu2"
export VERSION_LIBNCURSES5_DEV="=6.1-1ubuntu1.18.04"
export VERSION_LIBTINFO5="=6.1-1ubuntu1.18.04"
export VERSION_CMAKE="=3.10.2-1ubuntu2.18.04.1"
export VERSION_LIBFFI_DEV="=3.2.1-8"

echo "Reading Secrets"
echo "Reading Secrets" >> $LOGFILE
set -o allexport
source "$SECRETSDIR/secrets.ini"
set +o allexport

echo "Update repositories"
echo "Update repositories" >> $LOGFILE
sudo apt update >> $LOGFILE 2>>$LOGFILE

# Path to Keystore (we create it, if it does not exist)
export P4A_RELEASE_KEYSTORE="$SECRETSDIR/release-key.keystore"


if [ -d "${BUILDDIR}" ]
then
    echo "Reusing existing build"
    export "FROMSCRATCH=0"
else
    echo "Building from scratch"
    export "FROMSCRATCH=1"
fi

if [ "$FROMSCRATCH" == "1" ]
then
    echo "Create Folder"
    echo "Create Folder" >> $LOGFILE
    mkdir "${SOURCEDIR}" >> $LOGFILE
    mkdir "${TARGETDIR}" >> $LOGFILE
    mkdir "${BUILDDIR}" >> $LOGFILE
fi

echo "Copy sources"
echo "Copy sources" >> $LOGFILE
cp -R /media/Master/. "${SOURCEDIR}" >> $LOGFILE
# rsync -vazCq  /media/Master/. "${SOURCEDIR}" >> $LOGFILE

echo "Run custom script to prepare sources"
echo "Run custom script to prepare sources" >> $LOGFILE
# 'Prepare/Copy sources (Make the script excutable)'
chmod +x "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"
# do not remove the leading dot
. "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"  >> $LOGFILE

echo "Copy buildozer.spec"
echo "Copy buildozer.spec" >> $LOGFILE
# Copy buildozer.spec file to target folder (root)'
cp "${SOURCEDIR}/custombuildscripts/buildozer.spec" "${BUILDDIR}/buildozer.spec"  >> $LOGFILE

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

  echo "Unzip buildozer"
  echo "Unzip buildozer" >> $LOGFILE
  7z x "$SNAPSHOTDIR/buildozer.zip" >> $LOGFILE
  mv "${HOME}/buildozer-master" "${HOME}/buildozer" >> $LOGFILE
  cd "${HOME}/buildozer"
  echo "Build buildozer"
  echo "Build buildozer" >> $LOGFILE
  python setup.py build >> $LOGFILE 2>>$LOGFILE
  sudo pip3 install -e . >> $LOGFILE 2>>$LOGFILE
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
  APT_INSTALL "libffi-dev"      "$VERSION_LIBFFI_DEV"


  echo "Run Buildozer First Time (this will fail (buildozer bug)"
  echo "Run Buildozer First Time (this will fail (buildozer bug)" >> $LOGFILE
  # 'Run Buildozer First Time (this will fail (buildozer bug), but shown as succeed)'
  cd "${BUILDDIR}"
  timeout 180 buildozer -v android release >> $LOGFILE 2>>$LOGFILE
  # buildozer -v android release


  if [ -f $P4A_RELEASE_KEYSTORE ]
  then
    echo ""
    echo "Reusing existing Key/Keystore"
    echo "Reusing existing" >> $LOGFILE
  else
    # 'Create Keystore'
    echo ""
    echo "Create Key/Keystore"
    echo "Create Key/Keystore" >> $LOGFILE
    keytool -genkey -v -keystore "$P4A_RELEASE_KEYSTORE" -alias "$P4A_RELEASE_KEYALIAS" -keyalg RSA -keysize 2048 -validity 10000 -storepass "$P4A_RELEASE_KEYSTORE_PASSWD" -keypass "$P4A_RELEASE_KEYALIAS_PASSWD" -dname "CN=$ANDROID_KEYSTORE_NAME, OU=$ANDROID_KEYSTORE_ORGANISATION_UNIT, O=$AANDROID_KEYSTORE_ORGANISATION, L=$ANDROID_KEYSTORE_CITY, ST=$ANDROID_KEYSTORE_REGION, C=$ANDROID_KEYSTORE_COUNTRYCODE" >> $LOGFILE 2>>$LOGFILE
  fi

  # Buildozer installs ths SDK to /home/kivy
  echo "Install Android Build Tools after failed build (this should be done by buildozer, but the bug has not been removed)"
  echo "Install Android Build Tools after failed build (this should be done by buildozer, but the bug has not been removed)" >> $LOGFILE
  yes | "${HOME}/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager" "build-tools;29.0.2" >> $LOGFILE 2>>$LOGFILE

  # 'Remove the old buildozer app build folder'
  cd "${BUILDDIR}"
  rm -r -f "${BUILDDIR}/.buildozer"
fi

echo "Remove any old Build"
echo "Remove any old Build" >> $LOGFILE
rm "${BUILDDIR}/bin/*.apk" >> $LOGFILE >/dev/null 2>dev/null


echo "Run buildozer (this should work)"
echo "Run buildozer (this should work)" >> $LOGFILE
# 'Run buildozer second time (this should work)'
cd "${BUILDDIR}"
buildozer -v android release

# find the apk
echo "Searching for APK"
echo "Searching for APK" >> $LOGFILE
export BUILD_APK=$(find "${BUILDDIR}/bin/" -type f -name "*.apk")
echo "Found APK: $BUILD_APK"
echo "Found APK: $BUILD_APK" >> $LOGFILE


# 'Prepare/Copy Binray (Make the script excutable)'
echo "Finalize Binary"
echo "Finalize Binary" >> $LOGFILE
chmod +x "${SOURCEDIR}/custombuildscripts/android/prepare_binaries.sh"
. "${SOURCEDIR}/custombuildscripts/android/prepare_binaries.sh"

echo "Done/Finished"
echo "Done/Finished" >> $LOGFILE




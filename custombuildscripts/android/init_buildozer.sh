#!/bin/bash

# set -x

red=$'\e[1;31m'
grn=$'\e[1;32m'
yel=$'\e[1;33m'
blu=$'\e[1;34m'
mag=$'\e[1;35m'
cyn=$'\e[1;36m'
end=$'\e[0m'

function ECHO ()
{
  printf  "%s\n" "[${yel} Info ${end}] $1"
  printf [Info] %s $1 \n >> "$LOGFILE"
}

function ECHO_SILENT ()
{
  printf [Info] %s $1 \n >> "$LOGFILE"
}

function APT_INSTALL_SILENT ()
{

  printf  "%s" "[ Info ] Installing (apt) $1 ......" >> "$LOGFILE"
  sudo apt install -y $1$2 >> "$LOGFILE" 2>>"$LOGFILE"
  if [ $? -eq 0 ]; then
    printf  " %s\n" "[ OK ]" >> "$LOGFILE"
  else
    printf  "\r%s\n" "[${red}Failed${end}] Install (apt)            $1"
    printf  " %s\n" "[ Failed ]" >> "$LOGFILE"
    exit 1
  fi
}


function APT_INSTALL ()
{

  printf  "%s" "[${yel} Info ${end}] Installing (apt) $1 ....."
  printf  "%s" "[ Info ] Installing (apt) $1 ......" >> "$LOGFILE"
  sudo apt install -y $1$2 >> "$LOGFILE" 2>>"$LOGFILE"
  if [ $? -eq 0 ]; then
    printf  "\r%s\n" "[${grn}  OK  ${end}] Installed (apt) $1          "
    printf  " %s\n" "[ OK ]" >> "$LOGFILE"
  else
    printf  "\r%s\n" "[${red}Failed${end}] Install (apt)            $1"
    printf  " %s\n" "[ Failed ]" >> "$LOGFILE"
    exit 1
  fi
}

function PIP_INSTALL ()
{
  printf  "%s" "[${yel} Info ${end}] Installing (pip3) $1$2 ....."
  printf  "%s" "[ Info ] Installing (pip3) $1$2 ......">> "$LOGFILE"
  pip3 install $3 $1$2  >> "$LOGFILE" 2>>"$LOGFILE"
  if [ $? -eq 0 ]; then
    printf  "\r%s\n" "[${grn}  OK  ${end}] Installed (pip3) $1$2         "
    printf  " %s\n" "[ OK ]" >> "$LOGFILE"
  else
    printf  "\r%s\n" "[${red}Failed${end}] Install (pip3) $1$2           "
    printf  " %s\n" "[ Failed ]" >> "$LOGFILE"
    exit 1
  fi
}

function PYTHON39_Install
{
  # IF we want to update to to python 3.9

  printf  "%s" "[${yel} Info ${end}] Installing (apt) Python3.9 ....."
  printf  "%s" "[ Info ] Installing (apt) Python3.9 ......" >> "$LOGFILE"
  printf  "%s" "[ Info ] apt update ......" >> "$LOGFILE"
  sudo apt update >> "$LOGFILE" 2>/dev/null
  APT_INSTALL_SILENT "software-properties-common"
  printf  "%s" "[ Info ] add-apt-repository -y ppa:deadsnakes/ppa......" >> "$LOGFILE"
  sudo add-apt-repository -y ppa:deadsnakes/ppa >> "$LOGFILE"
  if [ $? -ne 0 ]; then
    printf  "\r%s\n" "[${red}Failed${end}] add-apt-repository             $1"
    printf  " %s\n" "[ Failed ]" >> "$LOGFILE"
    exit 1
  fi


  APT_INSTALL_SILENT "python3.9"
  printf  "%s" "[ Info ] update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9......" >> "$LOGFILE"
  sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 3 >> "$LOGFILE"
  APT_INSTALL_SILENT "python3.9-distutils"
  # todo:check python version
  printf  "\r%s\n" "[${grn}  OK  ${end}] Installed (apt) Python3.9          "
  printf  " %s\n" "[ OK ] Python3.9" >> "$LOGFILE"
}

function BUILDOZER_INSTALL
{
  printf  "%s" "[${yel} Info ${end}] Installing Buildozer (unzip).....        "
  printf  "%s" "[ Info ] Installing Buildozer (unzip)......" >> "$LOGFILE"

  ECHO_SILENT "unzip $SNAPSHOTDIR/buildozer.zip"
  7z x "$SNAPSHOTDIR/buildozer.zip" >> "$LOGFILE"
  mv "${HOME}/buildozer-master" "${HOME}/buildozer" >> "$LOGFILE"
  cd "${HOME}/buildozer"

  printf  "\r%s" "[${yel} Info ${end}] Installing Buildozer (build).....        "
  printf  "%s" "[ Info ] Installing Buildozer (build)......" >> "$LOGFILE"
  python setup.py build >> "$LOGFILE" 2>>"$LOGFILE"

  printf  "\r%s" "[${yel} Info ${end}] Installing Buildozer (install).....       "
  printf  "%s" "[ Info ] Installing Buildozer (install)......" >> "$LOGFILE"
  sudo pip3 install -e . >> "$LOGFILE" 2>>"$LOGFILE"
  export PATH="${HOME}/.local/bin:$PATH"
  cd "${HOME}"
  printf  "\r%s\n" "[${grn}  OK  ${end}] Installed buildozer                        "
  printf  " %s\n" "[ OK ] buildozer" >> "$LOGFILE"
}

# just to activate sudo
sudo ls > /dev/null

export LOGFILE=${HOME}/logfile.txt
rm -f $LOGFILE
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
#export VERSION_CYTHON="==0.29.10" # ubuntu 18.04
export VERSION_CYTHON="==0.29.21"
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

# ECHO "Update repositories"
# sudo apt update >> "$LOGFILE" 2>>"$LOGFILE"

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

  ECHO "Create Folder ${SOURCEDIR}"
  mkdir "${SOURCEDIR}" >> "$LOGFILE"
  ECHO "Create Folder ${TARGETDIR}"
  mkdir "${TARGETDIR}" >> "$LOGFILE"
  ECHO "Create Folder ${BUILDDIR}"
  mkdir "${BUILDDIR}" >> "$LOGFILE"

  APT_INSTALL "p7zip-full"
  PYTHON39_Install
  APT_INSTALL "python3-pip"

  cd "${HOME}"
  PIP_INSTALL "setuptools" "$VERSION_SETUPTOOLS"
  BUILDOZER_INSTALL
  export PATH="${HOME}/.local/bin:$PATH"

  APT_INSTALL "software-properties-common"
  APT_INSTALL "dirmngr"
  APT_INSTALL "apt-transport-https"
  APT_INSTALL "lsb-release"
  APT_INSTALL "ca-certificates"

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

  APT_INSTALL "libssl-dev"
  PIP_INSTALL "rsa"

  # we install the Android SDK manually, as buildozer fails to accept the licenses
  ECHO "Installing Android SDK"
  # download
  wget -q http://dl.google.com/android/repository/sdk-tools-linux-4333796.zip >> "$LOGFILE"  2>/dev/null
  mkdir android-sdk >> "$LOGFILE"
  cd android-sdk
  # unzip
  unzip  ~/sdk-tools-linux-4333796.zip >> "$LOGFILE"
  # This is the weakest point: Buildozer searches for the latest available build tools version, which might change
  yes|tools/bin/sdkmanager --licenses >> "$LOGFILE"
  # yes|tools/bin/sdkmanager "build-tools;30.0.0-rc4" >> "$LOGFILE"
  yes|tools/bin/sdkmanager "build-tools;30.0.1" >> "$LOGFILE"


  # we install the ndk as well
  cd ~
  ECHO "Installing Android NDK"
  wget -q http://dl.google.com/android/repository/android-ndk-r19b-linux-x86_64.zip >> "$LOGFILE"
  unzip ~/android-ndk-r19b-linux-x86_64.zip >> "$LOGFILE"
  # will be extracted to android-ndk-r19b

  # lets use the sdk manager to istall further android tools
  cd ~/android-sdk/tools/bin
  ./sdkmanager tools >> "$LOGFILE"
  yes|./sdkmanager platform-tools >> "$LOGFILE"
  ./sdkmanager --update >> "$LOGFILE"
  ./sdkmanager  "platforms;android-27" >> "$LOGFILE"


  if [ -f $P4A_RELEASE_KEYSTORE ]
  then
    ECHO "Reusing existing Key/Keystore"
  else
    # 'Create Keystore'
    ECHO "Create Key/Keystore"
    keytool -genkey -v -keystore "$P4A_RELEASE_KEYSTORE" -alias "$P4A_RELEASE_KEYALIAS" -keyalg RSA -keysize 2048 -validity 10000 -storepass "$P4A_RELEASE_KEYSTORE_PASSWD" -keypass "$P4A_RELEASE_KEYALIAS_PASSWD" -dname "CN=$ANDROID_KEYSTORE_NAME, OU=$ANDROID_KEYSTORE_ORGANISATION_UNIT, O=$AANDROID_KEYSTORE_ORGANISATION, L=$ANDROID_KEYSTORE_CITY, ST=$ANDROID_KEYSTORE_REGION, C=$ANDROID_KEYSTORE_COUNTRYCODE" >> "$LOGFILE" 2>>"$LOGFILE"
  fi


  # ECHO "Run Buildozer First Time (this will fail) as we do not have the "
  # cd "${BUILDDIR}"
  # buildozer -v android release
  #exit 0

  # Temporary: We now have to remove the broken openssl download and patch the receipe
  ## rm -rf "${BUILDDIR}"/.buildozer/android/platform/build-armeabi-v7a/packages/openssl
  ## sed -i 's/1.1.1/1.1.1f/'  "${BUILDDIR}"/.buildozer/android/platform/python-for-android/pythonforandroid/recipes/openssl/__init__.py


  # Buildozer installs ths SDK to /home/kivy
  # echo "Install Android Build Tools after failed build (this should be done by buildozer, but the bug has not been removed)"
  # echo "Install Android Build Tools after failed build (this should be done by buildozer, but the bug has not been removed)" >> "$LOGFILE"
  # yes|"${HOME}/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager" "build-tools;29.0.2"  >> "$LOGFILE" 2>>"$LOGFILE"

  # 'Remove the old buildozer app build folder'
  # cd "${BUILDDIR}"
  # rm -r -f "${BUILDDIR}/.buildozer"
fi

ECHO "Removing copy of sources in ${SOURCEDIR}"
rm -r ${SOURCEDIR}/* >> "$LOGFILE"
ECHO "Copy sources /media/Master/ to ${SOURCEDIR}"
cp -R /media/Master/. "${SOURCEDIR}" >> "$LOGFILE"
# rsync -vazCq  /media/Master/. "${SOURCEDIR}" >> $LOGFILE

ECHO "Run custom script to prepare sources"
# 'Prepare/Copy sources (Make the script excutable)'
chmod +x "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"
source "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"

ECHO "Copy buildozer.spec"
# Copy buildozer.spec file to target folder (root)'
cp "${SOURCEDIR}/custombuildscripts/android/buildozer.spec" "${BUILDDIR}/buildozer.spec"  >> "$LOGFILE"


ECHO "Remove any old Build"
cd "${BUILDDIR}"
find . -name "*.apk" -type f -delete >> "$LOGFILE"

ECHO "Run buildozer"
# 'Run buildozer second time (this should work)'
cd "${BUILDDIR}"
buildozer -v android release

# find the apk
ECHO "Searching for APK"
export BUILD_APK=$(find "${BUILDDIR}/bin/" -type f -name "*.apk")
ECHO "Found APK: $BUILD_APK"


# 'Prepare/Copy Binray (Make the script excutable)'
ECHO "Finalize Binary"
chmod +x "${SOURCEDIR}/custombuildscripts/android/prepare_binaries.sh"
source "${SOURCEDIR}/custombuildscripts/android/prepare_binaries.sh"

ECHO "Done/Finished"

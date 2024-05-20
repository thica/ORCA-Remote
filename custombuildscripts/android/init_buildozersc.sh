mc
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

function APT_REMOVE ()
{

  printf  "%s" "[${yel} Info ${end}] Removing (apt) $1 ....."
  printf  "%s" "[ Info ] Removing (apt) $1 ......" >> "$LOGFILE"
  sudo apt-get remove -y $1$2 >> "$LOGFILE" 2>>"$LOGFILE"
  if [ $? -eq 0 ]; then
    printf  "\r%s\n" "[${grn}  OK  ${end}] Removed (apt) $1          "
    printf  " %s\n" "[ OK ]" >> "$LOGFILE"
  else
    printf  "\r%s\n" "[${red}Failed${end}] Removed (apt)            $1"
    printf  " %s\n" "[ Failed ]" >> "$LOGFILE"
  fi
}


function PIP_INSTALL ()
{
  printf  "%s" "[${yel} Info ${end}] Installing (pip3) $1$2 ....."
  printf  "%s" "[ Info ] Installing (pip_3) $1$2 ......">> "$LOGFILE"
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

function CREATE_FOLDER ()
{

  printf  "%s" "[${yel} Info ${end}] Create Folder $1 ....."
  printf  "%s" "[ Info ] Create Folder $1 ......" >> "$LOGFILE"
  if ! [ -d "${1}" ]; then
    mkdir "${1}" >> "$LOGFILE"
  fi

  if [ -d "${1}" ]; then
    printf  "\r%s\n" "[${grn}  OK  ${end}] Created Folder $1          "
    printf  " %s\n" "[ OK ]" >> "$LOGFILE"
  else
    printf  "\r%s\n" "[${red}Failed${end}] Create Folder            $1"
    printf  " %s\n" "[ Failed ]" >> "$LOGFILE"
    exit 1
  fi
}

function REMOVE_FOLDER ()
{

  printf  "%s" "[${yel} Info ${end}] Remove Folder $1 ....."
  printf  "%s" "[ Info ] Remove Folder $1 ......" >> "$LOGFILE"
  if  [ -d "${1}" ]; then
    rm -r ${1}/* >> "$LOGFILE" >> "$LOGFILE"
    rm -r ${1} >> "$LOGFILE" >> "$LOGFILE"
  fi

  if ! [ -d "${1}" ]; then
    printf  "\r%s\n" "[${grn}  OK  ${end}] Removed Folder $1          "
    printf  " %s\n" "[ OK ]" >> "$LOGFILE"
  else
    printf  "\r%s\n" "[${red}Failed${end}] Remove Folder            $1"
    printf  " %s\n" "[ Failed ]" >> "$LOGFILE"
    # exit 1
  fi
}



# just to activate sudo
sudo ls > /dev/null

export LOGFILE=${HOME}/logfile_sc.txt
rm -f $LOGFILE
ECHO "Logging to $LOGFILE"
ECHO "Start Log"

cd "${HOME}"
export SOURCEDIR="${HOME}/githubsources_sc"
export TARGETDIR="${HOME}/buildsources_sc"
export BUILDDIR="${HOME}/builddest_sc"
export SNAPSHOTDIR="/media/snapshots"
export SECRETSDIR="/media/secrets"

# Some Versions
# do not change =/== as they belong to apt/pip syntax
#export VERSION_CYTHON="==0.29.10" # ubuntu 18.04
export VERSION_CYTHON="==0.29.33"
# export VERSION_SETUPTOOLS="==58.0.0"
# export VERSION_SETUPTOOLS="==57.5.0"
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

# export VERSION_CYTHON=""
# export VERSION_SETUPTOOLS="==58.0.0"
export VERSION_GIT=""
export VERSION_ZIP=""
export VERSION_UNZIP=""
export VERSION_AUTOCONF=""
export VERSION_LIBTOOL=""
export VERSION_PKG_CONFIG=""
export VERSION_ZLIB1G_DEV=""
export VERSION_LIBNCURSES5_DEV=""
export VERSION_LIBTINFO5=""
export VERSION_CMAKE=""
export VERSION_LIBFFI_DEV=""

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

  CREATE_FOLDER "${SOURCEDIR}"
  CREATE_FOLDER "${TARGETDIR}"
  CREATE_FOLDER "${BUILDDIR}"

  APT_INSTALL "p7zip-full"
  cd "${HOME}"
  sudo apt update >> "$LOGFILE" 2>/dev/null

  APT_INSTALL "git"
  APT_INSTALL "zip"
  APT_INSTALL "unzip"
  APT_INSTALL "openjdk-17-jdk"
  APT_INSTALL "python3-pip"
  APT_INSTALL "autoconf"
  APT_INSTALL "libtool"
  APT_INSTALL "pkg-config"
  APT_INSTALL "zlib1g-dev"
  APT_INSTALL "libncurses5-dev"
  APT_INSTALL "libncursesw5-dev"
  APT_INSTALL "libtinfo5"
  APT_INSTALL "cmake"
  APT_INSTALL "libffi-dev"
  APT_INSTALL "libssl-dev"

  ECHO "Temporary disabling externally managed "
  sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old
  PIP_INSTALL "cython"          "$VERSION_CYTHON"
  PIP_INSTALL "virtualenv"

  BUILDOZER_INSTALL

  ##  PIP_INSTALL  "testresources"
  ##  PIP_INSTALL "setuptools" "$VERSION_SETUPTOOLS"

  APT_INSTALL "software-properties-common"
  APT_INSTALL "dirmngr"
  APT_INSTALL "apt-transport-https"
  APT_INSTALL "lsb-release"
  APT_INSTALL "ca-certificates"

  # read -p "Press [Enter] key to continue"

  PIP_INSTALL "rsa"
fi

  export PATH=$PATH:~/.local/bin/
  if [ -f $P4A_RELEASE_KEYSTORE ]
  then
    ECHO "Reusing existing Key/Keystore"
  else
    # 'Create Keystore'
    ECHO "Create Key/Keystore"
    keytool -genkey -v -keystore "$P4A_RELEASE_KEYSTORE" -alias "$P4A_RELEASE_KEYALIAS" -keyalg RSA -keysize 2048 -validity 10000 -storepass "$P4A_RELEASE_KEYSTORE_PASSWD" -keypass "$P4A_RELEASE_KEYALIAS_PASSWD" -dname "CN=$ANDROID_KEYSTORE_NAME, OU=$ANDROID_KEYSTORE_ORGANISATION_UNIT, O=$AANDROID_KEYSTORE_ORGANISATION, L=$ANDROID_KEYSTORE_CITY, ST=$ANDROID_KEYSTORE_REGION, C=$ANDROID_KEYSTORE_COUNTRYCODE" >> "$LOGFILE" 2>>"$LOGFILE"
  fi

REMOVE_FOLDER "${SOURCEDIR}"
ECHO "Copy sources /media/Master_sc/ to ${SOURCEDIR}"
cp -R /media/Master_sc/. "${SOURCEDIR}" >> "$LOGFILE"
# rsync -vazCq  /media/Master/. "${SOURCEDIR}" >> $LOGFILE

ECHO "Run custom script to prepare sources (Kivy Showcase)"
# 'Prepare/Copy sources (Make the script excutable)'
chmod +x "/media/Master/custombuildscripts/android/prepare_sources_sc.sh"
source "/media/Master/custombuildscripts/android/prepare_sources_sc.sh"

ECHO "Copy buildozer.spec  (Kivy Showcase)"
# Copy buildozer.spec file to target folder (root)'
cp "/media/Master/custombuildscripts/android/buildozer_sc.spec" "${BUILDDIR}/buildozer.spec"  >> "$LOGFILE"


ECHO "Remove any old Build"
cd "${BUILDDIR}"
find . -name "*.apk" -type f -delete >> "$LOGFILE"
find . -name "*.aab" -type f -delete >> "$LOGFILE"
find . -name "*.apks" -type f -delete >> "$LOGFILE"

ECHO "Run buildozer"
# 'Run buildozer second time (this should work)'
cd "${BUILDDIR}"
# buildozer -v android release
buildozer -v android debug

# find the apk
## ECHO "Searching for AAB"
## export BUILD_AAB=$(find "${BUILDDIR}/bin/" -type f -name "*.aab")
## ECHO "Found AAB: $BUILD_AAB"

## ECHO "Extract APKs"
## java -jar "$SNAPSHOTDIR/bundletool-all-1.11.2.jar" build-apks --mode=universal --ks="$P4A_RELEASE_KEYSTORE" --ks-pass=pass:"$P4A_RELEASE_KEYSTORE_PASSWD" --ks-key-alias="$P4A_RELEASE_KEYALIAS" --key-pass=pass:"$P4A_RELEASE_KEYALIAS_PASSWD"
# --bundle=$BUILD_AAB --output=$BUILDDIR/bin/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apks
## unzip -p $BUILDDIR/bin/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apks > $BUILDDIR/bin/${varAPPNAME4}-${varORCABRANCH}-${varORCAVERSION}.apk

ECHO "Searching for APK"
export BUILD_APK=$(find "${BUILDDIR}/bin/" -type f -name "*.apk")
ECHO "Found APK: $BUILD_APK"


# 'Prepare/Copy Binray (Make the script executable)'
ECHO "Finalize Binary"
chmod +x "/media/Master/custombuildscripts/android/prepare_binaries_sc.sh"
source "/media/Master/custombuildscripts/android/prepare_binaries_sc.sh"

ECHO "Done/Finished"

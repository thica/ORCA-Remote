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
    printf  " %s\n" "[Failed]" >> "$LOGFILE"
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
    printf  " %s\n" "[Failed]" >> "$LOGFILE"
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
    printf  " %s\n" "[Failed]" >> "$LOGFILE"
    exit 1
  fi
}

function PIP2_INSTALL ()
{
  printf  "%s" "[${yel} Info ${end}] Installing (pip3) $1$2 ....."
  printf  "%s" "[ Info ] Installing (pip3) $1$2 ......">> "$LOGFILE"
  pip install $3 $1$2  >> "$LOGFILE" 2>>"$LOGFILE"
  if [ $? -eq 0 ]; then
    printf  "\r%s\n" "[${grn}  OK  ${end}] Installed (pip3) $1$2         "
    printf  " %s\n" "[ OK ]" >> "$LOGFILE"
  else
    printf  "\r%s\n" "[${red}Failed${end}] Install (pip3) $1$2           "
    printf  " %s\n" "[Failed]" >> "$LOGFILE"
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

  # We add kivy here to the repo
  printf  "%s" "[ Info ] add-apt-repository -y ppa:kivy-team/kivy......"
  sudo add-apt-repository -y ppa:kivy-team/kivy >> "$LOGFILE"

  APT_INSTALL_SILENT "python3.9"
  printf  "%s" "[ Info ] update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9......" >> "$LOGFILE"
  sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 3 >> "$LOGFILE"
  APT_INSTALL_SILENT "python3.9-distutils"
  # todo:check python version
  printf  "\r%s\n" "[${grn}  OK  ${end}] Installed (apt) Python3.9          "
  printf  " %s\n" "[ OK ] Python3.9" >> "$LOGFILE"
}

# just to activate sudo
sudo ls > /dev/null
export LOGFILE=${HOME}/logfile.txt
# export LOGFILE=/dev/tty
rm -f $LOGFILE
ECHO "Logging to $LOGFILE"
ECHO "Start Log"


cd "${HOME}"
export SOURCEDIR="${HOME}/githubsources"
export TARGETDIR="${HOME}/buildsources"
export BUILDDIR="${HOME}/builddest"
export SNAPSHOTDIR="/media/snapshots"
export SECRETSDIR="/media/secrets"
export PYTHONDONTWRITEBYTECODE=1


ECHO "Reading Secrets"
set -o allexport
source "$SECRETSDIR/secrets.ini"
set +o allexport

ECHO "Update repositories"
sudo apt update >> "$LOGFILE" 2>>"$LOGFILE"

if [ -d "${BUILDDIR}" ]
then
    ECHO "Reusing existing build"
    export "FROMSCRATCH=0"
else
    ECHO "Building from scratch"
    export "FROMSCRATCH=1"
fi

export "FROMSCRATCH=1"

if [ "$FROMSCRATCH" == "1" ]
then
  ECHO "Create Folder ${SOURCEDIR}"
  mkdir "${SOURCEDIR}" >> "$LOGFILE"
  ECHO "Create Folder ${TARGETDIR}"
  mkdir "${TARGETDIR}" >> "$LOGFILE"
  ECHO "Create Folder ${BUILDDIR}"
  mkdir "${BUILDDIR}" >> "$LOGFILE"
fi

ECHO "Copy sources"
cp -R /media/Master/. "${SOURCEDIR}" >> "$LOGFILE"

ECHO "Run custom script to prepare sources"
# 'Prepare/Copy sources (Make the script excutable)'
chmod +x "${SOURCEDIR}/custombuildscripts/debian/prepare_sources.sh"
source "${SOURCEDIR}/custombuildscripts/debian/prepare_sources.sh"


if [ "$FROMSCRATCH" == "1" ]
then

  APT_INSTALL "p7zip-full"
  # PYTHON39_Install
  APT_INSTALL "python3-pip"
  APT_INSTALL "python3-dev"
  APT_INSTALL "python3-venv"
  sudo add-apt-repository -y ppa:kivy-team/kivy >> "$LOGFILE"
  # APT_INSTALL "python3-pip"
  # PIP_INSTALL "pip"

  # sudo ln -sf /usr/bin/python3.7 /usr/bin/python3
  # cd "/usr/lib/python3/dist-packages"
  # sudo ln -s "/usr/lib/python3/dist-packages/apt_pkg.cpython-36m-x86_64-linux-gnu.so" "/usr/lib/python3/dist-packages/apt_pkg.so"
  # cd ~

  APT_INSTALL "zip"             "$VERSION_ZIP"
  APT_INSTALL "unzip"           "$VERSION_UNZIP"

  # install kivy
  # sudo add-apt-repository -y ppa:kivy-team/kivy
  APT_INSTALL "git"
  APT_INSTALL "ffmpeg"
  APT_INSTALL "libsdl2-dev"
  APT_INSTALL "libsdl2-image-dev"
  APT_INSTALL "libsdl2-mixer-dev"
  APT_INSTALL "libsdl2-ttf-dev"
  APT_INSTALL "libportmidi-dev"
  APT_INSTALL "libswscale-dev"
  APT_INSTALL "libavformat-dev"
  APT_INSTALL "libavcodec-dev"
  APT_INSTALL "zlib1g-dev"
  APT_INSTALL "libgstreamer1.0-0"
  APT_INSTALL "gstreamer1.0-plugins-base"
  APT_INSTALL "gstreamer1.0-plugins-good"
  PIP_INSTALL "virtualenv"
  PIP_INSTALL "setuptools"

  export USE_X11=1
  PIP_INSTALL Cython
  PIP_INSTALL kivy[base]
  PIP_INSTALL kivy_examples
  PIP_INSTALL git+https://github.com/kivy/buildozer.git@master
  PIP_INSTALL git+https://github.com/kivy/plyer.git@master
  PIP_INSTALL "pygments"
  PIP_INSTALL "docutils"
  # python3 -c "import pkg_resources; print(pkg_resources.resource_filename('kivy', '../share/kivy-examples'))"
  PIP_INSTALL "PyInstaller"

  ECHO "Run custom script to install further modules required by the app"
  chmod +x "${SOURCEDIR}/custombuildscripts/debian/install_modules.sh"
  source "${SOURCEDIR}/custombuildscripts/debian/install_modules.sh"

  ECHO "Prepare sources"
  chmod +x "${SOURCEDIR}/custombuildscripts/debian/prepare_sources.sh"
  source "${SOURCEDIR}/custombuildscripts/debian/prepare_sources.sh"

  cp -r ${SOURCEDIR}/custombuildscripts/debian/patch_kivy.1.11/pyinstaller_hooks ~/.local/lib/python3.7/site-packages/kivy/tools/packaging

fi

ECHO "Remove any old Build"
rm -r "${BUILDDIR}/dist" -y >> "$LOGFILE" >/dev/null 2>/dev/null

ECHO "Copy debian.spec file to target folder (root)"
cp "${SOURCEDIR}/custombuildscripts/debian/debian.spec" "${BUILDDIR}/debian.spec" >> "$LOGFILE"

# read -p "Press [Enter] key to start backup..."


ECHO Delete __pychache__ folder those might confuse pyinstaller
cd "${TARGETDIR}"
python3 -c "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"

# read -p "Press [Enter] key to start backup..."



ECHO Run PyInstaller
cd "${BUILDDIR}"
python3 -B -m PyInstaller --clean --paths ~/.local/lib/python3.7/site-packages --icon="${SOURCEDIR}/custombuildscripts/debian/OrcaLogo.ico" debian.spec

# read -p "Press [Enter] key to start backup..."


# find the zip
ECHO "Searching for binary"
export BUILD_ZIP="${BUILDDIR}"
ECHO "Found DEST: $BUILD_ZIP"

# 'Prepare/Copy Binray (Make the script excutable)'
ECHO "Finalize Binary"
chmod +x "${SOURCEDIR}/custombuildscripts/debian/prepare_binaries.sh"
source "${SOURCEDIR}/custombuildscripts/debian/prepare_binaries.sh"
ECHO "Done Finished"

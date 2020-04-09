#!/bin/bash

set +x

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

function PIP2_INSTALL ()
{
  echo "Install (PIP2) $1$2"
  echo "Install (PIP2) $1$2" >> "$LOGFILE"
  pip install $3 $1$2  >> "$LOGFILE" 2>>"$LOGFILE"
  if [ $? -eq 0 ]; then
    echo OK >> "$LOGFILE"
  else
    echo FAIL
    echo FAIL >> "$LOGFILE"
    exit 1
  fi

}

# just to activate sudo
sudo ls > /dev/null
export LOGFILE=${HOME}/logfile.txt
# export LOGFILE=/dev/tty

ECHO "Logging to $LOGFILE"
ECHO "Start Log"

ECHO "Disable Screensaver"
gsettings set org.gnome.desktop.screensaver lock-enabled false

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
    ECHO "Create Folder"
    mkdir "${SOURCEDIR}" >> "$LOGFILE"
    mkdir "${TARGETDIR}" >> "$LOGFILE"
    mkdir "${BUILDDIR}" >> "$LOGFILE"
fi


ECHO "Copy sources"
cp -R /media/Master/. "${SOURCEDIR}" >> "$LOGFILE"

ECHO "Run custom script to prepare sources"
# 'Prepare/Copy sources (Make the script excutable)'
chmod +x "${SOURCEDIR}/custombuildscripts/debian/prepare_sources.sh"
# do not remove the leading dot
. "${SOURCEDIR}/custombuildscripts/debian/prepare_sources.sh"  >> "$LOGFILE"


if [ "$FROMSCRATCH" == "1" ]
then


  APT_INSTALL "p7zip-full"
  APT_INSTALL "python3-dev"
  APT_INSTALL "python3-venv"
  APT_INSTALL "python3-pip"
  PIP_INSTALL "pip"

  sudo ln -sf /usr/bin/python3.7 /usr/bin/python3
  cd "/usr/lib/python3/dist-packages"
  sudo ln -s "/usr/lib/python3/dist-packages/apt_pkg.cpython-36m-x86_64-linux-gnu.so" "/usr/lib/python3/dist-packages/apt_pkg.so"
  cd ~

  APT_INSTALL "zip"             "$VERSION_ZIP"
  APT_INSTALL "unzip"           "$VERSION_UNZIP"

  # install kivy
  sudo add-apt-repository -y ppa:kivy-team/kivy
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
  APT_INSTALL "libgstreamer1.0"
  APT_INSTALL "gstreamer1.0-plugins-base"
  APT_INSTALL "gstreamer1.0-plugins-good"
  PIP_INSTALL "virtualenv"
  PIP_INSTALL "setuptools"

  export USE_X11=1
  PIP_INSTALL Cython==0.29.10
  PIP_INSTALL kivy==1.11.0
  PIP_INSTALL git+https://github.com/kivy/buildozer.git@master
  PIP_INSTALL git+https://github.com/kivy/plyer.git@master

  PIP_INSTALL "pygments"
  PIP_INSTALL "docutils"

  PIP_INSTALL kivy==1.11.0
  #a short test
  python3 -c "import pkg_resources; print(pkg_resources.resource_filename('kivy', '../share/kivy-examples'))"

  PIP_INSTALL "PyInstaller"

  ECHO "Run custom script to install further modules required by the app"
  chmod +x "${SOURCEDIR}/custombuildscripts/debian/install_modules.sh"
  # do not remove the leading dot
. "${SOURCEDIR}/custombuildscripts/debian/install_modules.sh"  >> "$LOGFILE"


  ECHO "Prepare sources"
  chmod +x "${SOURCEDIR}/custombuildscripts/debian/prepare_sources.sh"
  # do not remove the leading dot
. "${SOURCEDIR}/custombuildscripts/debian/prepare_sources.sh"  >> "$LOGFILE"

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
. "${SOURCEDIR}/custombuildscripts/debian/prepare_binaries.sh"


ECHO "Done Finished"

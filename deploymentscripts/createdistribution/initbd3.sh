#!/bin/bash

# set -x

# just to activate sudo
sudo ls

cd "${HOME}"
export SOURCEDIR="${HOME}/githubsources"
export TARGETDIR="${HOME}/buildsources"
export BUILDDIR="${HOME}/builddest"


mkdir "${SOURCEDIR}"
mkdir "${TARGETDIR}"
mkdir "${BUILDDIR}"

# rsync -vazC  /media/Master/. "${SOURCEDIR}"

cp -R /media/Master/. "${SOURCEDIR}"


sudo apt update
sudo apt-get -y install p7zip-full
sudo apt-get -y install python3.7
sudo apt-get -y install python3-pip

# make Python3 the default for all calls
cd /usr/bin
sudo ln -s python3.7 python
cd "${HOME}"

# some steps to install buildozer 
# We us a snapshot, as buildozer does not ave proper versioning  
pip3 install setuptools
7z x "/media/sf_Orca/buildozer.zip"
mv "${HOME}/buildozer-master" "${HOME}/buildozer"
cd "${HOME}/buildozer"
python setup.py build
sudo pip3 install -e .
export PATH="${HOME}/.local/bin:$PATH"


cd "${HOME}"

# some of the dependencies should be in the runner image, but it doesn't cost time to 
# request to install them again, as apt will skip it, if allready there

# Install dependencies Git 
sudo apt install -y git 

# 'Install dependencies Zip'
sudo apt install -y zip

# 'Install dependencies Unzip'
sudo apt install -y unzip 

# 'Install dependencies  openjdk-8-jdk'
sudo apt install -y openjdk-8-jdk

# 'Install dependencies autoconf'
sudo apt install -y autoconf=2.69-11

# 'Install dependencies libtool'
sudo apt install -y libtool=2.4.6-2

# 'Install dependencies pkg-config'
sudo apt install -y pkg-config

# 'Install dependencies zlib1g-dev'
sudo apt install -y zlib1g-dev

# 'Install dependencies libncurses5-dev'
sudo apt install -y libncurses5-dev

# 'Install dependencies libtinfo5'
sudo apt install -y libtinfo5

# 'Install dependencies python3-venv'
sudo apt install -y python3-venv

# 'Install dependencies cmake'
sudo apt install -y cmake

# Install dependencies #3 (cython,virtualenv, ..)'
sudo pip3 install --user --upgrade cython==0.29.10 virtualenv

sudo apt install -y libffi-dev

# we look to find a custom prepare sources script in  githubsources/custombuildscripts/android/prepare_sources.sh
# if yes, this will be executed, and it should place the final sources in buildsources
# if no custom script is available, then it will just copy the githubsources to the buildsources
# 'Prepare/Copy sources (Make the script excutable)'
chmod +x "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"
/bin/bash "${SOURCEDIR}/custombuildscripts/android/prepare_sources.sh"

# Copy buildozer.spec file to target folder (root)'
cp "${SOURCEDIR}/custombuildscripts/buildozer.spec" "${BUILDDIR}/buildozer.spec"

    # - name: 'Adjust spec file'
    #  run: export MYHOME=$(pwd) &&
    #       rpl HOME "$MYHOME" buildsources/buildozer.spec 

    # - name: Cache App Buildozer Folder
    #  id: cache-App-Buildozer
    #  uses: actions/cache@v1
    #  with:
    #    path: buildsources/.buildozer
    #    key: ${{ runner.os }}-App-Buildozer

    # - name: Cache SDK Buildozer Folder
    #   id: cache-SDK-Buildozer
    #   uses: actions/cache@v1
    #   with:
    #     path: .buildozer
    #     key: ${{ runner.os }}-SDK-Buildozer


    # we do download the sdk manually
    # buildozer is buggy
    # the preinstalled in the runner needs sudo
    # buildozer doesn't work with sudo
    
    # - name: 'Download Android SDK'
    #  run: mkdir android-sdk &&
    #       cd android-sdk &&
    #       wget http://dl.google.com/android/repository/sdk-tools-linux-4333796.zip &&
    #       unzip -q sdk-tools-linux-4333796.zip &&
    #       rm sdk-tools-linux-4333796.zip &&
    #       cd ..

    # - name: 'Check Install Android Build Tools after failed build (this should be done by buildozer, but the bug has not been removed)'
    #  run: yes | android-sdk/tools/bin/sdkmanager "build-tools;29.0.2"

# 'Run Buildozer First Time (this will fail (buildozer bug), but shown as succeed)'
cd "${BUILDDIR}"
timeout 60 buildozer -v android release

# 'Create Keystore'
export P4A_RELEASE_KEYSTORE="$PWD/release-key.keystore"
export P4A_RELEASE_KEYSTORE_PASSWD=mypasswort
export P4A_RELEASE_KEYALIAS_PASSWD=mypasswort
export P4A_RELEASE_KEYALIAS=androidreleasekey
keytool -genkey -v -keystore "$P4A_RELEASE_KEYSTORE" -alias "$P4A_RELEASE_KEYALIAS" -keyalg RSA -keysize 2048 -validity 10000 -storepass "$P4A_RELEASE_KEYSTORE_PASSWD" -keypass "$P4A_RELEASE_KEYALIAS_PASSWD" -dname "CN=$ANDROID_KEYSTORE_CN, OU=$ANDROID_KEYSTORE_OU, O=$ANDROID_KEYSTORE_O, L=$ANDROID_KEYSTORE_L, S=$ANDROID_KEYSTORE_S, C=$ANDROID_KEYSTORE_C"

# Buildozer installs ths SDK to /home/kivy
# 'Install Android Build Tools after failed build (this should be done by buildozer, but the bug has not been removed)'
yes | "${HOME}/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager" "build-tools;29.0.2"

# 'Remove the old buildozer app build folder'
cd "${BUILDDIR}"
rm -r -f "${BUILDDIR}/.buildozer"


# 'Run buildozer second time (this should work)'
cd "${BUILDDIR}"
buildozer -v android release

# find the apk
export BUILD_APK=$(find buildsources/bin/ -type f -name "*.apk")
echo "Found filename $BUILD_APK"
mv "$BUILD_APK" "buildsources/bin/KivyApp_Android.apk"

# 'Adjust/rename binary (Run the script)'
# sh KivyGitActionsBuild/scripts/android/prepare_bin.sh

# 'Upload Binary'
# "buildsources/bin/KivyApp_Android.apk"


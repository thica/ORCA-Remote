#!/bin/sh

# noting to do with pure compile
cp /mnt/ORCA/development/ORCA/Master/deploymentscripts/compile.sh ~/compile.sh
# /mnt/ORCA/development/ORCA/Master/deploymentscripts/buildozer/initbd2.sh
# sudo usermod -aG vboxsf kivy
# mkdir ~/keystores/
# keytool -genkey -v -keystore ~/keystores/orca-release-key.keystore -alias orca-release-key -keyalg RSA -keysize 2048 -validity 10000
# export P4A_RELEASE_KEYSTORE=~/keystores/orca-release-key.keystore
# export P4A_RELEASE_KEYSTORE_PASSWD=android
# export P4A_RELEASE_KEYALIAS_PASSWD=android
# export P4A_RELEASE_KEYALIAS=orca-release-key


#cth Undocumented requierement: Add the google certificate to the keystore




# cth !!! ausgelassen
wget https://pki.google.com/GIAG2.crt
cd /etc/ssl/certs/java/
sudo keytool -import -noprompt -storepass changeit -alias googleCA -file ~/GIAG2.crt -keystore cacerts 
cd ~

# undocmented reqierement
sudo apt-get install zlib1g-dev


#cth GIT is a undocumented prerequierement and needs to get installed manually
sudo apt-get -y install git


#cth PIP is a undocumented prerequierement  and needs to get installed manually
sudo apt-get -y install python3-pip
sudo apt-get -y install autoconf

 
# taken from https://buildozer.readthedocs.io/en/latest/installation.html#targeting-android
sudo pip3 install --upgrade cython==0.21
sudo dpkg --add-architecture i386
sudo apt-get update

sudo apt-get -y install ccache git libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 openjdk-8-jdk unzip zlib1g-dev zlib1g:i386


# taken from https://kivy.org/docs/guide/packaging-android.html
git clone https://github.com/kivy/buildozer.git
cd buildozer
sudo python3 setup.py install
buildozer init
cd ~


# lets download p4a
# cd ~
# git clone https://github.com/kivy/python-for-android.git
# cd python-for-android
# pip install --user -e .

# We need to install the ndk manually as buildozer fails on everything larger than 10e
# cd ~
# mkdir ~/.buildozer
# mkdir ~/.buildozer/android
# mkdir ~/.buildozer/android/platform
# wget https://dl.google.com/android/repository/android-ndk-r16b-linux-x86_64.zip
# unzip android-ndk-r16b-linux-x86_64.zip -d ~/.buildozer/android/platform
# rm android-ndk-r16b-linux-x86_64.zip 

# Buildozer can handle anything else larger than API 18
# cd ~
# mkdir ~/.buildozer
# mkdir ~/.buildozer/android
# mkdir ~/.buildozer/android/platform
# cd ~/.buildozer/android/platform
# wget https://dl.google.com/android/android-sdk_r22-linux.tgz
# tar xzf android-sdk_r22-linux.tgz -C  ~/.buildozer/android/platform
# mv ~/.buildozer/android/platform/android-sdk-linux ~/.buildozer/android/platform/android-sdk-22


#cth lets download one of the examples
cd ~
mkdir settings
cd settings
wget https://raw.githubusercontent.com/kivy/kivy/master/examples/settings/main.py
wget https://raw.githubusercontent.com/kivy/kivy/master/examples/settings/android.txt

#create a simple spec file with some extended reqs
echo "[app]" > buildozer.spec
echo "title = Settings" >> buildozer.spec
echo "package.name = settings" >> buildozer.spec
echo "package.domain = org.settings" >> buildozer.spec
echo "version = 1.1.0" >> buildozer.spec
echo "requirements = python3crystax,,sdl2,android,kivy,future,openssl,png,pil,wakeonlan" >> buildozer.spec
echo "orientation = all" >> buildozer.spec
echo "fullscreen = 0" >> buildozer.spec
echo "source.dir = /home/kivy/settings" >> buildozer.spec
echo "p4a.branch = stable" >> buildozer.spec
echo "android.ndk_path = ~/buildozer/crystax-ndk-10.3.2-linux-x86_64"

# echo "p4a.source_dir = /home/kivy/python-for-android/" >> buildozer.spec	
# echo "android.api = 22" >> buildozer.spec
# echo "android.minapi = 22" >> buildozer.spec
# echo "android.sdk = 22" >> buildozer.spec
# echo "android.ndk = 16b" >> buildozer.spec


# 18,18,18,9c: works, copy error at end
# 19,19,19.9c: not working, gzip: stdin: not in gzip format, tar: Child returned status 1, tar: Error is not recoverable: exiting now, Command failed: tar xzf android-sdk_r19-linux.tgz
# 20,20,20,9c: not working, zlib headers must be installed,
# 20,20,20,9c: not working, zlib headers installed, but error "Requested API target 20 is not available, install it with the SDK android tool."
# 18,18,18,16b: not working: ./android-ndk-r16b-linux-x86_64.bin: 3: ./android-ndk-r16b-linux-x86_64.bin: Syntax error: newline unexpected
# 18,18,18,11c: not working: ./android-ndk-r11c-linux-x86_64.bin: 3: ./android-ndk-r11c-linux-x86_64.bin: Syntax error: newline unexpected
# 18,18,18,10e: works, copy error at end
# 19,19,19.10e: not working, gzip: stdin: not in gzip format, tar: Child returned status 1, tar: Error is not recoverable: exiting now, Command failed: tar xzf android-sdk_r19-linux.tgz

# python3 support
# Download Crystax NDK
cd ~/buildozer
wget https://www.crystax.net/download/crystax-ndk-10.3.2-linux-x86_64.tar.xz
tar -xvf crystax-ndk-10.3.2-linux-x86_64.tar.xz


#and kick it off (and it will fail due to a bug in p4a) (/home/kivy/settings/.buildozer/android/platform/build/dists/settings/tmp-src/org/kivy/android/PythonService.java:108: error: multi-catch statement is not supported in -source 1.5)
buildozer -v android debug
# So replace the buggy file
# cp /mnt/ORCA/Development/ORCA/Master/deploymentscripts/buildozer/PythonService.java ~/settings/.buildozer/android/platform/build/dists/settings/tmp-src/org/kivy/android/PythonService.java
# and do it again
# buildozer -v android debug
# So we have an apk in  /home/kivy/settings/.buildozer/android/platform/build/dists/settings/bin/Settings-1.1.0-debug.apk
# But we still get an eror, as Buildozer tries to proceed with /home/kivy/settings/.buildozer/android/platform/build/dists/settings/build/outputs/apk/settings-debug.apk


# Reimport the Keystore
mkdir ~/keystores/
cp /mnt/ORCA/Deployment/Key/orca-release-key.keystore ~/keystores/orca-release-key.keystore





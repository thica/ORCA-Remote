#!/bin/sh

# Install necessary system packages
mkdir buildozer
cd buildozer
#sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install -y build-essential ccache git zlib1g-dev python2.7 python2.7-dev libncurses5:i386 libstdc++6:i386 zlib1g:i386 openjdk-8-jdk unzip

sudo apt-get install autoconf

# Bootstrap a current Python environment
sudo apt-get remove --purge -y python-virtualenv python-pip python-setuptools
# wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | sudo python2.7
# wget https://github.com/pypa/setuptools
sudo apt-get install python-setuptools
rm -f setuptools*.zip
#sudo easy_install-2.7 -U pip
#sudo pip2.7 install -U virtualenv
sudo apt-get install python-pip python-dev build-essential 
sudo pip install --upgrade pip 
sudo pip install --upgrade virtualenv 


# Install current version of Cython
sudo apt-get remove --purge -y cython
#sudo pip2.7 install cython==0.20.1
sudo pip install cython


# Install Buildozer from master
sudo pip2.7 install -U git+https://github.com/kivy/buildozer.git@master

#cd buildozer
#sudo python2.7 setup.py install

git clone https://github.com/kivy/buildozer.git
cd buildozer


#export P4A_RELEASE_KEYSTORE=orca-release-key.keystore
#$ export P4A_RELEASE_KEYSTORE_PASSWD=android
#$ export P4A_RELEASE_KEYALIAS_PASSWD=android
#$ export P4A_RELEASE_KEYALIAS=<ALIAS>


orca-release-key.keystore

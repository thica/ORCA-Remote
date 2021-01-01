How to create a virtual image for compiling the apk

# Example for virtual box

Create a ubuntu instance based on 20.04. standard desktop installation
Choose "kivy" as the user name
Install the guest tools



Be aware: the build script is versioned on Ubuntu 20.04 libraries

Ensure the shared folder to the ORCA files are mounted
Add the user to the Vbox group to grant access
sudo usermod -G vboxsf -a kivy

Create some subfolders which points to some ORCA folder
* /media/Master
* /media/snapshots
* /media/secrets
* /media/upload

For my setup:

sudo ln -s /media/sf_Orca/Development/ORCA/Master /media/Master
sudo ln -s /media/sf_Orca/Development/snapshots /media/snapshots
sudo ln -s /media/sf_Orca/Development/secrets /media/secrets
sudo ln -s /media/sf_Orca/Development/ORCA/Deployment /media/upload

This is tested for buildozer version downloaded 27.10.2019 from Master

* /media/secrets should point to a folder where to store the secrets

Folder contents:
/media/Master:
    should point to the (Github) Master folder of Orca files
/media/snapshots:
    should point to a folder to find the buildozer version to use as a zip file
    This is tested for buildozer version
/media/secrets:
    should point to a folder containing the secrets.txt for passwords, etc
/media/upload:
    should point to a folder to store the compiled app


for ubuntu 20.04 run this once before
    remove unattended updates (unattanded updates might lock the install process)
    sudo apt remove unattended-upgrades
    sudo apt -y install software-properties-common dirmngr apt-transport-https lsb-release ca-certificates


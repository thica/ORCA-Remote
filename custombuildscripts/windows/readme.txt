How to create a virtual image for compiling the exe/zip (windows)

# Example for virtual box

Create a windows 10 image

Create some subfolders which points to some ORCA folder
* c:\media\Master
* c:\/media\snapshots
* c\media\secrets

For my setup:

mklink /D c:\media\Master \\VBoxsvr\CTPrivat\Orca\Development\ORCA\Master
mklink /D c:\media\snapshots \\VBoxsvr\CTPrivat\Orca\Development\snapshots
mklink /D c:\media\secrets \\VBoxsvr\CTPrivat\Orca\Development\secrets


* /media/secrets should point to a folder where to store the secrets

Folder contents:
/media/Master:
    should point to the (Github) Master folder of Orca files
/media/snapshots:
    should point to a folder to find the buildozer version to use as a zip file
    This is tested for buildozer version
/media/secrets:
    should point to a folder containing the secrets.txt for passwords, etc



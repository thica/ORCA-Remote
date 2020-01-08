cd /Users/thica/Orca
pyinstallerdir="/Users/thica/ORCA/pyinstaller-2.0"
spec="ORCA.spec"

fil="/Volumes/ctprivat/ORCA/Development/ORCA/Master/src/ORCA.py"

if [ -f $fil ]
then

  #read through the file looking for the word self.fVersion=

  while read line
  do
    echo $line | grep -q self.sVersion= >nul
    if [ $? == 0 ]; then
    varORCAVERSION=`echo $line  | cut -d = -f2 | cut -d : -f1`
	break
    fi
  done < $fil

fi


varORCAVERSION=`echo $varORCAVERSION | tr -d "\n"`
varORCAVERSION=`echo $varORCAVERSION | tr -d "\r"`
varORCAVERSION="${varORCAVERSION%\"}"
varORCAVERSION="${varORCAVERSION#\"}"

echo "Version Found1: [$varORCAVERSION]"

if [ -f $fil ]
then

  #read through the file looking for the word self.sBranch=

  while read line
  do
    echo $line | grep -q self.sBranch= >nul
    if [ $? == 0 ]; then
    varORCABRANCH=`echo $line  | cut -d = -f2 | cut -d : -f1`
    break
    fi
  done < $fil

fi


varORCABRANCH=`echo $varORCABRANCH | tr -d "\n"`
varORCABRANCH=`echo $varORCABRANCH | tr -d "\r"`
varORCABRANCH="${varORCABRANCH%\"}"
varORCABRANCH="${varORCABRANCH#\"}"

echo "Branch Found: [$varORCABRANCH]"



echo "$varORCAVERSION" > "/Volumes/ctprivat/ORCA/Development/ORCA/Master/src/dataversion_"${varORCAVERSION}.txt

set -x verbose #echo on
# Title
varAPPNAME1="ORCA Remote Control"
# Automatic Created Filename, blanks excluded
varAPPNAME2=ORCARemoteControl
#filename prefix for final zip
varAPPNAME3=orca
# Source Folder
varSOURCE="/Volumes/ctprivat/ORCA/Development/ORCA/Master/src"
#workdir for copy of ORCA python files
varWORKDIR="/Users/thica/ORCA/work"
#workdir for copy of ORCA data files
varWORKDIRDATA="/Users/thica/ORCA/work2"
# Workdir to create final Zip
varWORKDIRZIP="/Users/thica/ORCA/workzip"

varDESTDIR="/Volumes/ctprivat/ORCA/Development/Orca"
varDESTWORK="/Users/thica/ORCA/work3"



# We create the spec file manual.
echo "# -*- mode: python -*-" > $spec
echo "from kivy.tools.packaging.pyinstaller_hooks import install_hooks"  >> $spec
echo "install_hooks(globals())" >> $spec
echo "a = Analysis(['${varWORKDIR}/main.py'],pathex=['${pyinstallerdir}'],hiddenimports=[])" >> $spec
echo "pyz = PYZ(a.pure)" >> $spec
echo "exe = EXE(pyz,a.scripts,exclude_binaries=1,name=os.path.join('build/pyi.darvin/ORCA','ORCA'),debug=False,strip=None,upx=True,console=True )" >> $spec
# echo "coll = COLLECT(exe, Tree('${varWORKDIR}'),a.binaries,[('datapackage.zip','${varWORKDIRZIP}/datapackage.zip', 'DATA')],a.zipfiles,a.datas,strip=None,upx=True,name='ORCA')" >> $spec
echo "coll = COLLECT(exe, Tree('${varWORKDIR}/'),a.binaries,a.zipfiles,a.datas,strip=None,upx=True,name=os.path.join('dist','ORCA'))" >> $spec

#Cleaning workdirs
mkdir "${varWORKDIR}"

echo "1" > "${varWORKDIR}"/stub.txt
rm -R "${varWORKDIR}"/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi
mkdir "${varWORKDIRDATA}"
echo "1" > "${varWORKDIRDATA}"/stub.txt
rm -R "${varWORKDIRDATA}"/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi

mkdir "${varWORKDIRZIP}"
echo "1" > "${varWORKDIRZIP}"/stub.txt
rm -R "${varWORKDIRZIP}"/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi

mkdir "${varDESTWORK}"
echo "1" > "${varDESTWORK}"/stub.txt
rm -R "${varDESTWORK}"/*
if [ "$?" -ne "0" ]; then
  echo "Cleaning folder failed"
  exit 1
fi

#copy python files
# read -p "Press [Enter] key to continue..."
cp -f "${varSOURCE}"/*.py "${varWORKDIR}"
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi


cp -f "${varSOURCE}"/*.txt "${varWORKDIR}"
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi

cp -f -r "${varSOURCE}"/* "${varWORKDIRDATA}"
if [ "$?" -ne "0" ]; then
  echo "Copy sources failed"
  exit 1
fi

rm "${varWORKDIRDATA}"/*.log
rm "${varWORKDIRDATA}"/*.pyc
rm "${varWORKDIRDATA}"/*.log
rm "${varWORKDIRDATA}"/*.ini

#delete all interface settings, with the exception of those, we mark as to be included
IFS=$(echo -en "\n\b")
for file in  $(find "${varWORKDIRDATA}" -name "config.ini") 
   do
      dir="${file%/*}"
      filename="${file##*/}"
      testfile="$dir/include.txt"
   
      if test -f $testfile;
      then
         echo Include: "$file"
      else
         rm $file
      fi
   done

# create the version file
echo ${varORCAVERSION} >  "${varWORKDIRDATA}"/dataversion_${varORCAVERSION}.txt



# Create Data Package
cd "${varWORKDIRDATA}"
zip -r -D -9  ${varWORKDIRZIP}/datapackage_${varORCAVERSION}.zip .
# copy packagezip into apk package folder
cp  ${varWORKDIRZIP}/datapackage_${varORCAVERSION}.zip ${varWORKDIR}


rm -R "${pyinstallerdir}/ORCA" 
pushd "${pyinstallerdir}"
mkdir ORCA


kivy "${pyinstallerdir}/pyinstaller.py" --name ORCA "${varWORKDIR}/main.py" --noconfirm
popd

cp "/Users/thica/ORCA/${spec}" "${pyinstallerdir}/ORCA"
# del $spec


pushd "${pyinstallerdir}"
kivy "${pyinstallerdir}/pyinstaller.py" "${pyinstallerdir}/ORCA/${spec}" --noconfirm
popd

pushd "${pyinstallerdir}/ORCA/dist"
mv ORCA ORCA.app
hdiutil create ./ORCA.dmg -srcfolder ORCA.app -ov
cp ORCA.dmg /Volumes/ctprivat/ORCA/Development/ORCA/Deployment/orca-${varORCABRANCH}-${varORCAVERSION}-macosx.dmg
popd


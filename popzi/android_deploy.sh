#!/bin/sh
set -e
rm -rf ~/pgs4a-0.9.4/popzi
cp -a ../popzi ~/pgs4a-0.9.4
cd ~/pgs4a-0.9.4
rm -rf ~/pgs4a-0.9.4/bin/Popzi-*-release-unsigned.apk
./android.py build popzi release
exit 0
jarsigner ~/pgs4a-0.9.4/bin/Popzi-*-release-unsigned.apk popzi
adb uninstall org.osgameseed.games.popzi
apk=$(ls ~/pgs4a-0.9.4/bin/Popzi-*-release-unsigned.apk)
signed_apk=$(echo $apk | sed "s/unsigned/signed/")
zipalign 4 $apk $signed_apk
echo "Filename file at $signed_apk"
adb install $signed_apk

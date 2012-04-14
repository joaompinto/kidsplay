#!/bin/sh
set -e
rm -rf ~/pgs4a-0.9.4/popzi
cp -a ../popzi ~/pgs4a-0.9.4
cd ~/pgs4a-0.9.4
rm -rf ~/pgs4a-0.9.4/bin/Popzi-*-release-unsigned.apk
./android.py build popzi release
#adb uninstall -k org.osgameseed.games.popzi
apk=$(ls ~/pgs4a-0.9.4/bin/Popzi-*-release.apk)
[ "$1" != "build" ] && adb install -r $apk

#!/bin/sh
set -e
rm -rf ~/pgs4a-0.9.4/mazenum
cp -a ../mazenum ~/pgs4a-0.9.4
cd ~/pgs4a-0.9.4
rm -rf ~/pgs4a-0.9.4/bin/Mazenum-*-release-unsigned.apk
./android.py build mazenum release

apk=$(ls ~/pgs4a-0.9.4/bin/Mazenum-*-release.apk)
[ "$1" != "build" ] && adb install -r $apk

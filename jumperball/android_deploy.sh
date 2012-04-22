#!/bin/sh
GN=jumperball
set -e
rm -rf ~/pgs4a-0.9.4/$GN
cp -a ../$GN ~/pgs4a-0.9.4
cd ~/pgs4a-0.9.4
rm -rf ~/pgs4a-0.9.4/bin/*.apk
./android.py build $GN release
apk=$(ls ~/pgs4a-0.9.4/bin/JumperBall-*-release.apk)
[ "$1" != "build" ] && adb install -r $apk

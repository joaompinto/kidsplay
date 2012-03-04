#!/bin/sh
set -e
rm -rf ~/pgs4a-0.9.4/popzi
cp -a ../popzi ~/pgs4a-0.9.4
cd ~/pgs4a-0.9.4
rm -rf ~/pgs4a-0.9.4/bin/Popzi-*-release-unsigned.apk
./android.py build popzi release
jarsigner ~/pgs4a-0.9.4/bin/Popzi-*-release-unsigned.apk popzi
adb uninstall com.example.popzi
adb install ~/pgs4a-0.9.4/bin/Popzi-*-release-unsigned.apk

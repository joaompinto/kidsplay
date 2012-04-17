#!/bin/sh
set -e
PGDIR=~/pgs4a-0.9.4
#PGDIR=~/pgs4a
rm -rf $PGDIR/mazenum
cp -a ../mazenum $PGDIR
cd $PGDIR
rm -rf $PGDIR/bin/Mazenum-*-release-unsigned.apk
./android.py build mazenum release

apk=$(ls $PGDIR/bin/Mazenum-*-release.apk)
[ "$1" != "build" ] && adb install -r $apk

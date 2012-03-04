#!/usr/bin/python
import sys
import os
from os.path import isdir, join
from glob import glob

if len(sys.argv) < 2:
	print "Usage: %s theme" % sys.argv[0]
	sys.exit(1)

theme = sys.argv[1]
theme_dir = join('gfx','themes', theme)
if not isdir(theme_dir):
	print "%s is not a directory" % theme_dir
	sys.exit(2)

images = glob(join(theme_dir, "piece-*.png"))
for img in images:
	if 'mini' in images:
		continue
	mini_name = img.replace('.png','') + '-mini.png'
	os.system('convert %s -resize 16x16  %s' % (img, mini_name))

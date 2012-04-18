#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@copyright:
    (C) Copyright 2012, Open Source Game Seed

@license:
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.    
"""
from distutils.core import setup
from mazenum.version import VERSION
from os.path import join
from glob import glob

setup(name="mazenum",
	version=VERSION,
	description="A simple group and pop objects game.",
	author="João Pinto",
	author_email="joao.pinto@osgameseed.org",
	url="http://www.osgameseed.org/games/mazenum",
	packages = ['mazenum'],
		package_dir = {'mazenum': 'mazenum'},
		scripts = ['bin/mazenum'],
		data_files = [
			('share/games/mazenum/', ['android-icon.png'] ),
			('share/games/mazenum/fonts', glob('fonts/*')),
			('share/games/mazenum/gfx/buttons', glob('gfx/buttons/*')),
			('share/games/mazenum/gfx', glob('gfx/*.jpg')),
			('share/applications', ['data/mazenum.desktop']),
			('share/pixmaps', ['data/mazenum-icon.png'])
		],
	)


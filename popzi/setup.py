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
from popzi.version import VERSION
from os.path import join
from glob import glob

themes = []
themes_dir = glob(join('gfx', 'themes', '*'))
for theme in themes_dir:
	themes.append((theme, glob(join(theme,'*'))))

print themes

setup(name="popzi",
	version=VERSION,
	description="A simple group and pop objects game.",
	author="João Pinto",
	author_email="joao.pinto@osgameseed.org",
	url="http://www.osgameseed.org/games/popzi",
	packages = ['popzi'],
		package_dir = {'popzi': 'popzi'},
		scripts = ['bin/popzi'],
		data_files = [
			(themes)
			('share/applications', ['data/popzi.desktop']),
			('share/pixmaps', ['data/popzi-icon.png'])
		],
	)

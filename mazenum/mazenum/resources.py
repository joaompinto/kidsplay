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
import sys
from os.path import join, abspath, exists
from os import getcwd

DATA_DIR = None
LAUNCH_DIR = getcwd()

def get_resource(resource_name):
	""" Check for resource files, first on local (source) dir, then on 
	other data dirs """
	
	search_dirs = [LAUNCH_DIR, DATA_DIR]
	for directory in search_dirs:		
		potential_path = join(directory, resource_name)
		if exists(potential_path):
			return potential_path

	raise Exception(potential_path+" not found")

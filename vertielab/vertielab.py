#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@copyright:
  (C) Copyright 2012, Open Source Game Seed <devs at osgameseed dot org>

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

import kivy
import os
kivy.require('1.0.5')

from kivy.config import Config
from kivy.lang import Builder

Builder.load_file('vertielab/vertielab.kv')

from vertielab.app import VertieLabApp

if __name__ in ('__android__', '__main__'):
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	Config.set('graphics', 'width', '800')
	Config.set('graphics', 'height', '600')	
	
	VertieLabApp().run()

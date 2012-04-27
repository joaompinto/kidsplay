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

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

class ToolBox(Widget):
	""" The tollbox widget provides a container for a group of buttons
	which can be used to select a tool . """
	static_selected = True
	selected_tool = ObjectProperty(None)	

	def __init__(self, **kwargs):
		super(ToolBox, self).__init__(**kwargs)
		self.register_event_type('on_tool_select')	
		self.register_event_type('on_static_toggle')
	
	def on_press_static(self, widget):		
		self.static_selected ^= True
		if self.static_selected:
			widget.background_normal = 'atlas://data/images/defaulttheme/button_pressed'
		else:
			widget.background_normal = 'atlas://data/images/defaulttheme/button'
		self.static_selected = self.static_selected
		self.dispatch('on_static_toggle', self.static_selected)

	def on_press_tool(self, widget):	
		if self.selected_tool:
			self.selected_tool.background_normal = 'atlas://data/images/defaulttheme/button'
		widget.background_normal = 'atlas://data/images/defaulttheme/button_pressed'
		self.dispatch('on_tool_select', widget.name)
	
	def on_tool_select(self, tool_name):
		pass
		
	def on_static_toggle(self, tool_name):
		pass		

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

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from vertielab.simulatorcanvas import SimulatorCanvas
from vertielab.toolbox import ToolBox


class VertieLabApp(App):

	toolbox = ObjectProperty(None)
	simulator_canvas = ObjectProperty(None)

	def on_tool_select(self, obj, value):
		self.simulator_canvas.tool_name = value

	def on_static_toggle(self, obj, value):
		self.simulator_canvas.static_tool = value

	def on_toolbox_action(self, obj, value):
		print value
		if value == "clear_all":
			self.simulator_canvas.clear_all()

	def build(self):
		root = BoxLayout(orientation='horizontal')
		#root.padding = 0
		self.toolbox = ToolBox()
		root.add_widget(self.toolbox)
		self.simulator_canvas = SimulatorCanvas()
		root.add_widget(self.simulator_canvas)
		self.toolbox.bind(on_tool_select=self.on_tool_select)
		self.toolbox.bind(on_static_toggle=self.on_static_toggle)
		self.toolbox.bind(on_action=self.on_toolbox_action)
		return root

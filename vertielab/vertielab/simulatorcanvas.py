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
from kivy.core.window import Window
from kivy.properties import ObjectProperty, DictProperty , NumericProperty, StringProperty, BooleanProperty
from kivy.graphics import Color, Ellipse, Line
from kivy.vector import Vector
from kivy.clock import Clock
from math import hypot
from vertie.geometry import Point
from vertie.shapes import CircleShape
from vertie.world import World

class SimulatorCanvas(Widget):
	
	tool_name = StringProperty("")
	static_tool = BooleanProperty(True)
	last_point_x = NumericProperty(0)
	last_point_y = NumericProperty(0)
	last_point = ObjectProperty(None)	
	current_line = ObjectProperty(None, allownone=True)
	
	world = ObjectProperty(None) # Simulation world
		
	simulator_shapes = DictProperty({})

	def __init__(self, **kwargs):
		super(SimulatorCanvas, self).__init__(**kwargs)
		Window.bind(mouse_pos=self.on_mouse_move)
		self.bind(tool_name=self.on_tool_change)
		self.world = World(self.width, self.height)
		self.world.gravity = Vector(0, -1)
		Clock.schedule_interval(self.simulation_step,1/60)	
		
	def on_tool_change(self, object, value):
		pass
			
	def simulation_step(self, dt):
		moving_shapes = self.world.step()
		for shape in moving_shapes:
			pieces = self.simulator_shapes[shape]
			if shape.pos.y < -100: #out of scene
				for piece in pieces:
					self.canvas.remove(piece)
				self.world.remove(shape)
				del self.simulator_shapes[shape]
				return
			if isinstance(shape, CircleShape):		
				print shape.pos
				pieces[0].pos = (shape.pos.x-shape.radius, shape.pos.y-shape.radius)
				pieces[1].pos = (shape.pos.x+1-shape.radius, shape.pos.y+1-shape.radius)
		
	def on_touch_down(self, touch):
		userdata = touch.ud
		if super(SimulatorCanvas, self).on_touch_down(touch):
			return True
		if not self.collide_point(touch.x, touch.y):
			return False
		with self.canvas:
			if self.tool_name == 'circle':
				Color(1, 1, 0)
				d = 5
				self.last_point = Vector(touch.x, touch.y)
				userdata['ellipse'] = Ellipse(pos=(touch.x - d/2, touch.y - d/2), size=(d, d))
				Color(255, 0, 0)
				d -= 2
				if d:
					userdata['ellipse_inner'] = Ellipse(pos=(self.last_point.x - d/2, self.last_point.y - d/2), size=(d, d))
			elif self.tool_name == 'polygon':	
				if self.current_line:			
					self.current_line.points += (touch.x, touch.y)	
				else:
					self.current_line = Line(points=(touch.x, touch.y))
	
	def on_touch_move(self, touch):	
		userdata = touch.ud
		with self.canvas:
			if 'ellipse' in userdata:
				d = hypot(touch.x - self.last_point.x, touch.y - self.last_point.y)
				if d > 0:
					# Recreate the cirle with new pos, new size
					Color(1, 1, 0)
					Color(255, 0, 0)
					#d = 100
					if d:
						userdata['ellipse'].pos = (self.last_point.x - d/2, self.last_point.y - d/2)
						userdata['ellipse'].size = (d, d)
						d -= 2
						if d:
							userdata['ellipse_inner'].pos = (self.last_point.x - d/2, self.last_point.y - d/2)
							userdata['ellipse_inner'].size = (d, d)						
					
			
	def on_mouse_move(self, window, pos):
		mouse_x, mouse_y = pos
		if self.current_line:
			if self.collide_point(mouse_x, mouse_y):
				if len(self.current_line.points) > 2:
					self.current_line.points = self.current_line.points[:-2]
				self.current_line.points += (mouse_x, mouse_y)			
			else:		
				self.canvas.remove(self.current_line)				
				self.current_line = None

	def on_touch_up(self, touch):	
		userdata = touch.ud
		if 'ellipse' in userdata:
			ellipse =  userdata['ellipse']
			radius = ellipse.size[0]/2
			x,y = ellipse.pos[0] + radius, ellipse.pos[1] + radius		
			simulation_shape = CircleShape(Point(x, y), ellipse.size[0]/2)
			self.world.add(simulation_shape, is_static=self.static_tool)
			graphical_shape = ([userdata['ellipse'], userdata['ellipse_inner']])
			self.simulator_shapes[simulation_shape]= graphical_shape			
			del userdata['ellipse']
			
	def update(self):
		pass

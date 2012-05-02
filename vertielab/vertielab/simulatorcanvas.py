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
import cymunk as cy
from math import hypot
from os.path import join, dirname
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import ObjectProperty, DictProperty \
	, NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.core.image import Image
from kivy.vector import Vector
from vertielab.linehelper import segment_nearest_point

class SimulatorCanvas(Widget):
	
	tool_name = StringProperty("")
	static_tool = BooleanProperty(True)
	circle_center = ObjectProperty(None)

	# Physical simulation objects
	cbounds = ListProperty([])
	shape_map = DictProperty({})
	cmap = DictProperty({})	# Circles map
	smap = DictProperty({})	# Static segment map
	body_list = ListProperty([])
	world = ObjectProperty(None) # Simulation world

	def __init__(self, **kwargs):
		super(SimulatorCanvas, self).__init__(**kwargs)
		#self._hue = 0
		self.init_physics()
		self.bind(size=self.update_bounds, pos=self.update_bounds)
		self.texture = Image(join(dirname(__file__), '..', 'data', 'circle.png'), mipmap=True).texture
		self.bind(tool_name=self.on_tool_change)
		Clock.schedule_interval(self.step,1/30)
		self.static_tool = False

	def init_physics(self):
		# create the space for physics simulation
		self.space = space = cy.Space()
		space.iterations = 50
		space.gravity = (0, -500)
		space.sleep_time_threshold = 0.5
		space.collision_slop = 0.5

		# create 4 segments that will act as a bounds
		for x in xrange(4):
			seg = cy.Segment(space.static_body,
					cy.Vec2d(0, 0), cy.Vec2d(0, 0), 10)
			seg.elasticity = 0.5
			seg.friction = 0.5
			self.cbounds.append(seg)
			space.add_static(seg)

		# update bounds with good positions
		self.update_bounds()

	def update_bounds(self, *largs):
		assert(len(self.cbounds) == 4)
		a, b, c, d = self.cbounds
		x0, y0 = self.pos
		x1 = self.right
		y1 = self.top

		self.space.remove_static(a)
		self.space.remove_static(b)
		self.space.remove_static(c)
		self.space.remove_static(d)
		# Add margin to match the static body radius
		x0 -= 10
		y0 -= 10
		x1 += 10
		y1 +=10
		a.a = (x0, y0)
		a.b = (x1, y0)
		b.a = (x1, y0)
		b.b = (x1, y1)
		c.a = (x1, y1)
		c.b = (x0, y1)
		d.a = (x0, y1)
		d.b = (x0, y0)
		self.space.add_static(a)
		self.space.add_static(b)
		self.space.add_static(c)
		self.space.add_static(d)

	def step(self, dt):
		self.space.step(1 / 30.)
		self.update_objects()

	def update_objects(self):
		for body, obj in self.cmap.iteritems():
			p = body.position
			radius, color, rect = obj
			rect.pos = p.x - radius, p.y - radius
			rect.size = radius * 2, radius * 2

	def add_circle(self, x, y, radius):
		# create a falling circle
		body = cy.Body(100, 1e9)
		body.position = x, y
		circle = cy.Circle(body, radius)
		circle.elasticity = 0.5
		#circle.friction = 0.5
		self.space.add(body, circle)

		with self.canvas:
			#self._hue = (self._hue + 0.01) % 1
			#color = Color(self._hue, 1, 1, mode='hsv')
			color = Color(88, 1, 1)
			rect = Rectangle(
				texture=self.texture,
				pos=(x - radius, y - radius),
				size=(radius * 2, radius * 2))
		self.cmap[body] = (radius, color, rect)
		self.shape_map[body] = circle

	def add_line(self, line):
		assert(len(line.points) == 4)
		points = line.points
		a = Vector(points[0], points[1])
		b = Vector(points[2], points[3])
		seg = cy.Segment(self.space.static_body,
			cy.Vec2d(a.x, a.y), cy.Vec2d(b.x, b.y), 0)
		seg.elasticity = 0.5
		self.space.add_static(seg)
		with self.canvas:
			line = Line(points=(a.x, a.y, b.x, b.y))
		self.smap[seg] = line

	def on_tool_change(self, object, value):
		pass

	def on_touch_down(self, touch):
		if super(SimulatorCanvas, self).on_touch_down(touch):
			return True
		if not self.collide_point(touch.x, touch.y):
			return False
		userdata = touch.ud
		if self.tool_name == 'circle':
			radius = 20
			with self.canvas:
				rect = Rectangle(
					texture = self.texture,
					pos=(touch.x - radius, touch.y - radius),
					size=(radius * 2, radius * 2))
			self.circle_center = Vector(touch.x, touch.y)
			userdata['circle'] = rect
		elif self.tool_name == 'polygon':
			with self.canvas:
				userdata['line'] = Line(points=(touch.x, touch.y))
		elif self.tool_name == 'remove':
			to_delete = None
			# Check if a circle was touched
			for body, obj in self.cmap.iteritems():
				p = body.position
				radius, color, rect = obj
				distance = hypot(touch.x-p.x, touch.y-p.y)
				if distance < radius:
					to_delete = body
					break
			if to_delete:
				self.space.remove(body)
				self.space.remove(self.shape_map[body])
				self.canvas.remove(rect)
				del self.cmap[body]
				del self.shape_map[body]
			else:
				# Check if a static segment was touched
				for segment, line in self.smap.iteritems():
					#print touch, segment.a, segment.b
					np = segment_nearest_point(touch, Vector(segment.a),
						Vector(segment.b))
					distance = hypot(touch.x - np.x, touch.y - np.y)
					if distance < 5:
						to_delete = segment
						break
				if to_delete:
					self.space.remove_static(segment)
					self.canvas.remove(line)
					del self.smap[segment]


	def on_touch_move(self, touch):	
		userdata = touch.ud
		with self.canvas:
			if 'circle' in userdata:
				radius = hypot(touch.x - self.circle_center.x,
					touch.y - self.circle_center.y)
				if radius < 20:
					radius = 20
				userdata['circle'].pos = (self.circle_center.x - radius,
					self.circle_center.y - radius)
				userdata['circle'].size = (radius*2, radius*2)
			if 'line' in userdata:
				line = userdata['line']
				if len(line.points) > 2:
					line.points = line.points[:2]
				line.points += (touch.x, touch.y)

	def on_touch_up(self, touch):
		userdata = touch.ud
		if 'line' in userdata:
			line = userdata['line']
			if len(line.points) > 2:
				self.add_line(line)
			self.canvas.remove(line)
			del userdata['line']
		elif 'circle' in userdata:
			circle =  userdata['circle']
			radius = circle.size[0]/2
			x,y = circle.pos[0] + radius, circle.pos[1] + radius
			self.add_circle(x, y, radius)
			self.canvas.remove(circle)
			del userdata['circle']

	def clear_all(self):
		for body, obj in self.cmap.iteritems():
			radius, color, rect = obj
			self.space.remove(body)
			self.space.remove(self.shape_map[body])
			self.canvas.remove(rect)
		self.cmap = {}
		self.shape_map = {}
		for segment, line in self.smap.iteritems():
			self.space.remove_static(segment)
			self.canvas.remove(line)
		self.smap = {}

import os
from os.path import exists
from interface.graphical import GraphichalEngine
from simulation.geometry import *
from simulation.shapes import *
from simulation.world import *

import pygame
from pygame.color import THECOLORS

try:
	import android	
	ANDROID = True
except ImportError:
	ANDROID = False
	
# Graphichal Engine
class JumperBall(GraphichalEngine):	
	lines_xml = 'lines.xml'
	def init(self):
		if not ANDROID:
			self.world.gravity = Vector(0, 0.2)
		self.drawing_line = Line(None, None)
		self.load_lines_from_xml()
		brokenball = CircleShape(Point(121, 147), 10)
		self.world.add(brokenball)		
		if ANDROID:
			start_ball = CircularBody(Point((100, 100)), 10)
			self.world.bodies.append(start_ball)
		
	def load_lines_from_xml(self):
		try:
			with open(self.lines_xml) as xml_file:
				lines = xml_file.read().splitlines()
		except IOError:
			return
		for line in lines:
			x1, y1, x2, y2 = line.split()
			l = Line(Point(int(x1), int(y1)), Point(int(x2), int(y2)))
			self.world.lines.append(l)
		
	def update(self):
		if ANDROID:
			x,y,z = android.accelerometer_reading()
			self.world.y_gravity = x/10
			self.world.x_gravity = y/10
		self.world.step()
			
	def draw(self):
		self.display.fill(THECOLORS['black'])
		for shape in self.world.circle_shapes:
			pygame.draw.circle(self.display, THECOLORS['red'], shape.center().pos(), shape.radius)
		#for line in self.world.lines:		
		#	pygame.draw.line(self.display, THECOLORS['yellow'], line.A.pos(), line.B.pos())
		if self.drawing_line.A and self.drawing_line.B:
			line = self.drawing_line
			pygame.draw.line(self.display, THECOLORS['green'], line.A.pos(), line.B.pos())

	def on_MOUSEBUTTONDOWN(self, mouse):
		to_delete = [shape for shape in self.world.circle_shapes if shape.hit(mouse.point)]
		if not to_delete and mouse.pressed[-1]:
			b = CircleShape(mouse.point, 10)
			self.world.add(b)
		elif mouse.pressed[0]:
			self.drawing_line.A = Point(mouse.x, mouse.y)
			self.drawing_line.B = None
		for shape in to_delete:
			self.world.remove(body)
				
	def on_MOUSEMOTION(self, mouse):
		if mouse.pressed[0] and self.drawing_line.A:
			self.drawing_line.B = Point(mouse.x, mouse.y)

	def on_MOUSEBUTTONUP(self, mouse):
		if self.drawing_line.A and self.drawing_line.B:
			self.world.lines.append(self.drawing_line)
			self.drawing_line = Line(None, None)
		elif not self.drawing_line.B and mouse.last_pressed[0]:
			to_delete = []
			for line in self.world.lines:				
				MouseCircle = CirculeShape(mouse.point, 3)
				contact_point = line.contact_point(MouseCircle)
				if contact_point:
					to_delete.append(line)
			for line in to_delete:
				self.world.lines.remove(line)	

	def on_KEY_s(self):
		new_fn = self.lines_xml+'.new'
		with open(new_fn, 'a') as lines_file:
			for line in self.world.lines:
				lines_file.write("%s %s %s %s\n" \
					% (line.A.x, line.A.y, line.B.x, line.B.y))
		if exists(self.lines_xml):
			os.unlink(self.lines_xml)
		os.rename(new_fn, self.lines_xml)

	def on_KEY_c(self):
		self.world.lines = []
		self.world.bodies = []

	def on_KEY_space(self):
		for body in self.world.bodies:
			body.py = body.y + 5

g = JumperBall()
g.init()
g.startLoop()

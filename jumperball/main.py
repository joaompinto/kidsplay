import os
from os.path import exists
from interface.graphical import GraphichalEngine
from simulation.dynamics import *


import pygame
from pygame.color import THECOLORS

try:
	import android	
	ANDROID = True
except ImportError:
	ANDROID = False
	
# Graphichal presentation
class JumperBall(GraphichalEngine):	
	lines_xml = 'lines.xml'
	def init(self):
		if not ANDROID:
			self.simulator.y_gravity = 0.2
		self.drawing_line = Line(None, None)
		self.load_lines_from_xml()
		if ANDROID:
			start_ball = CircularBody(Point(100, 100), 10)
			self.simulator.bodies.append(start_ball)
		
	def load_lines_from_xml(self):
		try:
			with open(self.lines_xml) as xml_file:
				lines = xml_file.read().splitlines()
		except IOError:
			return
		for line in lines:
			x1, y1, x2, y2 = line.split()
			l = Line(Point(int(x1), int(y1)), Point(int(x2), int(y2)))
			self.simulator.lines.append(l)
		
	def update(self):
		if ANDROID:
			x,y,z = android.accelerometer_reading()
			self.simulator.y_gravity = x/10
			self.simulator.x_gravity = y/10
		self.simulator.step()
			
	def draw(self):
		self.display.fill(THECOLORS['black'])
		for body in self.simulator.bodies:
			pygame.draw.circle(self.display, THECOLORS['red'], (int(body.x), int(body.y)), body.radius)
		for line in self.simulator.lines:		
			pygame.draw.line(self.display, THECOLORS['blue'], line.A.pos(), line.B.pos())
			for body in self.simulator.bodies:
				cp = line.contact_point(body)
				if cp:
					pygame.draw.circle(self.display, THECOLORS['white'], cp.pos(), 5, 1)
		if self.drawing_line.A and self.drawing_line.B:
			line = self.drawing_line
			pygame.draw.line(self.display, THECOLORS['green'], line.A.pos(), line.B.pos())

	def on_MOUSEBUTTONDOWN(self, mouse):
		to_delete = [body for body in self.simulator.bodies if body.hit(mouse.x, mouse.y)]
		if not to_delete and mouse.pressed[-1]:
			b = CircularBody(mouse.point, 10)
			self.simulator.bodies.append(b)
		elif mouse.pressed[0]:
			self.drawing_line.A = Point(mouse.x, mouse.y)
			self.drawing_line.B = None
		for body in to_delete:
			self.simulator.bodies.remove(body)
				
	def on_MOUSEMOTION(self, mouse):
		if mouse.pressed[0] and self.drawing_line.A:
			self.drawing_line.B = Point(mouse.x, mouse.y)

	def on_MOUSEBUTTONUP(self, mouse):
		if self.drawing_line.A and self.drawing_line.B:
			self.simulator.lines.append(self.drawing_line)
			self.drawing_line = Line(None, None)
		elif not self.drawing_line.B and mouse.last_pressed[0]:
			to_delete = []
			for line in self.simulator.lines:				
				MouseCircle = CircularBody(mouse.point, 3)
				contact_point = line.contact_point(MouseCircle)
				if contact_point:
					to_delete.append(line)
			for line in to_delete:
				self.simulator.lines.remove(line)	

	def on_KEY_s(self):
		new_fn = self.lines_xml+'.new'
		with open(new_fn, 'a') as lines_file:
			for line in self.simulator.lines:
				lines_file.write("%s %s %s %s\n" \
					% (line.A.x, line.A.y, line.B.x, line.B.y))
		if exists(self.lines_xml):
			os.unlink(self.lines_xml)
		os.rename(new_fn, self.lines_xml)

	def on_KEY_c(self):
		self.simulator.lines = []
		self.simulator.bodies = []

	def on_KEY_space(self):
		for body in self.simulator.bodies:
			body.py = body.y + 5

g = JumperBall()
g.init()
g.startLoop()

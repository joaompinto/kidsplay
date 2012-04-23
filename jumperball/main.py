from interface.graphical import GraphichalEngine
from simulation.dynamics import *
from math import hypot

import pygame
from pygame.color import THECOLORS

try:
	import android	
	ANDROID = True
except ImportError:
	ANDROID = False
	
# Graphichal presentation
class JumperBall(GraphichalEngine):	
	def init(self):
		self.simulator.y_gravity = 0.2
		top_line = Line(Point(100, 100), Point(500, 100))		
		left_line = Line(Point(100, 100), Point(100, 400))		
		right_line = Line(Point(500, 100), Point(500, 400))		
		bottom_line = Line(Point(100, 400), Point(500, 400))		
		bottom_line_d = Line(Point(100, 400), Point(500, 500))
		
		self.c = c = CircularBody(350, 280, 20)
		#self.simulator.lines = [] #[top_line, left_line, right_line, bottom_line_d]
		#self.simulator.bodies = [c]		
		self.drawing_line = Line(None, None)
		
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
		if not to_delete and mouse.pressed[0]:
			b = CircularBody(mouse.x, mouse.y, 20)
			self.simulator.bodies.append(b)
		elif mouse.pressed[-1]:
			self.drawing_line.A = Point(mouse.x, mouse.y)
			self.drawing_line.B = None
		for body in to_delete:
			self.simulator.bodies.remove(body)
				
	def on_MOUSEMOTION(self, mouse):
		if mouse.pressed[-1] and self.drawing_line.A:
			self.drawing_line.B = Point(mouse.x, mouse.y)

	def on_MOUSEBUTTONUP(self, mouse):
		if self.drawing_line.A and self.drawing_line.B:
			self.simulator.lines.append(self.drawing_line)
			self.drawing_line = Line(None, None)
                    
g = JumperBall()
g.init()
g.startLoop()

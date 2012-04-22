from interface.graphical import GraphichalEngine
from simulation.dynamics import CircularBody, Simulation
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

		self.simulator.y_gravity = 0.4
		
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

	def on_MOUSEBUTTONDOWN(self, mouse):
		hit = False
		for body in self.simulator.bodies:
			if body.hit(mouse.x, mouse.y):
				#body.px = mouse.x
				#body.py = mouse.y
				hit = True
				break
		if not hit:
			b = CircularBody(mouse.x, mouse.y, 40)
			self.simulator.bodies.append(b)
                    
g = JumperBall()
g.init()
g.startLoop()

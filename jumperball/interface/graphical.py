import os
import pygame
from math import sqrt
from pygame.color import THECOLORS
from random import randint, choice

from simulation.dynamics import Simulation

try:
	import android	
	import android.mixer as mixer
	ANDROID = True
except ImportError:
	ANDROID = None	
	import pygame.mixer as mixer
		
# Graphichal presentation
class GraphichalEngine:	
	def __init__(self):		
		self.loopFlag = True
				
		#Display
		if not ANDROID:
			os.environ['SDL_VIDEO_CENTERED'] = '1'		
		
		pygame.init()	
		if ANDROID:
			android.init()
			android.accelerometer_enable(True)
			android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
			
		width, height = 800, 480
		self.displaySize = width, height
		self.display = pygame.display.set_mode(self.displaySize)
		self.fps = 60		

		#Peripherals
		#self.keyboard = Keyboard()
		self.mouse = Mouse()
				
		# Simulation
		self.simulator = Simulation(width, height)

		#Other objects
		self.clock = pygame.time.Clock()		
				
	def beforeUpdate(self):
		self.events = pygame.event.get()
		for event in self.events:
			if event.type == pygame.QUIT:
				self.loopFlag = False
		
		#self.keyboard.update(self.events)
		self.mouse.update(self.events, self)        
		
	def afterUpdate(self):
		pygame.display.flip()
		self.clock.tick(self.fps) #Keep framerate stable

	def startLoop(self):
		while self.loopFlag:
			self.beforeUpdate()
			self.update()
			self.draw()
			self.afterUpdate()
			
	def update(self):
		pass
			
	def draw(self):
		pass

class Mouse:
	"""One more self-explicative singleton. Update each frame!
	"""
	def __init__(self):
		self.x = 0
		self.y = 0
		self.xPrev = 0
		self.yPrev = 0
		
		self.pressed = [0,0,0]
		self.pressedPrev = [0,0,0]
		self.pressedTime = 0
		
		self.wheel = 0
	
	def update(self, events, caller):
		#Remember the now old state
		self.xPrev, self.yPrev = self.x, self.y
		self.pressedPrev = self.pressed
		self.wheel = 0
		
		#Update state
		self.x, self.y = pygame.mouse.get_pos()
		self.pressed = pygame.mouse.get_pressed()
		
		#Remember for how many frames the mouse has been pressed
		if self.pressed[0] or self.pressed[2]:
			self.pressedTime += 1
		else:
			self.pressedTime = 0
		
		#Handle mouse wheel
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				caller.on_MOUSEBUTTONDOWN(self)

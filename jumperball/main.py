"""
This code was ported to Python from this greate article:
http://codeflow.org/entries/2010/nov/29/verlet-collision-with-impulse-preservation/
"""
import os
import pygame
from math import sqrt
from pygame.color import THECOLORS
from random import randint, choice

class Body:
	def __init__(self, x, y, radius, color):
		self.x, self.y, self.radius = x, y, radius
		self.color = color
		self.px, self.py = x, y
		self.ax = self.ay = 0

	def accelerate(self, delta):
		self.x += self.ax * delta * delta
		self.y += self.ay * delta * delta
		self.ax = self.ay = 0
		
	def inertia(self):
		x, y = self.x*2 - self.px, self.y*2 - self.py
		self.px, self.py = self.x, self.y;
		self.x, self.y = x, y
		
class Simulation:
	possible_colors = ['blue', 'red', 'green', 'yellow', 'magenta', 'cyan', 'purple', 'orange']
	def __init__(self, width, height):
		self.bodies = []
		self.width = width
		self.height = height
		self.damping = 0.98
		
		# Place non colliding balls as random positions
		while len(self.bodies) < 50:
			x = randint(25, width - 25)
			y = randint(25, height - 25)
			r = randint(5, height/15)
			c = THECOLORS[choice(self.possible_colors)]
			body = Body(x, y, r, c)
			collides = False
			for other in self.bodies:
				x, y = other.x - body.x, other.y - body.y
				length = sqrt(x*x+y*y);
				if length < other.radius + body.radius:
					collides = True
			if not collides:
				self.bodies.append(body)
				
	def collide(self, preserve_impulse):
		for i in range(len(self.bodies)):
			body1 = self.bodies[i]
			for j in range(i+1, len(self.bodies)):
				body2 = self.bodies[j]
				x, y = body1.x - body2.x, body1.y - body2.y
				slength = float(x*x+y*y);
				length = sqrt(slength)
				target = body1.radius + body2.radius;
				if length < target: # Colision detected				
					# Current velocity is needed to calculate impulse
					v1x = body1.x - body1.px
					v1y = body1.y - body1.py
					v2x = body2.x - body2.px
					v2y = body2.y - body2.py   
					 
					# Correction factor, to push bodies "away"                    
					factor = (length-target)/length;
					body1.x -= x*factor*0.5;
					body1.y -= y*factor*0.5;
					body2.x += x*factor*0.5;
					body2.y += y*factor*0.5;			
											
					if preserve_impulse:
						
						f1 = (self.damping*(x*v1x+y*v1y))/slength
						f2 = (self.damping*(x*v2x+y*v2y))/slength
						
						v1x += f2*x - f1*x
						v2x += f1*x - f2*x
						v1y += f2*y - f1*y
						v2y += f1*y - f2*y
					
						body1.px = body1.x - v1x
						body1.py = body1.y - v1y
						body2.px = body2.x - v2x
						body2.py = body2.y - v2y							

	def border_collide_preserve_impulse(self):
		width, height = self.width, self.height
		for body in self.bodies:
			radius, x, y = body.radius, body.x, body.y

			if x-radius < 0:
				vx = (body.px - body.x)*self.damping
				body.x = radius
				body.px = body.x - vx			
			elif x + radius > width:
				vx = (body.px - body.x)*self.damping
				body.x = width-radius
				body.px = body.x - vx
			
			if y-radius < 0:
				vy = (body.py - body.y)*self.damping
				body.y = radius
				body.py = body.y - vy
			elif y + radius > height:
				vy = (body.py - body.y)*self.damping;
				body.y = height-radius
				body.py = body.y - vy
				
	def border_collide(self):
		width, height = self.width, self.height
		for body in self.bodies:
			radius, x, y = body.radius, body.x, body.y
		if x-radius < 0:
			body.x = radius
		elif x + radius > width:
			body.x = width-radius

		if y-radius < 0:
			body.y = radius;		
		elif y + radius > height:
			body.y = height-radius

	def gravity(self):
		for body in self.bodies:
			body.ay += 0.5

	def inertia(self):
		for body in self.bodies:
			body.inertia()
			
	def accelerate(self, delta):
		for body in self.bodies:
			body.accelerate(delta)

	def step(self):
		steps = 2
		delta = 1.0/steps
		for i in range(steps):
			self.gravity();
			self.accelerate(delta);
			self.collide(False);
			self.border_collide();
			self.inertia();
			self.collide(True);
			self.border_collide_preserve_impulse();


# Graphichal presentation
class GraphichalEngine:	
	def __init__(self):		
		self.loopFlag = True
				
		#Display
		os.environ['SDL_VIDEO_CENTERED'] = '1'
		width, height = 800, 480
		self.displaySize = width, height
		self.display = pygame.display.set_mode(self.displaySize)
		self.fps = 30		

		#Peripherals
		#self.keyboard = Keyboard()
		#self.mouse = Mouse()
				
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
		#self.mouse.update(self.events)        
		
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
		self.simulator.step()
			
	def draw(self):
		self.display.fill(THECOLORS['black'])
		for body in self.simulator.bodies:
			pygame.draw.circle(self.display, body.color, (int(body.x), int(body.y)), body.radius)
			

g = GraphichalEngine()
g.startLoop()

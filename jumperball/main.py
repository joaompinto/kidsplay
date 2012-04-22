"""
This code was ported to Python from this greate article:
http://codeflow.org/entries/2010/nov/29/verlet-collision-with-impulse-preservation/
"""
import os
import pygame
from math import sqrt
from pygame.color import THECOLORS
from random import randint, choice

try:
	import android	
	import android.mixer as mixer
	ANDROID = True
except ImportError:
	ANDROID = None	
	import pygame.mixer as mixer
		
class Body:
	def __init__(self, x, y, radius, color):
		self.x, self.y, self.radius = x, y, radius
		self.color = color
		self.px, self.py = x, y
		self.ax = self.ay = 0

	def accelerate(self, delta):
		self.x += self.ax * delta * delta
		self.y += self.ay * delta * delta
		self.y += self.ay * delta * delta
		self.ax = self.ay = 0
		
	def inertia(self):
		x, y = self.x*2 - self.px, self.y*2 - self.py
		self.px, self.py = self.x, self.y;
		self.x, self.y = x, y
		
class Simulation:
	possible_colors = ['blue', 'red', 'green', 'yellow', 'magenta']
	def __init__(self, width, height):
		self.bodies = []
		self.width = width
		self.height = height
		self.damping = 0.98
		
		# Place non colliding balls as random positions
		b1 = Body(100, 100, 30, THECOLORS['red'])
		#self.bodies = [b1]
		#return 
		while len(self.bodies) < 2:
			x = randint(25, width - 25)
			y = randint(25, height - 25)
			#r = randint(5, height/15)
			r = 10
			c = THECOLORS[choice(self.possible_colors)]
			body = Body(x, y, r, c)
			body.friction = randint(0, 1)
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
				
					#if body1.color == body2.color:
					#	body1.radius /= 2
					#	body2.radius /= 2
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
			body.ay += self.y_gravity
			body.ax += self.x_gravity

	def friction(self):		
		friction = 0.05
		for body in self.bodies:						
			if body.friction == 0:
				continue
			x = (body.px - body.x)
			y = (body.py - body.y)
			slength = float(sqrt(x*x+y*y))		
			length = sqrt(slength)
			if x <> 0:				
				body.ax = (x/length)*friction
			if y <> 0:
				body.ay = (y/length)*friction		
		
	def inertia(self):
		for body in self.bodies:
			body.inertia()
			
	def accelerate(self, delta):
		for body in self.bodies:
			body.accelerate(delta)
			
	def destroy_small_balls(self):
		to_delete = []
		for body in self.bodies:
			if body.radius < 10:
				to_delete.append(body)
		for body in to_delete:
			self.bodies.remove(body)

	def step(self):
		steps = 2
		delta = 1.0/steps
		for i in range(steps):
			#self.friction()
			self.gravity()
			self.accelerate(delta)
			self.collide(False)
			self.border_collide()
			self.inertia()	
			self.collide(True)
			self.destroy_small_balls()
			self.border_collide_preserve_impulse();


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
		self.mouse.update(self.events, self.simulator)        
		
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
		if ANDROID:
			x,y,z = android.accelerometer_reading()
		else:
			x, y, z = 0, 0, 0
		print x, y, z
		self.simulator.y_gravity = x/10
		self.simulator.x_gravity = y/10
		self.simulator.step()
			
	def draw(self):
		self.display.fill(THECOLORS['black'])
		for body in self.simulator.bodies:
			pygame.draw.circle(self.display, body.color, (int(body.x), int(body.y)), body.radius)
			

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
	
	def update(self, events, simulator):
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
				for body in simulator.bodies:
					x = body.x - self.x
					y = body.y - self.y
					length = sqrt(x*x+y*y)
					if length <= body.radius:
						body.px = self.x
						body.py = self.y
					
                    
g = GraphichalEngine()
g.startLoop()

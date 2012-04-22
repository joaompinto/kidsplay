"""
The balls verlet colision code with impulse preservation was based on:
	http://codeflow.org/entries/2010/nov/29/verlet-collision-with-impulse-preservation/
	
"""
from math import sqrt, hypot, pi, sin, cos

class CircularBody:
	def __init__(self, x, y, radius):
		self.x, self.y, self.radius = x, y, radius
		self.px, self.py = x, y
		self.ax = self.ay = 0

	def hit(self, hit_x, hit_y):
		x = self.x - hit_x
		y = self.y - hit_y
		length = hypot(x, y)
		return length < self.radius
					
	def accelerate(self, delta):
		self.x += self.ax * delta * delta
		self.y += self.ay * delta * delta
		self.y += self.ay * delta * delta
		self.ax = self.ay = 0
		
	def inertia(self):
		x, y = self.x*2 - self.px, self.y*2 - self.py
		self.px, self.py = self.x, self.y;
		self.x, self.y = x, y
	
	def apply_friction(self, friction):
		x = (self.px - self.x)
		y = (self.py - self.y)
		length = hypot(x, y)
		if x <> 0:			
			self.ax += (x/length)*friction
			if abs(x) < 0.04: # stop on residual acceleration
				self.ax = 0
				self.px = self.x			
		if y <> 0:
			self.ay += (y/length)*friction
			if abs(y) < 0.04:  # stop on residual acceleration
				self.ay = 0
				self.py = self.y

			
		
class Simulation:
	def __init__(self, width, height):
		self.bodies = []
		self.width = width
		self.height = height
		self.damping = 0.98
		self.x_gravity = self.y_gravity = 0
		self.friction = 0
						
	def collide(self, preserve_impulse):
		""" Check all bodies for collisions """
		for i in range(len(self.bodies)):
			body1 = self.bodies[i]
			for j in range(i+1, len(self.bodies)):
				body2 = self.bodies[j]
				x, y = body1.x - body2.x, body1.y - body2.y
				slength = float(x*x+y*y);
				length = sqrt(slength)
				target = body1.radius + body2.radius
				if length < target: # Colision detected
				
					# record previous velocityy
					v1x = body1.x - body1.px
					v1y = body1.y - body1.py
					v2x = body2.x - body2.px
					v2y = body2.y - body2.py   
					 
					# resolve the body overlap conflict
					factor = (length-target)/length;
					body1.x -= x*factor*0.5;
					body1.y -= y*factor*0.5;
					body2.x += x*factor*0.5;
					body2.y += y*factor*0.5;			
											
					if preserve_impulse:
						# compute the projected component factors					
						f1 = (self.damping*(x*v1x+y*v1y))/slength
						f2 = (self.damping*(x*v2x+y*v2y))/slength
						
						# swap the projected components						
						v1x += f2*x - f1*x
						v2x += f1*x - f2*x
						v1y += f2*y - f1*y
						v2y += f1*y - f2*y
						
						# the previous position is adjusted
						# to represent the new velocity
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

	def apply_gravity(self):		
		for body in self.bodies:
			body.ay += self.y_gravity
			print body.ay
			body.ax += self.x_gravity

	def apply_friction(self):	
		for body in self.bodies:						
			body.apply_friction(self.friction)
		
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
			self.apply_friction()
			self.apply_gravity()		
			self.accelerate(delta)
			self.collide(False)
			self.border_collide()
			self.inertia()	
			self.collide(True)
			self.border_collide_preserve_impulse();
			

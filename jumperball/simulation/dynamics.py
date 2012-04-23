"""
The balls verlet colision code with impulse preservation was based on:
	http://codeflow.org/entries/2010/nov/29/verlet-collision-with-impulse-preservation/
	
"""
from math import sqrt, hypot, pi, sin, cos, atan2

class Point:
	def __init__(self, x, y):
		self.x, self.y = x, y
			
	def distance_to(self, other):
		return hypot(self.x-other.x, self.y-other.y)
		
	def pos(self):
		return (int(self.x), int(self.y))
		
	def nearest(self, *args):
		nearest_point = args[0]
		min_length = hypot(args[0].x - self.x, args[0].y - self.y)
		for arg in args[1:]:
			length = hypot(arg.x - self.x, arg.y - self.y)
			if length < min_length:
				nearest_point = arg
		return nearest_point
		
class CircularBody:
	def __init__(self, x, y, radius):
		self.x, self.y, self.radius = x, y, radius
		self.px, self.py = x, y
		self.ax = self.ay = 0

	def center(self):
		return Point(self.x, self.y)
		
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

			
class StaticRectangle:	
	def __init__(self, x, y, width, height):
		self.x, self.y = x ,y
		self.width, self.height = width, height
		


class Line:
	
	def __init__(self, A, B):
		self.A, self.B = A, B
		
	def __repr__(self):
		return "<Line> "+str(self.A.pos())+","+str(self.B.pos())
	
	def intersection_point(self, C):
		""" 
		Returns (point, in_segement)
			point - the point from the line which is closer to point C
			in_segement - True if the point is contained in the line seg
		Math from http://paulbourke.net/geometry/pointline/ 
		"""			
		A, B = self.A, self.B
		line_length = hypot(A.x - B.x, A.y - B.y)
		u = (((C.x - A.x ) * ( B.x - A.x )) +
			((C.y - A.y) * (B.y - A.y))) / ( line_length ** 2 )
		
		in_segement = not (u < 0 or u > 1)
		
		# Determine point of intersection
		intersection_x = A.x + u * ( B.x - A.x)
		intersection_y = A.y + u * ( B.y - A.y)
		return Point(intersection_x, intersection_y), in_segement
	
	def contact_point(self, C):
		""" Returns the contact point with a circle """
		p, in_segement = self.intersection_point(C.center())
		if not in_segement:
			p = C.center().nearest(self.A, self.B)
		distance = p.distance_to(C.center())
		if distance > C.radius:
			return None
		else:
			return p
	
class Simulation:
	def __init__(self, width, height):
		self.bodies = []
		self.rectangles = []
		self.lines = []
		self.width = width
		self.height = height
		#self.damping = 0.98
		self.damping = 0.90
		self.x_gravity = self.y_gravity = 0
		self.friction = 0
						
	def collide(self, preserve_impulse):
		""" Check all bodies for collisions """
		for i in range(len(self.bodies)):
			body1 = self.bodies[i]
			for j in range(i+1, len(self.bodies)):
				body2 = self.bodies[j]
				x, y = body1.x - body2.x, body1.y - body2.y
				slength = float(x*x+y*y)
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
						
	def colide_with_lines(self, preserve_impulse):
		for line in self.lines:				
			for body in self.bodies:								
				contact_point = line.contact_point(body)
				if contact_point is None:
					continue
				
				# record velocity
				v1x = (body.x - body.px) * self.damping
				v1y = (body.y - body.py) * self.damping
									
				x, y = body.x - contact_point.x, body.y - contact_point.y
				length = contact_point.distance_to(body.center())
				target = body.radius
				factor = (length-target)/float(length);
				body.x -= x*factor		
				body.y -= y*factor
				#print line, contact_point.y
				#print body.y, contact_point.y, 
				if preserve_impulse:									
					factor_y = body.radius*sin(atan2(y, x))
					factor_x = body.radius*cos(atan2(y, x))					
					if abs(contact_point.y -  body.y) <= body.radius:
					#if body.y in [contact_point.y + body.radius, contact_point.y - body.radius]:
							body.py = contact_point.y+factor_y+v1y
					#if abs(contact_point.x - body.x) <= body.radius:							
					if body.x in [contact_point.x + body.radius, contact_point.x - body.radius]:
						body.px = contact_point.x+factor_x+v1x
		
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
			self.colide_with_lines(True)
			self.collide(False)
			self.border_collide()			
			self.inertia()	
			self.collide(True)
			self.border_collide_preserve_impulse()
			
			
			

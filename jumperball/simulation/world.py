#!/usr/bin/python
# -*- coding: utf-8 -*-
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

@doc:
  This module provides classes for:
  
  Basic geometric elements:
	Point, Line

  Shapes:
    Circle, Triangle, Rectangle
  
  World
    The world is the simulation container. You must add shape objects 
    to the world. When adding a object the object is either static or
    dynamic. Static objects can not be moved and will not collide with other 
    static objects. Dynamic objects are fully simulated.
    
  Special elements:
	ContactPoint - A special point object which is internally used to 
	mark the collision between two shapes.
    

@credits:
  The balls verlet colision code with impulse preservation was based on:
  http://codeflow.org/entries/2010/nov/29/verlet-collision-with-impulse-preservation/
	
"""
from math import sqrt, hypot, pi, sin, cos, atan2
from simulation.geometry import *
from simulation.shapes import *

class World:
	def __init__(self, width, height):
		self.circle_shapes = []
		self.lines = []
		self.width = width
		self.height = height
		self.damping = 0.90
		self.gravity = Vector(0, 0)
		self.friction = 0
						
	def collide(self, preserve_impulse):
		""" Check all bodies for collisions """
		for i in range(len(self.circle_shapes)):
			shape1 = self.circle_shapes[i]
			for j in range(i+1, len(self.circle_shapes)):
				shape2 = self.circle_shapes[j]
				x, y = shape1.x - shape2.x, shape1.y - shape2.y
				slength = float(x*x+y*y)
				length = sqrt(slength)
				target = shape1.radius + shape2.radius
				if length < target: # Colision detected
				
					# record previous velocityy
					v1x = shape1.x - shape1.px
					v1y = shape1.y - shape1.py
					v2x = shape2.x - shape2.px
					v2y = shape2.y - shape2.py   
					 
					# resolve the shape overlap conflict
					factor = (length-target)/length;
					shape1.x -= x*factor*0.5;
					shape1.y -= y*factor*0.5;
					shape2.x += x*factor*0.5;
					shape2.y += y*factor*0.5;			
											
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
						shape1.px = shape1.x - v1x
						shape1.py = shape1.y - v1y
						shape2.px = shape2.x - v2x
						shape2.py = shape2.y - v2y
						
	def colide_with_lines(self, preserve_impulse):
		for line in self.lines:				
			for shape in self.circle_shapes:								
				contact_point = line.contact_point(shape)
				if contact_point is None:
					continue
				
				# record velocity
				v1x = (shape.x - shape.px) * self.damping
				v1y = (shape.y - shape.py) * self.damping
									
				x, y = shape.x - contact_point.x, shape.y - contact_point.y
				length = contact_point.distance_to(shape.center())
				target = shape.radius
				factor = (length-target)/float(length);
				shape.x -= x*factor		
				shape.y -= y*factor
				
				if preserve_impulse:		
					factor_y = shape.radius*sin(atan2(int(y), int(x)))
					factor_x = shape.radius*cos(atan2(int(y), int(x)))						
					if abs(contact_point.y -  shape.y) <= shape.radius:
						shape.py = contact_point.y+factor_y+v1y	
					#if shape.x in [contact_point.x + shape.radius, contact_point.x - shape.radius]:
					#if abs(contact_point.x -  shape.x) <= shape.radius:
					#	#print factor_x
					#	print shape.x, contact_point.x-factor_x
					#	#shape.px = contact_point.x-x
		
	def border_collide_preserve_impulse(self):
		width, height = self.width, self.height
		for shape in self.circle_shapes:
			radius, x, y = shape.radius, shape.x, shape.y

			if x-radius < 0:
				vx = (shape.px - shape.x)*self.damping
				shape.x = radius
				shape.px = shape.x - vx			
			elif x + radius > width:
				vx = (shape.px - shape.x)*self.damping
				shape.x = width-radius
				shape.px = shape.x - vx
			
			if y-radius < 0:
				vy = (shape.py - shape.y)*self.damping
				shape.y = radius
				shape.py = shape.y - vy
			elif y + radius > height:
				vy = (shape.py - shape.y)*self.damping;
				shape.y = height-radius
				shape.py = shape.y - vy
				
	def border_collide(self):
		width, height = self.width, self.height
		for shape in self.circle_shapes:
			radius, x, y = shape.radius, shape.x, shape.y
			if x-radius < 0:
				shape.x = radius
			elif x + radius > width:
				shape.x = width-radius

			if y-radius < 0:
				shape.y = radius;		
			elif y + radius > height:
				shape.y = height-radius

	def apply_gravity(self):		
		for shape in self.circle_shapes:
			shape.ay += self.gravity.y
			shape.ax += self.gravity.x

	def apply_friction(self):	
		for shape in self.circle_shapes:						
			shape.apply_friction(self.friction)
		
	def inertia(self):
		for shape in self.circle_shapes:
			shape.inertia()
			
	def accelerate(self, delta):
		for shape in self.circle_shapes:
			shape.accelerate(delta)			

	def step(self):
		steps = 2
		delta = 1.0/steps
		for i in range(steps):
			if self.friction:			
				self.apply_friction()
			self.apply_gravity()		
			self.accelerate(delta)
			self.colide_with_lines(True)
			self.collide(False)
			self.border_collide()			
			self.inertia()	
			self.collide(True)
			self.border_collide_preserve_impulse()
			
	def shape_list(self, shape):
		if isinstance(shape, CircleShape):
			return self.circle_shapes
			
	def add(self, shape):
		""" Add a shape to the world """
		shape_list = self.shape_list(shape)
		shape_list.append(shape)
			
	def remove(self, shape):
		shape_list = self.shape_list(shape)
		shape_list.remove(shape)
			
			

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
  This module handles collisions
  
"""
from vertie.geometry import Point, Vector, Line
from vertie.shapes import CircleShape

class Contact:
	
	def __init__(self, shape1, shape2, solve_function):
		self.shape1, self.shape2 = shape1, shape2
		self.solve_function = solve_function

class CollisionSolver:
	def __init__(self):
		self.contacts = []
		self.preserve_impulse = False
		
	def resolve(self):
		""" Call contact points resolution functions """
		for contact in self.contacts:
			contact.solve_function(contact.shape1, contact.shape2)
		
	def create_contacts_list(self, shapes):
		""" Identifies contact points """
		contact_list = self.contacts = []
		for i in range(len(shapes)):
			shape1 = shapes[i]
			for j in range(i+1, len(shapes)):	
				shape2 = shapes[j]
				contacts = self.contacts_between(shape1, shape2)
				contact_list.extend(contacts)
				
	def contacts_between(self, shape1, shape2):
		""" Return list of contact points between shapes """
		# Contacts between circles
		if isinstance(shape1, CircleShape) and isinstance(shape2, CircleShape):				
			current_distance = shape1.pos - shape2.pos
			target_distance = Vector(shape1.radius + shape2.radius, 0)
			#print "current_distance = %d, target_distance=%d" % (current_distance, target_distance)
			if current_distance < target_distance: # Colision detected				
				return [Contact(shape1, shape2, self.resolve_circle2circle)]
		return []
	

	def resolve_staticcircle2circle(self, static_shape, moving_shape):		 
		distance = static_shape.pos - moving_shape.pos
		target = static_shape.radius + moving_shape.radius
		length = (distance).length
		if length == 0:
			factor = 1
		else:
			factor = (length-target)/length
		adjust_v = Vector(distance.x*factor, distance.y*factor)
		moving_shape.pos += adjust_v
		
	def resolve_circle2circle(self, shape1, shape2):
		static_shape = None
		if shape1.is_static:	
			return self.resolve_staticcircle2circle(shape1, shape2)
		elif shape2.is_static:
			return self.resolve_staticcircle2circle(shape2, shape1)
			
		distance = shape1.pos - shape2.pos
		if self.preserve_impulse:
			velocity1 = shape1.pos - shape1.prev_pos
			velocity2 = shape2.pos - shape2.prev_pos
				
		# resolve the shape overlap conflict
		target = shape1.radius + shape2.radius
		length = (distance).length
		factor = (length-target)/length
		adjust_v = Vector(distance.x*factor*0.5, distance.y*factor*0.5)
		shape1.pos -= adjust_v.pos
		shape2.pos += adjust_v.pos

		if self.preserve_impulse:
			# 
			slength = length**2
			# compute the projected component factors
			# distance*velocity = |distance||velocity|.cos(θ)				
			f1 = (self.damping*(distance * velocity1))/slength
			f2 = (self.damping*(distance * velocity2))/slength
			
			# swap the projected components	
			velocity1.x += f2*distance.x - f1*distance.x
			velocity2.x += f1*distance.x - f2*distance.x
			velocity1.y += f2*distance.y - f1*distance.y
			velocity2.y += f1*distance.y - f2*distance.y
			
			# the previous position is adjusted
			# to represent the new velocity
			shape1.prev_pos = shape1.pos - velocity1
			shape2.prev_pos = shape2.pos - velocity2

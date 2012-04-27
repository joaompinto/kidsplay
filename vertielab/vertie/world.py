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
from vertie.geometry import Point, Vector, Line
from vertie.shapes import CircleShape
from vertie.collisions import CollisionSolver

class World:
	def __init__(self, width, height):
		self.shapes = []
		self.lines = []
		self.width = width
		self.height = height
		self.damping = 0.90
		self.gravity = Vector(0, 0)
		self.friction = 0		
		self.collision_solver = CollisionSolver()		
	
	def apply_gravity(self):		
		for shape in self.shapes:
			shape.ay += self.gravity.y
			shape.ax += self.gravity.x

	def apply_friction(self):	
		""" Thise friction is used only on top-down representations.
			The friction is applied to all movements.
		"""
		for shape in self.shapes:						
			if not shape.is_static:
				shape.apply_friction(self.friction)
		
	def inertia(self):		
		for shape in self.shapes:
			if not shape.is_static:
				shape.inertia()
			
	def accelerate(self, delta):
		for shape in self.shapes:
			if not shape.is_static:
				shape.accelerate(delta)			

	def step(self):
		#if len(self.collision_solver.contacts) > 0:
		#	return []
		steps = 2
		delta = 1.0/steps
		collision_solver = self.collision_solver
		start_pos_dict = dict()
		for shape in self.shapes:
			start_pos_dict[shape] = shape.pos
		for i in range(steps):
			self.apply_friction()
			self.apply_gravity()	
			# Adjust current position based on accumulated acceleration
			self.accelerate(delta)			
			collision_solver.create_contacts_list(self.shapes)
			collision_solver.resolve()
			#self.colide_with_lines(True)
			#self.collide(False)
			#self.border_collide()			
			self.inertia()	
			#self.collide(True)
			#self.border_collide_preserve_impulse()
		# Return all shapes which moved
		moving_shapes = []
		for shape in self.shapes:
			start_pos = start_pos_dict[shape]
			if start_pos.x <> shape.pos.x or start_pos.y <> shape.pos.y:
				moving_shapes.append(shape)
		return moving_shapes				

	def add(self, shape, is_static=False):
		""" Add a shape to the world """
		shape.is_static = is_static
		self.shapes.append(shape)
			
	def remove(self, shape):
		self.shapes.remove(shape)
			
			

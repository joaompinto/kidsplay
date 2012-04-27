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
	Point, Vector, Line
"""
from math import sqrt, hypot, pi, sin, cos, atan2

class Point:

	def __init__(self, x, y):
		self.x, self.y = x, y
		
	def __repr__(self):
		return 'Point at' + str((self.x, self.y))
			
	@property	
	def intpos(self):
		""" return position as tuple, useful for some gfx libs """
		return (int(self.x), int(self.y))
		
	def pos_get(self):
		return Point(self.x, self.y)
		
	def pos_set(self, x, y):
		self.x, self.y = x,y
	pos = property(pos_get, pos_set)		
		
	def nearest(self, *args):
		""" Returns the nearest point from a list of points """
		nearest_point = args[0]
		min_length = (args[0] - self).length
		for arg in args[1:]:
			length = (arg - self).length
			if length < min_length:
				nearest_point = arg
		return nearest_point
	
	def __add__(self, other):
		return Point(self.x + other.x, self.y + other .y)

	def __sub__(self, other):
		return Point(self.x - other.x, self.y - other .y)
		
	def __mul__(self, other):
		return self.x * other.x + self.y * other .y

	@property
	def length(self):
		return hypot(self.x, self.y)
		
		
class Vector(Point):
	""" 2D Vector """
	@property
	def length(self):		
		return hypot(self.x, self.y)

	def __cmp__(self, other):
		""" Compare vectors  lengths
		Use square lengths compares instead real length to avoid sqrt()
		"""
		self_length  = self.x**2+self.y**2
		other_length = other.x**2+other.y**2
		return self_length - other_length
	

class Line:
	""" Line segement between point A and B """
	def __init__(self, A,  B):
		self.A, self.B = A, B
			
	def __repr__(self):
		return "<Line> "+str(self.A.pos())+","+str(self.V.pos())
	
	def intersection_point(self, C):
		""" 
		Returns (point, in_segement)
			point - the point from the line which is closer to point C
			in_segement - True if the point is contained in the line seg
		Math from http://paulbourke.net/geometry/pointline/ 
		"""			
		A,B = self.A, self.B
		line_length = self.V.length()		
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
			# if the point is not in the line segment the contact can 
			# only happen at the nearest line end
			p = C.center().nearest(self.A, self.B)
		if p - C.center() > Vector(C.radius, 0):
			return None
		else:
			return p

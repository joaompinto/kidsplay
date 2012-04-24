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
			
	def distance_to(self, other):
		return hypot(self.x-other.x, self.y-other.y)
		
	def pos(self):
		""" return position as tuple, useful for some gfx libs """
		return (int(self.x), int(self.y))
		
	def nearest(self, *args):
		""" """
		nearest_point = args[0]
		min_length = hypot(args[0].x - self.x, args[0].y - self.y)
		for arg in args[1:]:
			length = hypot(arg.x - self.x, arg.y - self.y)
			if length < min_length:
				nearest_point = arg
		return nearest_point

class Vector(Point):
	""" For simplicy we assume vectors have origin (0,0) to (PointX, PointY)"""
	pass

class Line:
	""" Line between point A and B """
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

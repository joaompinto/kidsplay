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
  This is an helper class to identify distance between points and lines
"""
from kivy.vector import Vector
from math import hypot


def point_nearest_point(A, *args):
    """ Search args and returns the nearest point to A """
    nearest_point = args[0]
    min_length = hypot(args[0].x - A.x, args[0].y - A.y)
    for arg in args[1:]:
        length = hypot(arg.x - A.x, arg.y - A.y)
        if length < min_length:
            nearest_point = arg
    return nearest_point  

def segment_nearest_point(C, A, B):
    """ 
    Returns Vector corresponding to the closer point from segment AB 
    to point C
    """			
    line_length = hypot(A.x - B.x, A.y - B.y)
    u = (((C.x - A.x ) * ( B.x - A.x )) +
        ((C.y - A.y) * (B.y - A.y))) / ( line_length ** 2 )

    in_segment = not (u < 0 or u > 1)

    # Determine point of intersection
    if in_segment:
        intersection_x = A.x + u * ( B.x - A.x)
        intersection_y = A.y + u * ( B.y - A.y)
        nearest_point = Vector(intersection_x, intersection_y)
    else:
        nearest_point = point_nearest_point(C, A, B)

    return nearest_point

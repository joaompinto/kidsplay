#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@copyright:
    (C) Copyright 2012, Open Source Game Seed

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
"""

from random import randint
import pygame
from resources import get_resource
from pygame.color import THECOLORS
from pygame.gfxdraw import box, rectangle, filled_circle
from os.path import join

POPPING_INTERVAL = 33
POPPING_EVENT = pygame.USEREVENT + 3

class PlayBoard:
	""" The playboard is a two dimensional data store for the game date 
	it also provides some helper methods for the game logic """
	def __init__(self, screen, columns, rows, header_height=None):		
		self.rows = rows
		self.columns = columns		
		# Create two dimentional array using list comprehension
		# This array stores data for the static pieces on the game board
		self._board = [x[:] for x in [[0]*rows]*columns]
		# List of (animated) falling pieces 
		# Items on the list = (column, ypos, bubble_id)
		self.falling_pieces = []	
		# Max random id that can be assigned to a board piece
		self.max_rand_id = 5
		self.header_height = header_height
		
		self.screen = screen
		width, height = screen.get_width(), screen.get_height()
		
		# Dimension for the pieces		
		horizontal_size = width / self.columns
		vertical_size = (height-self.header_height) / self.rows
		self.piece_w = self.piece_h = vertical_size if vertical_size < horizontal_size else horizontal_size
		self.h_border = (width-(self.piece_w*self.columns))/2
		if self.h_border < 0: 
			self.h_border = 0
		self.surfaces  = []
		self.mini_surfaces  = []
		self.width = self.piece_w * self.columns
		self.height = self.piece_h * self.rows
		self.my_surface = pygame.Surface((self.width, self.height))
		self.tmp_surface = pygame.Surface((self.width, self.height))
		self.needs_static_redraw = True		
		
		self.font = pygame.font.Font(get_resource(join("fonts", "FreeSans.ttf")), 25)						
		
	def start(self):
		for c in range(self.columns):
			for r in range(self.rows):
				i = randint(1, 9)
				self.set_piece(c, r, i)
		pass
			
	def set_piece(self, x, y, piece_id):
		self._board[x][y] = piece_id
		self.needs_static_redraw = True
		
	def get_piece(self, x, y):
		return self._board[x][y]	
			
	def check_event(self, event):		
		pass
			
	def get_board_pos(self, (x, y)):
		board_x = (x-self.h_border)/self.piece_w
		board_y = (y-self.header_height)/self.piece_h	
		return board_x, board_y

	def set_background(self, surface):
		x, y = self.h_border, self.header_height
		w, h = self.width, self.height
		self.background = surface.subsurface(x, y, w, h).copy()
		
	def draw(self, screen):			
		my_surface, tmp_surface = self.my_surface, self.tmp_surface
		if self.needs_static_redraw:
			self.my_surface = my_surface = self.background.copy()
			# Draw static pieces
			for c in range(self.columns):
				for r in range(self.rows):
					piece_id = self.get_piece(c, r)
					if piece_id != 0:									
						pos = (c*self.piece_w, r*self.piece_h)
						rectangle(my_surface, pos+(self.piece_w, self.piece_h), 
							THECOLORS["white"] )
						text = self.font.render(str(piece_id), True, THECOLORS["white"])	
						xpos = (c*self.piece_w) + (self.piece_w/2) - (text.get_width()/2)
						ypos = (r*self.piece_h) + (self.piece_h/2) - (text.get_height()/2)
						my_surface.blit(text, (xpos, ypos))
			self.needs_static_redraw = False
		tmp_surface.blit(my_surface, (0,0))
		
		
		screen.blit(tmp_surface, (self.h_border, self.header_height))
			
		


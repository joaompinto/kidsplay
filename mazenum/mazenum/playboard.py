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

PLAYED_COLOR = (100, 100, 100)
PLAYED_BACKGROUND_COLOR = (0, 0, 100)

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
		
	def start(self, level):
		for c in range(self.columns):
			for r in range(self.rows):
				i = randint(1, 9)
				self.set_piece((c, r), i)
		start_x = randint(0, self.columns-1)
		start_y = randint(0, self.rows-1)		
		self.set_piece((start_x, start_y), 1)
		self._play_path = [(start_x, start_y)]
		self.goals = []
		self.make_sequence(7+level)
			
	def set_piece(self, (x, y), piece_id):
		self._board[x][y] = piece_id
		self.needs_static_redraw = True
		
	def get_piece(self, x, y):
		return self._board[x][y]	
			
	def make_sequence(self, start_count):
		""" Set a sequence in a random order with "count" pieces """		
		start_path = True
		count = start_count
		while count > 0:
			if start_path:
				count = start_count # need on deadlock restart
				placed = [self._play_path[0]]
				x, y = self._play_path[0]
				i = 2			
				start_path = False
				dead_lock = False
			out_of_bounds = True
			find_way_count = 0
			while out_of_bounds:
				find_way_count += 1
				move_x = randint(-1, 1)
				move_y = randint(-1, 1)
				new_pos = (x + move_x, y + move_y)
				out_of_bounds = x + move_x < 0 or \
					y + move_y < 0 or \
					x + move_x > self.columns-1 or \
					y + move_y > self.rows-1 or \
					new_pos in placed
				if find_way_count > 50: # Avoid deadlock
					dead_lock = True
					start_path = True					
					break
			if dead_lock:
				continue
			placed.append(new_pos)
			x,y = new_pos
			self.set_piece(new_pos, i)
			i += 1
			if i == 10:
				i=1
			count -= 1	
		self.goals.append(placed[-1])			
		
	def check_event(self, event):		
		pass
			
	def get_board_pos(self, (x, y)):
		board_x = (x-self.h_border)/self.piece_w
		board_y = (y-self.header_height)/self.piece_h	
		return board_x, board_y

	def place_at(self, pos):
		self._play_path.append(pos)
		self.needs_static_redraw = True
		
	def get_last_pos(self):
		return self._play_path[-1]
		
	def remove_last(self):
		self._play_path.pop()
		self.needs_static_redraw = True
		
	def set_background(self, surface):
		x, y = self.h_border, self.header_height
		w, h = self.width, self.height
		self.background = surface.subsurface(x, y, w, h).copy()
		
	def draw(self, screen):			
		my_surface, tmp_surface = self.my_surface, self.tmp_surface
		if self.needs_static_redraw:
			self.my_surface = my_surface = self.background.copy()
			
			# Draw the current piece background
			(c, r) = self.get_last_pos()
			pos = (c*self.piece_w, r*self.piece_h)
			box(my_surface, pos+(self.piece_w, self.piece_h), THECOLORS["blue"])
			
			# Draw the complete board
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
						
			# Turn those on play path gray
			for i in range(len(self._play_path)-1):
				c, r = self._play_path[i]
				piece_id = self.get_piece(c, r)
				pos = (c*self.piece_w+1, r*self.piece_h+1)
				box(my_surface, pos+(self.piece_w-1, self.piece_h-1), 
					PLAYED_BACKGROUND_COLOR )				
				text = self.font.render(str(piece_id), True, PLAYED_COLOR)	
				xpos = (c*self.piece_w) + (self.piece_w/2) - (text.get_width()/2)
				ypos = (r*self.piece_h) + (self.piece_h/2) - (text.get_height()/2)				
				my_surface.blit(text, (xpos, ypos))				

			# Paint goals
			for c, r in self.goals:
				piece_id = self.get_piece(c, r)
				pos = (c*self.piece_w+1, r*self.piece_h+1)
				box(my_surface, pos+(self.piece_w-1, self.piece_h-1), 
					THECOLORS["black"] )				
				text = self.font.render(str(piece_id), True, THECOLORS["green"])	
				xpos = (c*self.piece_w) + (self.piece_w/2) - (text.get_width()/2)
				ypos = (r*self.piece_h) + (self.piece_h/2) - (text.get_height()/2)				
				my_surface.blit(text, (xpos, ypos))				
								
			
			self.needs_static_redraw = False
		tmp_surface.blit(my_surface, (0,0))
		
		
		screen.blit(tmp_surface, (self.h_border, self.header_height))
			
		


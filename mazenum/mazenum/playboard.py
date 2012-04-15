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

from random import randint, choice
import pygame
from resources import get_resource
from pygame.color import THECOLORS
from pygame.gfxdraw import box, rectangle, filled_circle
from os.path import join

POPPING_INTERVAL = 33
POPPING_EVENT = pygame.USEREVENT + 3

PLAYED_COLOR = (0, 0, 0)
PLAYED_BACKGROUND_COLOR = THECOLORS['white']

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
		self._play_path = []
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
		
		"""
		for c in range(self.columns):
			for r in range(self.rows):
				i = randint(1, 9)
				self.set_piece((c, r), i)
		"""
		self.goals = []
		self.touched_goals = []
		self.clear()
		# First place the "Solution" path
		self.start_pos = start_pos = self.place_sequence(8+level, (level/2)+1)
		self._play_path =  [start_pos]
		self.place_sequence(9, False)
		# Now place 10 random paths
		while self._free_list():
			self.place_sequence(9, 0)		
			
	def set_piece(self, (x, y), piece_id):
		self._board[x][y] = piece_id
		self.needs_static_redraw = True
		
	def get_piece(self, (x, y)):
		return self._board[x][y]	
			
			
	def is_in_bounds(self, position):
		""" check if a given position is inside the playtable """
		c, r = position
		return not(c < 0 or r < 0 or c >= self.columns or r >= self.rows)
		
	def _free_list(self):
		# Build list of free positions for the random start pos
		free_list = []
		for c in range(self.columns):
			for r in range(self.rows):
				piece_id = self.get_piece((c, r))				
				if not piece_id:
					free_list.append((c, r))
					
		return free_list
				
	def clear(self):
		for c in range(self.columns):
			for r in range(self.rows):
				piece_id = self.set_piece((c, r), 0)						
				
	def place_sequence(self, count, goal_count):
		""" Create a sequence of "count" consecutive numbers in 
		a random direction """				
		if count > (self.rows*self.columns):
			count = (self.rows*self.columns)
		must_start_path = True
		start_count = count
		while count > 0:
			# We need init data structures inside the loop because
			# we may need to re-init when a deadlock is found
			if must_start_path:
				start_pos = choice(self._free_list())
				total_placed = 0
				count = start_count -1 # need on deadlock restart								
				placed = {}
				placed[start_pos] = 1
				current_nr = 2
				x, y = start_pos				
				must_start_path = False
			possible_pos = [] # list of possible positions for next piece
			for delta_c in range(-1, 2):
				for delta_r in range(-1, 2):
					pos = (x + delta_c, y + delta_r)
					if pos not in placed \
						and self.is_in_bounds(pos) \
						and self.get_piece(pos) == 0:
							possible_pos.append(pos)
			if len(possible_pos) == 0: # Deadlock
				if goal_count:
					must_start_path = True				
				else:
					break
			else:
				new_pos = choice(possible_pos)
				placed[new_pos] = current_nr
				x,y = new_pos				
				current_nr += 1
				if current_nr == 10:
					current_nr = 1 
				count -= 1	
				total_placed += 1
				
		for key, value in placed.iteritems():
			self.set_piece(key, value)
					
		if goal_count:
			self.goals.append(new_pos)			
			for i in range(goal_count-1):
				random_goal = choice(placed.keys())				
				while random_goal in self.goals or \
					random_goal==start_pos: # Never place on the first
					random_goal = choice(placed.keys())
				self.goals.append(random_goal)
		return start_pos
		
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
		if not self._play_path:
			return None
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
			if self.get_last_pos():
				(c, r) = self.get_last_pos()
				pos = (c*self.piece_w, r*self.piece_h)
				box(my_surface, pos+(self.piece_w, self.piece_h), THECOLORS["blue"])
			
			# Draw the complete board
			for c in range(self.columns):
				for r in range(self.rows):
					piece_id = self.get_piece((c, r))
					if piece_id != 0:									
						pos = (c*self.piece_w, r*self.piece_h)
						rectangle(my_surface, pos+(self.piece_w, self.piece_h), 
							THECOLORS["white"] )
						if (c, r) in self._play_path[:-1]:
							continue
						text_color =  THECOLORS["white"]
						text = self.font.render(str(piece_id), True, text_color)	
						xpos = (c*self.piece_w) + (self.piece_w/2) - (text.get_width()/2)
						ypos = (r*self.piece_h) + (self.piece_h/2) - (text.get_height()/2)
						my_surface.blit(text, (xpos, ypos))
						
			# Turn those on play path gray
			for i in range(len(self._play_path)-1):
				c, r = self._play_path[i]
				piece_id = self.get_piece(self._play_path[i])
				pos = (c*self.piece_w+1, r*self.piece_h+1)
				box(my_surface, pos+(self.piece_w-1, self.piece_h-1), 
					PLAYED_BACKGROUND_COLOR )	
				if (c, r)  == self.start_pos:
					text_color = THECOLORS["green"]		
				else:
					text_color = PLAYED_COLOR
				text = self.font.render(str(piece_id), True, text_color)	
				xpos = (c*self.piece_w) + (self.piece_w/2) - (text.get_width()/2)
				ypos = (r*self.piece_h) + (self.piece_h/2) - (text.get_height()/2)				
				my_surface.blit(text, (xpos, ypos))				

			# Paint goals
			for c, r in self.goals:
				piece_id = self.get_piece((c, r))
				pos = (c*self.piece_w+1, r*self.piece_h+1)
				#box(my_surface, pos+(self.piece_w-1, self.piece_h-1), 
				#	THECOLORS["green"] )			
				#if (c, r) in self.touched_goals:
				#	box(my_surface, pos+(self.piece_w-1, self.piece_h-1), 
				#		THECOLORS["green"] )				
					
				text = self.font.render(str(piece_id), True, THECOLORS["yellow"])	
				xpos = (c*self.piece_w) + (self.piece_w/2) - (text.get_width()/2)
				ypos = (r*self.piece_h) + (self.piece_h/2) - (text.get_height()/2)				
				my_surface.blit(text, (xpos, ypos))				
								
			
			self.needs_static_redraw = False
		tmp_surface.blit(my_surface, (0,0))
		
		
		screen.blit(tmp_surface, (self.h_border, self.header_height))

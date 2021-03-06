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
		
		surface  = pygame.image.load(get_resource('gfx/lightning.png'))
		self.lighthing_surface = pygame.transform.scale(surface, (self.piece_w, self.piece_h))
		
	def start(self):
		for c in range(self.columns):			
			for r in range(self.rows):			
				self.set_piece(c, r, 0)
								
		self.falling_pieces = []
		self.popping_pieces = []
		pygame.time.set_timer(POPPING_EVENT, POPPING_INTERVAL)


	def add_popping(self, (data)):
		self.popping_pieces.append(data)
		
	def get_zap_group(self, board_x, board_y, matching_group, u=0, d=0, r=0, l=0):
		""" search for objects in the specified direction path """
		
		if board_x < 0 or board_x > self.columns-1 or \
			board_y < 0 or board_y > self.rows-1:
				return []
		if(board_x, board_y) in matching_group:
			return []						
		piece_id = self.get_piece(board_x, board_y)
		if piece_id == 0:
			return []
		matching_group.append((board_x, board_y))
		if piece_id == -1:
			d=u=r=l=1
		if d:
			self.get_zap_group(board_x, board_y+1, matching_group, d=1)
		if u:
			self.get_zap_group(board_x, board_y-1, matching_group, u=1)
		if l:
			self.get_zap_group(board_x-1, board_y, matching_group, l=1)
		if r:
			self.get_zap_group(board_x+1, board_y, matching_group, r=1)
		return matching_group
		
	def get_same_adjacent(self, x, y, match_id=None):
		""" return list of adjance pieces starting a x,y with the same id """
		# Check for board boundaries
		if match_id is None:
			self.same_adjancent = []

		if x<0 or y<0 or x>self.columns-1 or y>self.rows-1:
			return []
		if (x, y) in self.same_adjancent:
			return []
					
		bubble_id = self._board[x][y]
		# Do not select if there is a match_id and it doesn't match
		if not bubble_id or (match_id and match_id<>bubble_id):
			return []
			
		# Try to select all adjacent pieces with matching ids
		self.same_adjancent += [(x, y)]
		self.get_same_adjacent(x-1, y, bubble_id)
		self.get_same_adjacent(x+1, y, bubble_id)
		self.get_same_adjacent(x, y-1, bubble_id)
		self.get_same_adjacent(x, y+1, bubble_id)		
		return self.same_adjancent

	def remove(self, aList):
		""" Remove list of pieces"""		
		for (c,r) in aList:
			self.set_piece(c, r, 0)
						
		
	def remove_vertical_gaps(self):
		""" Remove vertical gaps by setting pieces to falling """
		# For each column, flag when a gap was found
		for x in range(self.columns):
			falling = False
			for y in range(self.rows-1,-1,-1):
				if self._board[x][y] == 0:
					falling = True
				elif falling:
						bubble_id = self._board[x][y]
						self.set_piece(x, y, 0)
						self.add_falling_piece(x, y, bubble_id)
			
	def insert_row(self, row_nr=0, with_special=False):
		for c in range(self.columns):			
			piece_id = -1 if with_special and randint(0, 50) == 0 else None
			self.add_falling_piece(c, row_nr, piece_id)
			
	def set_piece(self, x, y, piece_id):
		self._board[x][y] = piece_id
		self.needs_static_redraw = True
		
	def get_piece(self, x, y):
		return self._board[x][y]	
			
	def add_falling_piece(self, column, row, bubble_id=None):
		""" 
		To ensure collisions are detected from bottom to top, 
		insert items ordered by ypos
		"""
		if not bubble_id:
			bubble_id = randint(1, self.max_rand_id)
		ypos = row*self.piece_h
		board_x, board_y = column, row
		if self._board[board_x][board_y] != 0:
			raise Exception("Overwriting piece!?")
		insert_pos = len(self.falling_pieces)
		# Insert orderered by ypos, descendent
		for i in range(len(self.falling_pieces)):
			if ypos > self.falling_pieces[i][1]:
				insert_pos = i
				break
		self.falling_pieces.insert(insert_pos, [column, ypos, bubble_id])

	def check_event(self, event):
		if event.type == POPPING_EVENT:					
			for piece in self.popping_pieces:
				piece[0] -= 1				
			# Keep only popping bubles whose time did not run out
			self.popping_pieces = [piece for piece in self.popping_pieces if piece[0]>0]				

	def falling_move(self, speed):
		""" 
		Move falling pieces
		If they reach the ground or hit another piece add it to the 
		static playboard and remove them from the falling list
		"""
		for piece in self.falling_pieces:
			column, ypos, bubble_id = piece
			ypos += speed
			piece[1] = ypos
			board_x = column
			board_y = ypos/self.piece_h
			# if hit ground 
			if board_y == self.rows - 1: 				
				self.set_piece(board_x, board_y, bubble_id)
				piece[0] = -1 # Mark to delete
			# if found a ground piece
			elif self._board[board_x][board_y+1]<>0: # found piece
				self.set_piece(board_x, board_y, bubble_id)
				piece[0] = -1 # Mark to delete 				
		# Remove deleted pieces
		self.falling_pieces = [piece for piece in self.falling_pieces if piece[0]<>-1]

	def set_surfaces(self, surfaces):	
		self.surfaces = []
		self.mini_surfaces = []
		for surface in surfaces:
			surface = pygame.transform.scale(surface, (self.piece_w, self.piece_h))
			mini_surface = pygame.transform.scale(surface, (self.piece_w/2, self.piece_h/2))
			self.surfaces.append(surface)
			self.mini_surfaces.append(mini_surface)
			
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
						if piece_id == -1:
							my_surface.blit(self.lighthing_surface, pos)
						else:
							my_surface.blit(self.surfaces[piece_id-1], pos)
			self.needs_static_redraw = False
		tmp_surface.blit(my_surface, (0,0))
		
		# Draw popping pieces
		for pop_count, (c, r), piece_id in self.popping_pieces:
			pos_x = (c*self.piece_w)+(self.piece_w/2)-(self.piece_w/4)
			pos_y = (r*self.piece_h)+(self.piece_h/2)-(self.piece_w/4)
			tmp_surface.blit(self.mini_surfaces[piece_id-1], (pos_x, pos_y))
			
		# Draw falling pieces
		for c, ypos, piece_id in self.falling_pieces:
			pos = (c*self.piece_w, ypos)
			if piece_id == -1:
				tmp_surface.blit(self.lighthing_surface, pos)
			else:
				tmp_surface.blit(self.surfaces[piece_id-1], pos)
		
		screen.blit(tmp_surface, (self.h_border, self.header_height))
			
		


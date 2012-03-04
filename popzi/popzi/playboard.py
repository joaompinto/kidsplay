#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import randint

class PlayBoard:
	""" The playboard is a two dimensional data store for the game date 
	it also provides some helper methods for the game logic """
	def __init__(self, columns, rows, piece_w, piece_h):		
		self.rows = rows
		self.columns = columns		
		self.piece_w = piece_w
		self.piece_h = piece_h
		# Create two dimentional array using list comprehension
		# This array stores data for the static pieces on the game board
		self.board = [x[:] for x in [[0]*rows]*columns]
		# List of (animated) falling pieces 
		# Items on the list = (column, ypos, bubble_id)
		self.falling_pieces = []	
		# Max random id that can be assigned to a board piece
		self.max_rand_id = 5 
				
	def ramdom_rows(self, nr_rows):
		""" Assign random values to the specified nr of bottom rows """
		for c in range(self.columns):			
			for r in range(nr_rows):			
				bubble_id = randint(1, self.max_rand_id)
				self.board[self.columns-c-1][self.rows-r-1] = bubble_id
	
	def get_same_adjacent(self, x, y, match_id=None):
		""" return list of adjance pieces starting a x,y with the same id """
		# Check for board boundaries
		if match_id is None:
			self.same_adjancent = []

		if x<0 or y<0 or x>self.columns-1 or y>self.rows-1:
			return []
		if (x, y) in self.same_adjancent:
			return []
					
		bubble_id = self.board[x][y]
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
			self.board[c][r] = 0
		
	def remove_vertical_gaps(self):
		""" Remove vertical gaps by setting pieces to falling """
		# For each column, flag when a gap was found
		for x in range(self.columns):
			falling = False
			for y in range(self.rows-1,-1,-1):
				if self.board[x][y] == 0:
					falling = True
				elif falling:
						bubble_id = self.board[x][y]						
						self.board[x][y] = 0
						self.add_falling_piece(x, y*self.piece_h, bubble_id)
			
	def insert_row(self, row_nr=0):
		for c in range(self.columns):
			bubble_id = randint(1, self.max_rand_id)
			self.add_falling_piece(c, row_nr*self.piece_h, bubble_id)
			
	def add_falling_piece(self, column, ypos, bubble_id):
		""" 
		To ensure collisions are detected from bottom to top, 
		insert items ordered by ypos
		"""
		board_x = column
		board_y = ypos/self.piece_h
		if self.board[board_x][board_y] != 0:
			raise Exception("Overwriting piece!?")
		insert_pos = len(self.falling_pieces)
		# Insert orderered by ypos, descendent
		for i in range(len(self.falling_pieces)):
			if ypos > self.falling_pieces[i][1]:
				insert_pos = i
				break
		self.falling_pieces.insert(insert_pos, [column, ypos, bubble_id])

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
			#hit_y = (ypos+self.piece_h)/self.piece_h
			# if hit ground 
			if board_y == self.rows - 1: 
				self.board[board_x][board_y] = bubble_id
				piece[0] = -1 # Mark to delete
			# if found a ground piece
			elif self.board[board_x][board_y+1]<>0: # found piece
				self.board[board_x][board_y] = bubble_id
				piece[0] = -1 # Mark to delete 				
		# Remove deleted pieces
		self.falling_pieces = [piece for piece in self.falling_pieces if piece[0]<>-1]

#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import string
import random
import os

# PyGame Constants
from os.path import join
import pygame
from pygame.locals import *
from pygame.color import THECOLORS
from pygame.gfxdraw import box, filled_circle
import random 
from random import randint

APPEND_ROW_EVENT = pygame.USEREVENT + 1
FALLING_MOVE_EVENT = pygame.USEREVENT + 2


FALLING_SPEED = 10
FALLING_INTERVAL = 33

try:
    import android
    ANDROID = True
except ImportError:
    ANDROID = None

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
		""" Remove selected pieces """
		for (c,r) in aList:			
			self.board[c][r] = 0
		
	def remove_vertical_gaps(self):
		""" Remove vertical gaps by moving pieces to bottom """
		# For each column, create the list with non zero ids
		# Final column = padding zeros followed by non zero ids
		for x in range(self.columns):
			no_gaps_pieces = [piece for piece in self.board[x] if piece]
			self.board[x] = [0]*(self.rows-len(no_gaps_pieces)) + no_gaps_pieces		

	def append_row(self):
		""" Append a row with random pieces  """
		# For each column, create the list with non zero ids
		# Final column = padding zeros followed by non zero ids and
		# an extra random bubble id
		for x in range(self.columns):
			no_gaps_pieces = [piece for piece in self.board[x] if piece]
			bubble_id = randint(1, self.max_rand_id)
			self.board[x] = [0]*(self.rows-len(no_gaps_pieces)-1) \
				+ no_gaps_pieces + [bubble_id] 

	def insert_row(self):
		for c in range(self.columns):
			bubble_id = randint(1, self.max_rand_id)
			self.add_falling_piece(c, 0, bubble_id)
			
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

	def falling_move(self):
		""" 
		Move falling pieces
		If they reach the ground or hit another piece add it to the 
		static playboard and remove them from the falling list
		"""
		for piece in self.falling_pieces:
			column, ypos, bubble_id = piece
			piece[1] += FALLING_SPEED
			board_x = column
			board_y = ypos/self.piece_h
			# if hit ground 
			if board_y == self.rows - 1: 
				self.board[board_x][board_y] = bubble_id
				piece[0] = -1 # Mark to delete
			# if found a ground piece
			elif self.board[board_x][board_y+1]!=0: # found piece
				self.board[board_x][board_y] = bubble_id
				piece[0] = -1 # Mark to delete 				
		# Remove deleted pieces
		self.falling_pieces = [piece for piece in self.falling_pieces if piece[0]<>-1]
						
	
class Game:
	top_header = 60
	board_bottom = 640+top_header
	side = 320
	columns = 10
	rows = 20	
	playboard = PlayBoard(columns, rows, 32, 32)
	def __init__(self):
		random.seed()
		#self.playboard.ramdom_rows(5)	
		
	def init(self):
		#WINSIZE = 480, 800
		WINSIZE = self.side, self.board_bottom	
		os.environ['SDL_VIDEO_CENTERED'] = '1'
		pygame.init()	
		if not ANDROID:
			pygame.mixer.init()	
		
		# Map the back button to the escape key.
		if ANDROID:
			android.init()
			android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
        		
		self.clock = pygame.time.Clock()			
		self.screen = pygame.display.set_mode(WINSIZE,0,8)
		pygame.display.set_caption('Popzi')
	
		self.bubble_surfaces = self.load_bubbles()
		self.bubble_w = self.bubble_surfaces[0].get_width()
		self.bubble_h = self.bubble_surfaces[0].get_height()
		
		if not ANDROID:
			self.pop_sound = pygame.mixer.Sound("sfx/pop-Sith_Mas-485.wav")
			self.wrong_sound = pygame.mixer.Sound("sfx/Buzz_But-wwwbeat-1892.wav")
	
	def run(self):
		# The target frames per second is used to "sleep" the main loop between
		# screen redraws
		TARGET_FPS = 30
		pygame.time.set_timer(APPEND_ROW_EVENT, 5*1000)
		pygame.time.set_timer(FALLING_MOVE_EVENT, FALLING_INTERVAL)
		self.playboard.insert_row()
		# The Main Event Loop
		while self._check_events():				 
			self._draw()
			self.clock.tick(TARGET_FPS)

	def _check_events(self):		
		playboard = self.playboard
		events = pygame.event.get()    
		# Android-specific:
		if ANDROID and android.check_pause():
			android.wait_for_resume()		    
		# Handle events
		for e in events:			
			if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
				return False
			elif e.type == MOUSEBUTTONDOWN:
				x,y = e.pos
				board_x = x/self.bubble_w
				board_y = (y-self.top_header)/self.bubble_h	
				if board_x < 0 or board_y < 0 or \
					board_x > self.columns-1 or board_y > self.rows-1 :
					board_x = board_y = None
				else:				
					color_group = playboard.get_same_adjacent(board_x, board_y)
					if len(color_group) > 1:
						if not ANDROID:
							self.pop_sound.play()
						playboard.remove(color_group)
						playboard.remove_vertical_gaps()
					elif len(color_group) == 1:
						if not ANDROID:
							self.wrong_sound.play()
			elif e.type == APPEND_ROW_EVENT:						
				self.playboard.insert_row()
			elif e.type == FALLING_MOVE_EVENT:
				touch_down = self.playboard.falling_move()
		return True
								
	def _draw(self):
		screen = self.screen
		screen.fill(THECOLORS["black"])
		# Draw falling bubbles
		for c, ypos, bubble_id in self.playboard.falling_pieces:
			rect = pygame.rect.Rect((c*self.bubble_w)+1, self.top_header+ypos, self.bubble_w, self.bubble_h)
			screen.blit(self.bubble_surfaces[bubble_id], rect)
		# Draw the bubbles
		for c in range(self.playboard.columns):
			for r in range(self.playboard.rows):
				bubble_id = self.playboard.board[c][r]
				if bubble_id != 0:
					rect = pygame.rect.Rect((c*self.bubble_w)+1, self.top_header+r*(self.bubble_h), self.bubble_w, self.bubble_h)	
					screen.blit(self.bubble_surfaces[bubble_id], rect)
					
		pygame.display.flip()

	def load_bubbles(self):
		""" Load bubbles image files """
		bubbles = []
		for n in range(8):
			fn = join('gfx', 'balls', 'bubble-%s.gif' % (n+1))
			bubble = pygame.image.load(fn)
			bubbles.append(bubble)
		return bubbles		

def main():
    game = Game()
    game.init()
    game.run()

if __name__=="__main__":
	main()    

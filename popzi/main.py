#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import string
import random

# PyGame Constants
from os.path import join
import pygame
from pygame.locals import *
from pygame.color import THECOLORS
from pygame.gfxdraw import box, filled_circle
import random 
from random import randint

APPEND_ROW_EVENT = pygame.USEREVENT + 1


class PlayBoard:
	def __init__(self, columns, rows):		
		self.rows = rows
		self.columns = columns		
		# Create two dimentional array using list comprehension
		self.board = [x[:] for x in [[0]*rows]*columns]		
		# List of selected pieces
		self.selected = []
		self.rand_color = 5
		
	def ramdom_rows(self, nr_rows):
		""" Assign random values to the specified nr of bottom rows """

		for c in range(self.columns):			
			for r in range(nr_rows):			
				bubble_id = randint(1, self.rand_color)
				self.board[self.columns-c-1][self.rows-r-1] = bubble_id
	
	def get_same_adjacent(self, x, y, match_id=None):
		""" return list of adjance pieces starting a x,y with the same id
		"""
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
		self.selected = []
		
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
			bubble_id = randint(1, self.rand_color)
			self.board[x] = [0]*(self.rows-len(no_gaps_pieces)-1) \
				+ no_gaps_pieces + [bubble_id] 

def load_bubbles():
	bubbles = []
	for n in range(8):
		fn = join('gfx', 'balls', 'bubble-%s.gif' % (n+1))
		bubble = pygame.image.load(fn)
		bubbles.append(bubble)
	return bubbles

class Game:
	top_header = 60
	board_bottom = 640+top_header
	side = 320
	columns = 10
	rows = 20	
	playboard = PlayBoard(columns, rows)
	def __init__(self):
		random.seed()
		self.playboard.ramdom_rows(5)	
		
	def init(self):
		WINSIZE = self.side, self.board_bottom	
		pygame.init()	
		pygame.mixer.init()	
		self.clock = pygame.time.Clock()			
		self.screen = pygame.display.set_mode(WINSIZE,0,8)
		pygame.display.set_caption('Popzi')
	
		self.bubble_surfaces = load_bubbles()
		self.bubble_w = self.bubble_surfaces[0].get_width()
		self.bubble_h = self.bubble_surfaces[0].get_height()
		
		self.pop_sound = pygame.mixer.Sound("sfx/pop-Sith_Mas-485.wav")
		self.wrong_sound = pygame.mixer.Sound("sfx/Buzz_But-wwwbeat-1892.wav")
	
	def run(self):
		# The target frames per second is used to "sleep" the main loop between
		# screen redraws
		TARGET_FPS = 30
		pygame.time.set_timer(APPEND_ROW_EVENT, 5*1000)
		# The Main Event Loop
		while self._check_events():				 
			self._draw()
			self.clock.tick(TARGET_FPS)

	def _check_events(self):		
		playboard = self.playboard
		events = pygame.event.get()        
		# Handle events
		for e in events:			
			if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
				return False
#			elif e.type == MOUSEMOTION:				
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
						self.pop_sound.play()
						playboard.remove(color_group)
						playboard.remove_vertical_gaps()
					elif len(color_group) == 1:
						self.wrong_sound.play()
			elif e.type == APPEND_ROW_EVENT:						
				self.playboard.append_row()
		return True
								
	def _draw(self):
		screen = self.screen
		screen.fill(THECOLORS["black"])
		# Draw the selected color group background
		if len(self.playboard.selected) > 2:
			for (c,r) in self.playboard.selected:
				rect = pygame.rect.Rect((c*self.bubble_w), self.top_header+r*(self.bubble_h), self.bubble_w, self.bubble_h)	
				box(screen, rect, THECOLORS["yellow"])								
		# Draw the bubbles
		for c in range(self.playboard.columns):
			for r in range(self.playboard.rows):
				bubble_id = self.playboard.board[c][r]
				if bubble_id != 0:
					rect = pygame.rect.Rect((c*self.bubble_w)+1, self.top_header+r*(self.bubble_h), self.bubble_w, self.bubble_h)	
					screen.blit(self.bubble_surfaces[bubble_id], rect)
					
		pygame.display.flip()
	
if __name__=="__main__":
    game = Game()
    game.init()
    game.run()
    
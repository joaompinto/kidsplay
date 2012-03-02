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

# The target frames per second is used to "sleep" the main loop between
# screen redraws
TARGET_FPS = 30

class PlayBoard:
	def __init__(self, columns, rows):		
		self.rows = rows
		self.columns = columns		
		# Create two dimentional array using list comprehension
		self.board = [x[:] for x in [[0]*rows]*columns]		
		# List of selected pieces
		self.selected = []
		
	def ramdom_rows(self, nr_rows, rand_max):
		""" Assign random values to the specified nr of bottom rows """

		for c in range(self.columns):			
			for r in range(nr_rows):			
				bubble_id = randint(1, rand_max)
				self.board[self.columns-c-1][self.rows-r-1] = bubble_id
	
	def select_with_adjacent(self, x, y, match_id=None):
		""" select pieces and all adjacent pieces with matching ids """		
		# Clean the selected list when starting
		if match_id is None: 
			self.selected = []			
		# Check for board boundaries
		if x<0 or y<0 or x>self.columns-1 or y>self.rows-1:
			return
		# Don't check on pieces already selected
		if (x,y) in self.selected:
			return
			
		bubble_id = self.board[x][y]
		# Do not select if there is a match_id and it doesn't match
		if not bubble_id or (match_id and match_id<>bubble_id):
			return			
		self.selected.append((x, y))
		# Try to select all adjacent pieces with matching ids
		self.select_with_adjacent(x-1, y, bubble_id)
		self.select_with_adjacent(x+1, y, bubble_id)
		self.select_with_adjacent(x, y-1, bubble_id)
		self.select_with_adjacent(x, y+1, bubble_id)		

	def remove_selected(self):
		""" Remove selected pieces """
		for (c,r) in self.selected:			
			self.board[c][r] = 0
		self.selected = []
		
	def remove_vertical_gaps(self):
		""" Remove vertical gaps by moving pieces to bottom """
		# For each column, create the list with non zero ids
		# Final column = padding zeros+non zero ids
		for x in range(self.columns):
			no_gaps_pieces = [piece for piece in self.board[x] if piece]
			self.board[x] = [0]*(self.rows-len(no_gaps_pieces)) + no_gaps_pieces		
		

def load_bubbles():
	bubbles = []
	for n in range(8):
		fn = join('gfx', 'balls', 'bubble-%s.gif' % (n+1))
		bubble = pygame.image.load(fn)
		bubbles.append(bubble)
	return bubbles
	
def main():
	random.seed()
	top_header = 60
	board_bottom = 640+top_header
	side = 320
	columns = 10
	rows = 20	
	playboard = PlayBoard(columns, rows)
	playboard.ramdom_rows(5, 7)	
	WINSIZE = side, board_bottom
	
	pygame.init()	
	pygame.mixer.init()	
	clock = pygame.time.Clock()
	
	screen = pygame.display.set_mode(WINSIZE,0,8)
	pygame.display.set_caption('Popzi')
	
	bubble_surfaces = load_bubbles()
	bubble_w = bubble_surfaces[0].get_width()
	bubble_h = bubble_surfaces[0].get_height()
		
	last_board_x = last_board_y = None
	# The Main Event Loop
	done = False
	while not done:
		     
		events = pygame.event.get()        
		# Handle events
		for e in events:
			if e.type == QUIT:
				done = True
				break
			elif e.type == KEYDOWN:
				if e.key == K_ESCAPE :
					done = True
					break						
			elif e.type == MOUSEMOTION:				
				x,y = pygame.mouse.get_pos()
				board_x = x/bubble_w
				board_y = (y-top_header)/bubble_h
				# Don't update if nothing changed
				if last_board_x != board_x or last_board_y != y:
					if board_x < 0 or board_y < 0 or \
						board_x > columns-1 or board_y > rows-1 :
						board_x = board_y = None
					else:
						playboard.select_with_adjacent(board_x, board_y)
			elif e.type == MOUSEBUTTONDOWN:
				if len(playboard.selected) > 2:
					playboard.remove_selected()
					playboard.remove_vertical_gaps()
				

		screen.fill(THECOLORS["black"])
		# Draw the selected color group background
		if len(playboard.selected) > 2:
			for (c,r) in playboard.selected:
				rect = pygame.rect.Rect((c*bubble_w), top_header+r*(bubble_h), bubble_w, bubble_h)	
				box(screen, rect, THECOLORS["yellow"])								
		# Draw the bubbles
		for c in range(playboard.columns):
			for r in range(playboard.rows):
				bubble_id = playboard.board[c][r]
				if bubble_id != 0:
					rect = pygame.rect.Rect((c*bubble_w)+1, top_header+r*(bubble_h), bubble_w, bubble_h)	
					screen.blit(bubble_surfaces[bubble_id], rect)
					
		pygame.display.flip()				
		clock.tick(TARGET_FPS)
	return
	
if __name__=="__main__":
    main()
    

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

TARGET_FPS = 60
class PlayBoard:
	def __init__(self, columns, rows):
		self.rows = rows
		self.columns = columns

		self.board = [x[:] for x in [[0]*rows]*columns]
		self.selected = []
		
	def ramdom_rows(self, nr_rows, rand_max):
		""" Assign random values to the specified nr of bottom rows """
		#print self.board
		for c in range(self.columns):			
			for r in range(nr_rows):			
				bubble_id = randint(1, rand_max)
				self.board[self.columns-c-1][self.rows-r-1] = bubble_id
		print self.board
		
	def select(self, x, y):
		self.selected = [(x, y)] if self.board[x][y] else []
		print "selected", x, y
	

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
	pygame.display.set_caption('Popit')
	
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
						playboard.select(board_x, board_y)
		# Draw
		screen.fill(THECOLORS["black"])
		for (c,r) in playboard.selected:
			print "Selected", c, r
			rect = pygame.rect.Rect((c*bubble_w), top_header+r*(bubble_h), bubble_w, bubble_h)	
			box(screen, rect, THECOLORS["yellow"])						
		
		#filled_circle(screen, 60, 60, 20, THECOLORS["red"])
		for c in range(playboard.columns):
			for r in range(playboard.rows):
				bubble_id = playboard.board[c][r]
				#print "bubble_id=", bubble_id
				#bubble_id = 2
				if bubble_id != 0:
					rect = pygame.rect.Rect((c*bubble_w)+1, top_header+r*(bubble_h), bubble_w, bubble_h)	
					screen.blit(bubble_surfaces[bubble_id], rect)
					
		pygame.display.flip()				
		clock.tick(TARGET_FPS)
	return
	
if __name__=="__main__":
    main()
    

#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import string
import random
import os

from playboard import PlayBoard

# PyGame Constants
from os.path import join
import pygame
from pygame.locals import *
from pygame.color import THECOLORS
from pygame.gfxdraw import box, filled_circle

try:
    import pygame.mixer as mixer
except ImportError:
    import android.mixer as mixer
import random 

APPEND_ROW_EVENT = pygame.USEREVENT + 1
FALLING_MOVE_EVENT = pygame.USEREVENT + 2


FALLING_SPEED = 10
FALLING_INTERVAL = 33

try:
    import android
    ANDROID = True
except ImportError:
    ANDROID = None		
    
class Game:
	top_header = 60
	board_bottom = 640+top_header
	side = 320
	columns = 10
	rows = 20	
	score = 0
	playboard = PlayBoard(columns, rows, 32, 32)
	def __init__(self):
		random.seed()
		#self.playboard.ramdom_rows(5)	
		
	def init(self):
		#WINSIZE = 480, 800
		WINSIZE = self.side, self.board_bottom	
		if not ANDROID:
			os.environ['SDL_VIDEO_CENTERED'] = '1'
		pygame.init()	
		if not ANDROID:
			mixer.init()	
		
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
		
		self.pop_sound = mixer.Sound("sfx/pop-Sith_Mas-485.wav")
		self.wrong_sound = mixer.Sound("sfx/Buzz_But-wwwbeat-1892.wav")
		
		self.score_font = pygame.font.Font(join("fonts", "FreeSans.ttf"), 25)
	
	def run(self):
		# The target frames per second is used to "sleep" the main loop between
		# screen redraws
		TARGET_FPS = 30
		pygame.time.set_timer(APPEND_ROW_EVENT, 5*1000)
		pygame.time.set_timer(FALLING_MOVE_EVENT, FALLING_INTERVAL)
		for row in range(0, 5):
			self.playboard.insert_row(row)
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
					color_count = len(color_group)
					if color_count > 1:
						self.pop_sound.play()
						self.score += color_count
						if color_count > 4:
							color_count += 10
						elif color_count > 6:
							color_count += 20
						playboard.remove(color_group)
						playboard.remove_vertical_gaps()
					elif color_count == 1:
						self.wrong_sound.play()
			elif e.type == APPEND_ROW_EVENT:						
				self.playboard.insert_row()
			elif e.type == FALLING_MOVE_EVENT:
				touch_down = self.playboard.falling_move(FALLING_SPEED)
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
		
		
		text = self.score_font.render('Score: %d' %self.score, True, (255,255, 255), (0, 0, 0))		
		textRect = pygame.rect.Rect((10,5)+text.get_size())
		screen.blit(text, textRect)
		pygame.display.flip()

	def load_bubbles(self):
		""" Load bubbles image files """
		bubbles = []
		for n in range(8):
			fn = join('gfx', 'balls', 'bubble-%s.gif' % (n+1))
			bubble = pygame.image.load(fn)
			bubbles.append(bubble)
		return bubbles		

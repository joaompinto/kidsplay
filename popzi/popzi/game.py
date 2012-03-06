#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@copyright:
  (C) Copyright 2012, Open Source Game Seed <devs at osgameseed dot org>

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

import time
import string
import random
import os
from os.path import expanduser, exists, isdir

from playboard import PlayBoard

# PyGame Constants
from os.path import join
import pygame
from pygame.locals import *
from pygame.color import THECOLORS
from pygame.gfxdraw import box, rectangle, filled_circle
from popzi.buttons import Button

try:
    import pygame.mixer as mixer
except ImportError:
    import android.mixer as mixer
import random 

INSERT_ROW_EVENT = pygame.USEREVENT + 1
FALLING_MOVE_EVENT = pygame.USEREVENT + 2

THEMES = ['Marbles', 'Fruits']
TARGET_FPS = 30

FALLING_SPEED = 10
FALLING_INTERVAL = 33

try:
    import android
    ANDROID = True
except ImportError:
    ANDROID = None		
    
class Game:
	header_height = 60
	columns = 10
	rows = 20	
	# Dimension for the "mini" pieces, mini pieces are shown when
	# a piece is popping up.
	mini_w = mini_h = 16	
	
	# List of bubles being poped (count, position, piece_id)
	theme = "marbles"
	
	def __init__(self):
		random.seed()
		#self.playboard.ramdom_rows(5)	
		
	def init(self):
		if not ANDROID:
			os.environ['SDL_VIDEO_CENTERED'] = '1'
			WINSIZE = 480, 800
		else:
			WINSIZE = 0, 0
		pygame.init()	
		if not ANDROID:
			mixer.init()	
		
		# Map the back button to the escape key.
		if ANDROID:
			android.init()
			android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

		self.clock = pygame.time.Clock()			
		screen = self.screen = pygame.display.set_mode(WINSIZE)
		self.width, self.height = screen.get_width(), screen.get_height()
		pygame.display.set_caption('Popzi')
					
		self.pop_sound = mixer.Sound("sfx/pop.wav")
		
		self.score_font = pygame.font.Font(join("fonts", "FreeSans.ttf"), 25)		
		
		self.start_button = Button("Start game")
		self.start_button.setCords((self.screen.get_width()/2) - (self.start_button.rect.width/2), 100)
		self.themes_button = Button("Select theme")
		self.themes_button.setCords((self.screen.get_width()/2) - (self.start_button.rect.width/2), 100+(self.start_button.rect.height*2))
		
		# Dimension for the pieces
		horizontal_size = self.screen.get_width()/10
		vertical_size = (self.screen.get_height()-self.header_height)/20
		self.piece_w = self.piece_h = vertical_size if vertical_size < horizontal_size else horizontal_size
		self.playboard = PlayBoard(self.columns, self.rows, self.piece_w, self.piece_h)
		self.h_border = (self.screen.get_width()-(self.piece_w*10))/2
		if self.h_border < 0: self.h_border = 0
		
		self._read_theme_config()
		
	def _read_theme_config(self):
		fname = self._config_file('theme.config')
		# Set the theme from the config file
		try:
			with open(fname, 'r') as theme_config:											
				config_theme = theme_config.read()
				if isdir(join('gfx', 'themes', config_theme)):
					self.theme = config_theme
		except IOError:
			pass

		self._set_theme()
		
			
	def start(self):
		self.level = 1
		self.score = self.level_score = self.remaining_score = 0
		self.is_game_over = False
		self.drop_row_interval = 10
		self.level = 1
		self._start_level()
		
	def _start_level(self):		
		self.level_score = self.remaining_score
		# Keep remaining score
		self.is_level_complete = False
		level = self.level
		
		# Adjust game settings based on the level
		self.drop_row_interval = 11 - self.level 
		if self.drop_row_interval < 1:
			self.drop_row_interval = 1	
		starting_rows = 4+self.level
		if starting_rows > 10:
			starting_rows = 10
		self.level_score_goal = 100*level
		
		# Restart board
		self.popping_pieces = []
		self.playboard.start()
		for row in range(0, starting_rows):
			self.playboard.insert_row(row)
		# Start timers
		pygame.time.set_timer(INSERT_ROW_EVENT, self.drop_row_interval*1000)
		pygame.time.set_timer(FALLING_MOVE_EVENT, FALLING_INTERVAL)
			
	def _config_file(self, fname):
		""" Return full filename for a config file based on the platform """
		if ANDROID:
			full_fname = fname
		else:
			config_dir = os.getenv('XDG_CONFIG_HOME', expanduser('~/.config'))
			config_dir = join(config_dir, 'popzi')
			if not exists(config_dir):
				os.makedirs(config_dir, 0750)
			full_fname = join(config_dir, fname)
		return full_fname
		
	def menu(self):
		screen = self.screen
		action = None
		while True:	
			for event in pygame.event.get():
				if event.type == MOUSEBUTTONDOWN:	
					mouse_pos = pygame.mouse.get_pos()
					if self.start_button.is_pressed(mouse_pos):
						self.run()
					if self.themes_button.is_pressed(mouse_pos):
						self._themes_menu()						
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					return False							
			screen.blit(self.background, (0,0))							
			screen.blit(self.start_button.image, self.start_button.rect)
			screen.blit(self.themes_button.image, self.themes_button.rect)
			pygame.display.flip()
			self.clock.tick(TARGET_FPS)

	def _set_theme(self):
		WINSIZE = self.width, self.height
		fn = join('gfx', 'themes', self.theme , 'background.jpg')
		background = pygame.image.load(fn)							
		self.background = pygame.transform.scale(background, (WINSIZE))
		self.piece_surfaces,  self.mini_piece_surfaces = self._load_pieces()
		
		
	def _themes_menu(self):
		screen = self.screen
		action = None
		buttons = []
		ypos = 100
		for theme_name in THEMES:
			button = Button(theme_name)
			button.setCords((self.screen.get_width()/2) - (self.start_button.rect.width/2), ypos)
			buttons.append(button)
			ypos += 50
		
		while True:	
			for event in pygame.event.get():
				if event.type == MOUSEBUTTONDOWN:	
					mouse_pos = pygame.mouse.get_pos()
					for button in buttons:
						if button.is_pressed(mouse_pos):
							self.theme = button.text.lower()
							self._set_theme()
							fname = self._config_file('theme.config')
							with open(fname, 'w') as theme_config:								
								theme_config.write(self.theme)
							return
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					return False							
			screen.blit(self.background, (0,0))	
			for button in buttons:
				screen.blit(button.image, button.rect)
			pygame.display.flip()
			self.clock.tick(TARGET_FPS)			
		
	def run(self):
		# The target frames per second is used to "sleep" the main loop between
		# screen redraws
		
		self.start()		
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
				if self.is_game_over:
					if self.start_button.is_pressed(e.pos):
						self.start()
					return True
				# Level completed only accepts touch after a 2 seconds wait
				elif self.is_level_complete:
					if time.clock() - self.level_complete_time > 2:					
						self.level += 1
						self._start_level()
					return True					
				x,y = e.pos
				board_x = (x-self.h_border)/self.piece_w
				board_y = (y-self.header_height)/self.piece_h	
				if board_x < 0 or board_y < 0 or \
					board_x > self.columns-1 or board_y > self.rows-1 :
					board_x = board_y = None
				else:				
					matching_group = playboard.get_same_adjacent(board_x, board_y)
					matching_count = len(matching_group)
					if matching_count > 1:
						self.pop_sound.play()
						# Update score
						score = matching_count
						if matching_count > 4:
							score += 10
						elif matching_count > 6:
							score += 20
						self.score += score							
						self.level_score += score
						for x,y  in matching_group:
							piece_id = self.playboard.get_piece(x, y)
							self.popping_pieces.append([5, (x,y), piece_id])
						playboard.remove(matching_group)
						playboard.remove_vertical_gaps()
						# Level is complete
						self.remaining_score = self.level_score - self.level_score_goal
						if self.remaining_score >= 0:							
							pygame.time.set_timer(INSERT_ROW_EVENT, self.drop_row_interval*1000)
							pygame.time.set_timer(FALLING_MOVE_EVENT, FALLING_INTERVAL)
							self.level_score = self.level_score_goal	
							self.is_level_complete = True
							self.level_complete_time = time.clock()
			elif e.type == INSERT_ROW_EVENT:
				for c in range(self.playboard.columns):
					# If there is a piece on the first row the game is over
					if self.playboard.get_piece(c, 0) != 0:
						pygame.time.set_timer(INSERT_ROW_EVENT, 0)
						pygame.time.set_timer(FALLING_MOVE_EVENT, 0)						
						self.is_game_over = True						
						break
				if not self.is_game_over:
					self.playboard.insert_row()
			elif e.type == FALLING_MOVE_EVENT:
				touch_down = self.playboard.falling_move(FALLING_SPEED)
				# Decrease visible time count for popping pieces
				for piece in self.popping_pieces:
					piece[0] -= 1
				# Keep only popping bubles whose time did not run out
				self.popping_pieces = [piece for piece in self.popping_pieces if piece[0]>0]				
		return True
								
	def _draw(self):
		screen = self.screen
		screen.blit(self.background, (0,0))

		# Score text
		text = self.score_font.render(' Score: %d ' % self.score, True, 
			THECOLORS["white"], THECOLORS["black"])		
		screen.blit(text, (10,5))
		

		# Level text
		text = self.score_font.render(' Level: %d ' % self.level, True, 
			THECOLORS["white"], THECOLORS["black"])		
		screen.blit(text, (self.width-text.get_width()-5,5))
		
		# Level progress rectangle
		rect = pygame.Rect(20, 5+text.get_height(), self.width-40, 20)		
		rectangle(screen, rect, THECOLORS["white"])
		
		# Level progress indicator (fill)
		filled = (float(self.level_score)/self.level_score_goal)*(self.width-40)
		rect = pygame.Rect(20, 5+text.get_height(), filled, 20)
		screen.fill(THECOLORS["white"], rect, special_flags=0)
		rectangle(screen, rect, THECOLORS["white"])
		
		# Game over label when required
		if self.is_game_over:
			text = self.score_font.render(' GAME OVER ', True, THECOLORS["red"], THECOLORS["black"])		
			screen.blit(text, ((screen.get_width()/2) - (text.get_width()/2), 150))
			screen.blit(self.start_button.image, self.start_button.rect)	
			
		if self.is_level_complete:
			text = self.score_font.render(' LEVEL COMPLETE! ', True, THECOLORS["yellow"], THECOLORS["black"])		
			screen.blit(text, ((screen.get_width()/2) - (text.get_width()/2), 150))
						
		# Draw popping pieces
		for pop_count, (c, r), piece_id in self.popping_pieces:
			pos_x = self.h_border+(c*self.piece_w)+(self.piece_w/2)-(self.mini_w/2)
			pos_y = (self.header_height+r*self.piece_h)+(self.piece_h/2)-(self.mini_h/2)
			screen.blit(self.mini_piece_surfaces[piece_id-1], (pos_x, pos_y))
		# Draw falling pieces
		for c, ypos, piece_id in self.playboard.falling_pieces:
			pos = (self.h_border+(c*self.piece_w), self.header_height+ypos)
			screen.blit(self.piece_surfaces[piece_id-1], pos)
		# Draw the pieces
		for c in range(self.playboard.columns):
			for r in range(self.playboard.rows):
				piece_id = self.playboard.get_piece(c, r)
				if piece_id != 0:
					pos = (self.h_border+(c*self.piece_w), self.header_height+(r*self.piece_h))
					screen.blit(self.piece_surfaces[piece_id-1], pos)
					
		pygame.display.flip()

	def _load_pieces(self):
		""" Load pieces image files """
		mini_pieces = []
		pieces = []
		for n in range(5):
			fn = join('gfx', 'themes', self.theme, 'piece-%d.png' % (n+1))
			piece = pygame.image.load(fn)
			piece = pygame.transform.scale(piece, (self.piece_w, self.piece_h))
			pieces.append(piece)
			mini_pieces.append(pygame.transform.scale(piece, (self.mini_w, self.mini_h)))
			
		return pieces, mini_pieces

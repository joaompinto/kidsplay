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
from random import randint
import os
from datetime import date
from os.path import join, expanduser, exists, isdir
import pygame
from pygame.locals import *
from pygame.color import THECOLORS
from pygame.gfxdraw import box, rectangle, filled_circle

from buttons import Button
import resources as resources
from resources import get_resource
from playboard import PlayBoard

ANDROID = USE_MIXER = PYTHON4ANDROID = False

if os.getenv('ANDROID_APP_PATH'):
	PYTHON4ANDROID = True
else:
	USE_MIXER = True
	try:
		import android	
		import android.mixer as mixer
		ANDROID = True
	except ImportError:
		ANDROID = None	
		import pygame.mixer as mixer
	
INSERT_ROW_EVENT = pygame.USEREVENT + 1
FALLING_MOVE_EVENT = pygame.USEREVENT + 2


THEMES = ['Fruits', 'Marbles']
TARGET_FPS = 30

FALLING_SPEED = 10
FALLING_INTERVAL = 33

DEBUG = False
resources.DATA_DIR = "/usr/share/popzi"
    
class Game:
	COLUMNS = 10
	ROWS = 16

	# Top header for score
	header_height = 60
	
	# List of bubles being poped (count, position, piece_id)
	theme = "fruits"	
	
	def __init__(self):
		random.seed()
		self.draw_count = 0
		
	def init(self):
		flags = 0
		if not ANDROID:
			os.environ['SDL_VIDEO_CENTERED'] = '1'
			WINSIZE = 480, 800
		else:
			WINSIZE = 0, 0
			flags |= pygame.FULLSCREEN
		pygame.init()	
		if USE_MIXER:
			mixer.init()
		
		# Map the back button to the escape key.
		if ANDROID:
			android.init()
			android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

		self.clock = pygame.time.Clock()			
		if not (ANDROID or PYTHON4ANDROID):
			self.icon = pygame.image.load(get_resource('android-icon.png'))
			pygame.display.set_icon(self.icon)
		screen = self.screen = pygame.display.set_mode(WINSIZE, flags)
		self.width, self.height = screen.get_width(), screen.get_height()
		pygame.display.set_caption('Popzi')

		if USE_MIXER:
			self.pop_sound = mixer.Sound(get_resource("sfx/pop.ogg"))
		
		self.score_font = pygame.font.Font(get_resource(join("fonts", "FreeSans.ttf")), 25)
		self.completed_font = pygame.font.Font(get_resource(join("fonts", "FreeSans.ttf")), 40)
		
		self.start_button = Button("Start game")				
		self.themes_button = Button("Select theme")
						
		self.playboard = PlayBoard(screen, 
				self.COLUMNS, self.ROWS, self.header_height)
		
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
		self._start_level(DEBUG)		
		self.screen.fill((0,0,0 ))
		
		
	def _start_level(self, debug=False):		
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
		self.playboard.start()
		if debug:
			for c in range(self.COLUMNS):
				for r in range(self.ROWS):
					self.playboard.set_piece(c, r, (c % 5)+1)
		else:
			for row in range(0, starting_rows):
				self.playboard.insert_row(row, self.level > 2 )
		# Start timers
		if not debug:
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

	def _check_high_scores(self):
		""" Check if the current score is an high score.
			Update the highscore if required."""
		# Read the higshcore file and check min fields are found
		high_score_fn = self._config_file('highscore.list')
		hs_list = self._high_scores = []
		if exists(high_score_fn):
			with open(high_score_fn, 'r') as hs_file:
				for line in hs_file.readlines():
					fields = line.strip('\r\n').split(';')
					if len(fields) == 3:
						hs_list.append(fields)		
		# Search our score position
		score_pos = len(hs_list)
		for i in range(len(hs_list)):
			if self.score >= int(hs_list[i][0]):
				score_pos = i
				break
		
		# If we have a score pos, rebuild the score table and save it
		if score_pos < 10 :
			lower_scores = hs_list[score_pos:]	
			higher_scores = hs_list[:score_pos]			
								 
			hs_list = higher_scores+[[str(self.score), str(self.level), str(date.today())]]+lower_scores
			hs_list = hs_list[:10]
			self._high_scores = hs_list

			with open(high_score_fn+'.new', 'w') as hs_file:
				for score in self._high_scores:
					hs_file.write(';'.join(score)+"\n")
			if exists(high_score_fn):
				os.unlink(high_score_fn)
			os.rename(high_score_fn+".new", high_score_fn)		
			
		self.score_pos = score_pos
				
		
	def menu(self):
		screen = self.screen
		self.start_button.setCords((screen.get_width()/2) - (self.start_button.rect.width/2), 100)
		self.themes_button.setCords((screen.get_width()/2) - (self.start_button.rect.width/2), 100+(self.start_button.rect.height*2))		
		action = None
		while True:	
			for event in pygame.event.get():
				if event.type == MOUSEBUTTONDOWN:	
					mouse_pos = pygame.mouse.get_pos()
					if self.start_button.is_pressed(mouse_pos):
						self.run()
						self.start_button.setCords((screen.get_width()/2) - (self.start_button.rect.width/2), 100)
					if self.themes_button.is_pressed(mouse_pos):
						self._themes_menu()						
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					return False										
			screen.blit(self.background, (0, 0))
			screen.blit(self.start_button.image, self.start_button.rect)
			screen.blit(self.themes_button.image, self.themes_button.rect)
			pygame.display.flip()
			self.clock.tick(TARGET_FPS)

	def _set_theme(self):
		WINSIZE = self.width, self.height
		fn = join('gfx', 'themes', self.theme , 'background.jpg')
		background = pygame.image.load(get_resource(fn))							
		self.background = pygame.transform.scale(background, (WINSIZE))		
		surfaces = self._load_pieces()
		self.playboard.set_surfaces(surfaces)
		self.playboard.set_background(background)
		
	def _themes_menu(self):
		screen = self.screen
		action = None
		buttons = []
		ypos = 100
		for theme_name in THEMES:
			button = Button(theme_name)
			button.setCords((self.screen.get_width()/2) - (self.start_button.rect.width/2), ypos)
			buttons.append(button)
			ypos += 100
		
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
			self.playboard.check_event(e)
			if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
				return False
			elif e.type == MOUSEBUTTONDOWN:
				if self.is_game_over:
					if self.start_button.is_pressed(e.pos):
						self.start()
					return True
				# Level completed only accepts touch after a 2 seconds wait
				elif self.is_level_complete:
					if time.time() - self.level_complete_time > 2:					
						self.level += 1
						self._start_level()
					return True					
				x,y = e.pos
				board_x, board_y = self.playboard.get_board_pos(e.pos)
				if board_x < 0 or board_y < 0 or \
					board_x > self.COLUMNS-1 or board_y > self.ROWS-1 :
					board_x = board_y = None
				else:						
					piece_id = self.playboard.get_piece(board_x, board_y)
					if piece_id == -1: # Zap
						matching_group = self.playboard.get_zap_group(board_x, board_y, [])
					else:
						matching_group = playboard.get_same_adjacent(board_x, board_y)
					matching_count = len(matching_group)
					if matching_count > 1:
						if USE_MIXER:
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
							self.playboard.add_popping([5, (x,y), piece_id])							
						playboard.remove(matching_group)
						playboard.remove_vertical_gaps()
						# Level is complete
						self.remaining_score = self.level_score - self.level_score_goal
						if self.remaining_score >= 0:							
							pygame.time.set_timer(INSERT_ROW_EVENT, 0)
							pygame.time.set_timer(FALLING_MOVE_EVENT, 0)
							self.level_score = self.level_score_goal	
							self.is_level_complete = True
							self.level_complete_time = time.time()
					else:
						# Penalize massive touchers, drop on touch
						#candidate_pos = []
						#for c in range(self.playboard.columns):
							# If there is a piece on the first row the game is over
						#	if self.playboard.get_piece(c, 0) == 0:	
						#		candidate_pos.append(c)
						#if candidate_pos:
						#	c = randint(0, len(candidate_pos)-1)
						if self.playboard.get_piece(board_x, 0) == 0:
							playboard.add_falling_piece(board_x, 0)
			elif e.type == INSERT_ROW_EVENT:
				for c in range(self.playboard.columns):
					# If there is a piece on the first row the game is over
					if self.playboard.get_piece(c, 0) != 0:
						pygame.time.set_timer(INSERT_ROW_EVENT, 0)
						pygame.time.set_timer(FALLING_MOVE_EVENT, 0)						
						self.is_game_over = True
						self._check_high_scores()
						break
				if not self.is_game_over:
					self.playboard.insert_row(with_special=self.level > 2)
			elif e.type == FALLING_MOVE_EVENT:
				touch_down = self.playboard.falling_move(FALLING_SPEED)
				# Decrease visible time count for popping pieces
		return True
								
	def _draw(self):
		self.draw_count += 1
		if self.draw_count == 1:
			self.first_draw = time.clock()
			
		screen = self.screen	
		self.playboard.draw(screen)		

		# Score text
		text = self.score_font.render(' Score: %d ' % self.score, True, 
			THECOLORS["white"], THECOLORS["black"])		
		screen.blit(text, (10,0))
		
		# Level text
		text = self.score_font.render(' Level: %d ' % self.level, True, 
			THECOLORS["white"], THECOLORS["black"])		
		screen.blit(text, (self.width-text.get_width()-5,0))
		
		# Level progress box
		rect = pygame.Rect(20, 3+text.get_height(), self.width-40, 20)						
		rectangle(screen, rect, THECOLORS["white"])
		
		# Level progress indicator (fill)
		filled = (float(self.level_score)/self.level_score_goal)*(self.width-40)
		white_rect = pygame.Rect(20, 3+text.get_height(), filled, 20)
		black_rect = pygame.Rect(20+filled, 3+text.get_height(), self.width-40-filled, 20)
		screen.fill(THECOLORS["white"], white_rect)
		screen.fill(THECOLORS["black"], black_rect)
		rectangle(screen, rect, THECOLORS["white"])
							
		# Game over label when required
		if self.is_game_over:
			text = self.score_font.render(' GAME OVER ', True, THECOLORS["yellow"], THECOLORS["red"])		
			screen.blit(text, ((screen.get_width()/2) - (text.get_width()/2), self.header_height + 20))

			#high score table
			i = 0
			ypos = self.header_height + 10 + text.get_height() + 30
			for score in self._high_scores:
				if i == self.score_pos:
					fg_color = THECOLORS["black"]
					bg_color = THECOLORS["white"]
				else:
					fg_color = THECOLORS["white"]
					bg_color = THECOLORS["black"]
				text = self.score_font.render('  %6s - Level %2s (%s)  ' % (score[0], score[1], score[2]), True
					, fg_color, bg_color)
				screen.blit(text, ((screen.get_width()/2) - (text.get_width()/2), ypos))
				ypos += text.get_height()+10
				i += 1
			ypos += 20
			self.start_button.setCords((screen.get_width()/2) - (self.start_button.rect.width/2), ypos)
			screen.blit(self.start_button.image, self.start_button.rect)
							
		if self.is_level_complete:
			text = self.completed_font.render(' LEVEL COMPLETED ', True, THECOLORS["blue"], THECOLORS["yellow"])		
			screen.blit(text, ((screen.get_width()/2) - (text.get_width()/2), self.height/2-text.get_height()/2))
			
		pygame.display.flip()
		
		if DEBUG and self.draw_count == 100:
			print "Playboard draw CPU time=", time.clock()-self.first_draw
			self.draw_count = 0

	def _load_pieces(self):
		""" Load pieces image files """		
		pieces = []
		for n in range(5):
			fn = join('gfx', 'themes', self.theme, 'piece-%d.png' % (n+1))
			piece = pygame.image.load(get_resource(fn))
			pieces.append(piece)			
			
		return pieces

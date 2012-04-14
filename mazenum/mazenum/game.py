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

try:
	import android	
	import android.mixer as mixer
	ANDROID = True
except ImportError:
	ANDROID = None	
	import pygame.mixer as mixer
	
TARGET_FPS = 30

DEBUG = False
resources.DATA_DIR = "/usr/share/mazenum"
    
class Game:
	COLUMNS = 8
	ROWS = 12

	# Top header for score
	header_height = 60
	
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
		mixer.init()
		
		# Map the back button to the escape key.
		if ANDROID:
			android.init()
			android.map_key(android.KEYCODE_BACK, pygame.K_b)

		self.clock = pygame.time.Clock()			
		if not ANDROID:
			self.icon = pygame.image.load(get_resource('android-icon.png'))
			pygame.display.set_icon(self.icon)
		screen = self.screen = pygame.display.set_mode(WINSIZE, flags)
		self.width, self.height = screen.get_width(), screen.get_height()		
		pygame.display.set_caption('Mazenum')
		
		self.score_font = pygame.font.Font(get_resource(join("fonts", "FreeSans.ttf")), 25)
		self.completed_font = pygame.font.Font(get_resource(join("fonts", "FreeSans.ttf")), 40)
		
		self.start_button = Button("Start game")
						
		self.playboard = PlayBoard(screen, 
				self.COLUMNS, self.ROWS, self.header_height)
		self._set_background()
		self.is_game_over = False		

	def start(self, debug=False):		
		self.score = 0
		self.is_game_over = False
		self.level = 1
		self._start_level(DEBUG)
		
	def _start_level(self, debug=False):
		self.playboard.start(self.level)
		self.is_level_complete = False
			
	def _config_file(self, fname):
		""" Return full filename for a config file based on the platform """
		if ANDROID:
			full_fname = fname
		else:
			config_dir = os.getenv('XDG_CONFIG_HOME', expanduser('~/.config'))
			config_dir = join(config_dir, 'mazenum')
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
		action = None
		while True:			
			for event in pygame.event.get():
				if event.type == MOUSEBUTTONDOWN:	
					mouse_pos = pygame.mouse.get_pos()
					if self.start_button.is_pressed(event.pos):
						self.run()
						self.start_button.setCords((screen.get_width()/2) - (self.start_button.rect.width/2), 100)
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					return False							
			screen.blit(self.background, (0, 0))
			screen.blit(self.start_button.image, self.start_button.rect)
			pygame.display.flip()
			self.clock.tick(TARGET_FPS)

	def _set_background(self):
		WINSIZE = self.width, self.height
		fn = join('gfx', 'background.jpg')
		background = pygame.image.load(get_resource(fn))							
		self.background = pygame.transform.scale(background, (WINSIZE))
		self.playboard.set_background(self.background)
				
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
			elif e.type == KEYDOWN and e.key == pygame.K_b:
				if self.is_game_over:
					return False
				else:
					self.is_game_over = True
					self._check_high_scores()
			elif e.type == MOUSEBUTTONDOWN:					
				if self.is_level_complete:
					self.level += 1
					self._start_level()
				elif self.is_game_over and e.type == MOUSEBUTTONDOWN:
					if self.start_button.is_pressed(e.pos):
						self.start()
				else:
					self._on_touch(e.pos)									
		return True

	def _on_touch(self, pos):
		""" A position was touched """
		touch_pos = self.playboard.get_board_pos(pos)
		if not touch_pos: # Out of the board
			return 
		touch_x, touch_y = touch_pos
		# Revert last played ?
		if touch_pos == self.playboard.get_last_pos() and \
			len(self.playboard._play_path) > 1:
				self.playboard.remove_last()
				return			
		current_x, current_y = self.playboard.get_last_pos()
		
		# Ignore touches which are not adjacent
		if abs(touch_x - current_x) > 1 or abs(touch_y - current_y) > 1:
			return 
		current_value = self.playboard.get_piece((current_x, current_y))
		touch_value = self.playboard.get_piece(touch_pos)
		diff = touch_value - current_value if touch_value < 10 else touch_value
		if not diff in (1, -8): # Ignore non consecutive sequence -8=1-9
			return
		self.score += 1
		self.playboard.place_at((touch_x, touch_y))
		if touch_pos in self.playboard.goals:
			self.is_level_complete = True		
		
	def _draw(self):
		screen = self.screen
		self.draw_count += 1

		if self.draw_count == 1:
			self.first_draw = time.clock()

		self.playboard.draw(screen)		

		# Score text
		text = self.score_font.render(' Score: %d ' % self.score, True, 
			THECOLORS["white"])		
		screen.blit(text, (10,0))
		
		# Level text
		text = self.score_font.render(' Level: %d ' % self.level, True, 
			THECOLORS["white"])		
		screen.blit(text, (self.width-text.get_width()-5,0))
		
		# Level progress box
		#rect = pygame.Rect(20, 3+text.get_height(), self.width-40, 20)						
		#rectangle(screen, rect, THECOLORS["white"])
		
		# Level progress indicator (fill)
		#filled = (float(self.level_score)/self.level_score_goal)*(self.width-40)
		#white_rect = pygame.Rect(20, 3+text.get_height(), filled, 20)
		#black_rect = pygame.Rect(20+filled, 3+text.get_height(), self.width-40-filled, 20)
		#screen.fill(THECOLORS["white"], white_rect)
		#screen.fill(THECOLORS["black"], black_rect)
		#rectangle(screen, rect, THECOLORS["white"])
							
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
					bg_color = THECOLORS["gray"]
				text = self.score_font.render('  %6s - Level %2s (%s)  ' % (score[0], score[1], score[2]), True
					, fg_color, bg_color)
				screen.blit(text, ((screen.get_width()/2) - (text.get_width()/2), ypos))
				ypos += text.get_height()+10
				i += 1
			
			ypos += 20
			self.start_button.setCords((screen.get_width()/2) - (self.start_button.rect.width/2), ypos)
			screen.blit(self.start_button.image, self.start_button.rect)
							
		if self.is_level_complete and not self.is_game_over:
			text = self.completed_font.render(' LEVEL COMPLETED ', True, THECOLORS["blue"], THECOLORS["yellow"])		
			screen.blit(text, ((screen.get_width()/2) - (text.get_width()/2), self.height/2-text.get_height()/2))
			
		pygame.display.flip()
		
		if DEBUG and self.draw_count == 100:
			print "Playboard draw CPU time=", time.clock()-self.first_draw
			self.draw_count = 0

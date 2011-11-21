#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import string
import random

# PyGame Constants
import pygame
from pygame.locals import *
from pygame.color import THECOLORS
from pygame.gfxdraw import box

TARGET_FPS = 60

MOVE_PLANE_EVENT = pygame.USEREVENT + 1
MOVE_ORANGE_EVENT = pygame.USEREVENT + 2

def main():
	oranges = []
	plane_speed = 1
	WINSIZE = 1024,768
	pygame.init()	
	clock = pygame.time.Clock()
	screen = pygame.display.set_mode(WINSIZE,0,8)
	pygame.display.set_caption('Orange Drop!')

	plane_surface = pygame.image.load('plane.xpm')
	orange_surface = pygame.image.load('orange.xpm')
	plane_x = 0
	plane_rect = pygame.rect.Rect(plane_x, 0, plane_surface.get_width(), plane_surface.get_height())

	#letter_generator = LetterGenerator('KWXY')

	# The Main Event Loop
	done = False

	pygame.time.set_timer(MOVE_PLANE_EVENT, 10)
	pygame.time.set_timer(MOVE_ORANGE_EVENT, 10)
	
	while not done:
		          
		events = pygame.event.get()        
		for e in events:
			if e.type == QUIT:
				done = True
				break
			elif e.type == KEYDOWN:
				if e.key == K_SPACE:
					oranges.append([plane_rect.left+(plane_surface.get_width() / 2), plane_surface.get_height()])
				if e.key == K_ESCAPE :
					done = True
					break
				if e.key == K_f:
							pygame.display.toggle_fullscreen()
				elif e.type == MOUSEBUTTONDOWN:
					# drop ball
					pass
			elif e.type == MOVE_PLANE_EVENT:
				plane_rect.move_ip(plane_speed, 0)				
				if plane_rect.left >= screen.get_width() - plane_surface.get_width():
					plane_rect.left = 0								
			elif e.type == MOVE_ORANGE_EVENT:
				for orange in oranges:
					orange[1] += 1
		# Draw
		screen.fill(THECOLORS["black"])
		screen.blit(plane_surface, plane_rect)
		falling_oranges = []
		for i in range(0, len(oranges)):
			orange = oranges[i]
			rect = pygame.rect.Rect(orange[0], orange[1], plane_surface.get_width(), plane_surface.get_height())
			if orange[1] < screen.get_height():
				screen.blit(orange_surface, rect)
				falling_oranges.append(orange)
		oranges = falling_oranges # Only keep visible oranges
		pygame.display.flip()
		clock.tick(TARGET_FPS)
	print "Exiting!"
	return
	
if __name__=="__main__":
    main()
    

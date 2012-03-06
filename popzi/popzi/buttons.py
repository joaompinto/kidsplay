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

import pygame

import os
from os.path import join
from pygame.locals import *
from pygame.color import THECOLORS


def load_image(name, colorkey=None):
    fullname = os.path.join('gfx', 'buttons', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class Button():
    """Class used to create a button, use setCords to set 
        position of topleft corner."""
        
    def __init__(self, text=None):
        self.image, self.rect = load_image('dark.png')
        font = pygame.font.Font(join("fonts", "FreeSans.ttf"), 25)
        text_img = font.render(text, True, THECOLORS["white"])
        self.image.blit(text_img, (self.rect.width/2-text_img.get_width()/2, 0))
        self.text = text
        
    def setCords(self,x,y):
        self.rect.topleft = x,y
    
    def is_pressed(self, mouse_pos):
		return self.rect.collidepoint(mouse_pos)
        
def main():
	pygame.init()
	WINSIZE = 480, 800
	screen = pygame.display.set_mode(WINSIZE)
	button = Button(100, 100, "Test")
	button.setCords(100,100) #Button is displayed at 200,200
	while 1:
		for event in pygame.event.get():
			if event.type == MOUSEBUTTONDOWN:
				mouse = pygame.mouse.get_pos()
				if button.is_pressed(mouse):	#Button's pressed method is called
					print ('button hit')
		screen.blit(button.image, button.rect)
		pygame.display.flip()

if __name__ == '__main__': main()

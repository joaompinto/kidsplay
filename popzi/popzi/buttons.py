#load_image is used in most pygame programs for loading images
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

class Button(pygame.sprite.Sprite):
    """Class used to create a button, use setCords to set 
        position of topleft corner. Method pressed() returns
        a boolean and should be called inside the input loop."""
    def __init__(self, x, y, text=None):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('dark.png')
        self.rect.topleft = x,y
        font = pygame.font.Font(join("fonts", "FreeSans.ttf"), 25)
        text_img = font.render(text, True, THECOLORS["white"])
        self.image.blit(text_img, (self.rect.width/2-text_img.get_width()/2, 0))
        
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

#from bridgeFunction import *
import pygame
PATH = './drawing/'

######################################################################
# Board Class
######################################################################
class Board(pygame.sprite.Sprite):   
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(PATH+'rawboard.png')
        self.image = pygame.transform.scale(self.image, (360,360))
        self.rect = self.image.get_rect()

    def draw(self, screen):
        self.rect.center = (screenWidth/2,screenHeight/2)
        screen.blit(self.image,self.rect)

######################################################################
# Stone Class
######################################################################

class Stone(pygame.sprite.Sprite):
    
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)
        
        if color == 1: 
            self.image = pygame.image.load(PATH+'black.png')
        elif color == -1:
            self.image = pygame.image.load(PATH+'white.png')
 
        self.image = pygame.transform.scale(self.image, (70,70))
        self.rect = self.image.get_rect()
        

    def draw(self, screen, pixel):
        self.rect.center = (pixel[0],pixel[1])
        screen.blit(self.image,self.rect)
        
######################################################################
# Buttons
######################################################################

class Button(pygame.sprite.Sprite):
    
    def __init__(self, pos, rect, color, text = None):
	pygame.sprite.Sprite.__init__(self)
	self.pos = pos
	self.rect = pygame.Rect(rect)
	self.color = pygame.Color(*color)
	self.text = text
	
	if self.text:
	    self.text = self.renderText(self.text)
		
	self.image = self.roundedRect()
	
    def renderText(self, text, fontSize = 15, fontColor = (0,0,0)):
	myfont = pygame.font.SysFont("monospace",fontSize)
	rendered = myfont.render(text,1,fontColor)
	return rendered

    def roundedRect(self):

	radius = 0.8
	alpha = 80 # blur 0 ~ 255 vivid
	self.color.a = 0
	
	self.rect.topleft = 0,0
	rectangle = pygame.Surface(self.rect.size, pygame.SRCALPHA)
	rectpos = rectangle.get_rect()
	
	circle       = pygame.Surface([min(self.rect.size)*3]*2,pygame.SRCALPHA)
	pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
	circle       = pygame.transform.smoothscale(circle,[int(min(self.rect.size)*radius)]*2)

	radius              = rectangle.blit(circle,(0,0))
	radius.bottomright  = self.rect.bottomright
	rectangle.blit(circle,radius)
	radius.topright     = self.rect.topright
	rectangle.blit(circle,radius)
	radius.bottomleft   = self.rect.bottomleft
	rectangle.blit(circle,radius)

	rectangle.fill((0,0,0),self.rect.inflate(-radius.w,0))
	rectangle.fill((0,0,0),self.rect.inflate(0,-radius.h))

	rectangle.fill(self.color,special_flags=pygame.BLEND_RGBA_MAX)
	rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)
	
	
	if self.text:
	    textrect = self.text.get_rect()
	    x = rectpos.centerx - textrect.centerx
	    y = rectpos.centery - textrect.centery
	    rectangle.blit(self.text,(x,y))
	return rectangle   

    def draw(self, screen):
        screen.blit(self.image, self.pos)
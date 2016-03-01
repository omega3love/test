
from bridgeSprites import *
pygame.init()
import inputbox

def renderText(text):
    rendered = myfont.render(text,10,(0,0,0))
    return rendered

def roundedRect(surface, rect, color, radius = 0.4, text=None):
    rect = Rect(rect)
    color = Color(*color)
    
    alpha = 80
    
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0,0
    rectangle = Surface(rect.size, SRCALPHA)
    rectpos = rectangle.get_rect()
    
    circle       = Surface([min(rect.size)*3]*2,SRCALPHA)
    draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)
    
    textrect = text.get_rect()
    x = rectpos.centerx - textrect.centerx
    y = rectpos.centery - textrect.centery
    if text:
	rectangle.blit(text,(x,y))
    return surface.blit(rectangle,pos)    


screen = pygame.display.set_mode((500,500))
clock = pygame.time.Clock()
fps = 30
myfont = pygame.font.SysFont("monospace",15)

text1 = "143.248.12.189"
text2 = renderText("omega3love")

screen.fill(-1)
text = inputbox.ask(screen, "Type your name ")
button = Button((100,100),(50,50,200,50),(200,20,20),text)

running = True
while running:
    for ev in pygame.event.get():
	if ev.type == pygame.QUIT:
	    running = False
    screen.fill(-1)
    button.draw(screen)
    #roundedRect(screen,(50,50,200,50),(200,20,20),0.8, text1)
    #screen.blit(text1, (100,100))
    #screen.blit(text2, (100,200))
    
    pygame.display.update()
    clock.tick(fps)




quit()
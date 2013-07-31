#Main file for mah game.
import pygame
import world as World
import player as Player
#import player as Player
import ConfigParser
from controls import Control
from math import floor
import actions
import os

def do_input():
    keypresses = pygame.key.get_pressed()
    for c in controls:
        print c
        controls[c].update(keypresses[c])

def translate():
    #Move everything
    pass

def collide():
    #Check projectiles for collisions
    pass

def time():
    #Check timed objects against the global timer
    pass

def render():
    #Render the scene
    xtiles = windowx / tilewidth
    ytiles = windowy / tilewidth
    for x in range(xtiles):
        for y in range(ytiles):
            tile = world.get(int(floor(player.x + x - xtiles/2)), int(floor(player.y + y - ytiles/2)))
            screen.blit(tile_images[tile.type], (x*tilewidth, y*tilewidth))
    '''
    for y in range(int(config.get('world', 'y'))):
        for x in range(int(config.get('world', 'x'))):
            tile = world.get(x, y)
            #tile = world.tiles[x][y]
            if tile is not None:
                screen.blit(tile_images[tile.type], (x*tilewidth, y*tilewidth))
    '''

    pygame.display.flip()

config = ConfigParser.ConfigParser()
config.read("settings.cfg")
player = Player.Player([5, 5, 0])

'''
window = etc.Window()
'''
windowx = int(config.get('window', 'x'))
windowy = int(config.get('window', 'y'))
tilewidth = 32
screen = pygame.display.set_mode((windowx, windowy))
running = True

world = World.World(int(config.get('world', 'x')), int(config.get('world', 'y')), 10)
#world.load()

#Load control bindings
bindings = ConfigParser.ConfigParser()
bindings.read("bindings.cfg")
controls = {}
for binding in bindings.items('bindings'):
    #Add a Control object with Control.action = actionname, to the dictionary of bound controls
    controls[getattr(pygame, binding[0].upper())] = Control(getattr(actions, binding[1])())


#Load tile images
tile_images = {}
print os.listdir(".")
files = os.listdir("assets/images")
for i in files:
    if i[-4:] == ".jpg":
        tile_images[int(i[:-4])] = pygame.image.load("assets/images/" + i)

while running:
    print("WOOT SDFHJSDGJHDFJKAHGHJASFCD VASFCV DGB")
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = False

    do_input()
    translate()
    collide()
    time()
    render()
    
pygame.quit()

#Main file for mah game.
import pygame
import time
import world as World
import player as Player
#import player as Player
import ConfigParser
from controls import Control
from math import floor
import actions
import os

last_time = time.clock()

def do_input():
    keypresses = pygame.key.get_pressed()
    for key, control in controls.iteritems():
        control.update(keypresses[key], world=world, player=player, config=config)

def translate():
    player.update()
    #Move everything
    #dicks
    pass

def collide():
    #Check projectiles for collisions
    pass

def timer():
    #Check timed objects against the global timer
    global last_time
    print str(1.0 / (time.clock() - last_time)) + " FPS"
    last_time = time.clock()

def render():
    #Render the scene
    xtiles = windowx / tilewidth
    ytiles = windowy / tilewidth
    for x in range(xtiles + 1):
        for y in range(ytiles + 1):
            tile = world.get(int(floor(player.x + x - xtiles/2)), int(floor(player.y + y - ytiles/2)))
            screen.blit(tile_images[tile.type], ((x - player.x % 1)*tilewidth, (y - player.y % 1)*tilewidth))
    pygame.display.flip()

config = ConfigParser.ConfigParser()
config.read("settings.cfg")
player = Player.Player([20, 12, 0], config)

'''
window = etc.Window()
'''
windowx = int(config.get('window', 'x'))
windowy = int(config.get('window', 'y'))
tilewidth = 32
screen = pygame.display.set_mode((windowx, windowy))
#This cannot be done until display is initialised
from render import ScreenRegion, draw_world

running = True

world = World.World(x=int(config.get('world', 'x')), y=int(config.get('world', 'y')), z=10)
#world.load()


#Load control bindings
bindings = ConfigParser.ConfigParser()
bindings.optionxform = str
bindings.read("bindings.cfg")
controls = {}
for binding in bindings.items('bindings'):
    #Add a Control object with Control.action = actionname, to the dictionary of bound controls
    controls[getattr(pygame, binding[0])] = Control(getattr(actions, binding[1])())


#Load tile images
tile_images = {}
other_images = {}
print os.listdir(".")
files = os.listdir("assets/images")
for i in files:
    if i[-4:] == ".jpg":
        try:
            tile_images[int(i[:-4])] = pygame.image.load("assets/images/" + i).convert(32)
        except:
            other_images[i[:-4]] = pygame.image.load("assets/images/" + i).convert(32)


while running:
    #print("WOOT SDFHJSDGJHDFJKAHGHJASFCD VASFCV DGB")
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = False

    draw_world(world, player, screen, (45, 45, 640, 480), crop=True)
    pygame.display.flip()
    do_input()
    translate()
    timer()
    collide()
    #render()
    
pygame.quit()

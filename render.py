import pygame
from math import floor, ceil
import os
screenregions = []
tilewidth = 32
left, right, top, bottom = range(4)

import ConfigParser
config = ConfigParser.ConfigParser()
config.read("settings.cfg")
windowx = int(config.get('window', 'x'))
windowy = int(config.get('window', 'y'))
screen = pygame.display.set_mode((windowx, windowy))

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

class ScreenRegion:
    def __init__(self, rect, app, image=None):
        self.image = image
        self.rect = rect
        self.app = app

    def draw(self):
        self.app.screen.blit(self.image, self.rect)

    def action1(self, *args, **kwargs):
        return

    def action2(self, *args, **kwargs):
        return


#This SHOULD be faster than the below draw_world for large chunk sizes
def draw_world(game, player, rect, crop=False):
    world = game.world
    screen = game.screen
    xorig, yorig, w, h = rect
    #print "Rect is: %s" % repr(rect)
    xtiles = int(ceil(w / tilewidth)) + 1
    ytiles = int(ceil(h / tilewidth)) + 1
    xoffset = player.x % 1
    yoffset = player.y % 1
    world_rect = (int(floor(player.x - xtiles/2)), int(floor(player.y - ytiles/2)), xtiles, ytiles)
    #print "Passing %s to get_rect" % repr(world_rect)
    if not crop:
        #Draw the map straight to the screen
        region = world.get_rect(world_rect, player.z)
        for x in range(len(region)):
            for y in range(len(region[x])):
                tile = region[x][y]
                screen.blit(tile_images[tile.type if tile is not None else 0], 
                                (xorig + tilewidth + (x - xoffset)*tilewidth, 
                                 yorig + tilewidth + (y - yoffset)*tilewidth))

    else:
        #Draw the map to the buffer
        screenbuffer = pygame.Surface((w, h))
        region = world.get_rect(world_rect, player.z)
        #print region
        #sys.exit()
        for x in range(len(region)):
            for y in range(len(region[x])):
                tile = region[x][y]
                screenbuffer.blit(tile_images[tile.type if tile is not None else 0], 
                                    ((x - xoffset)*tilewidth, 
                                    (y - yoffset)*tilewidth))

        #Draw from the buffer to the screen
        screen.blit(screenbuffer, (xorig, yorig))

#Old one. Will be slower than the above for larger chunk sizes
'''
def draw_world(world, player, screen, rect, crop=False):
        xorig, yorig, w, h = rect

        xtiles = int(ceil(w / tilewidth))
        ytiles = int(ceil(h / tilewidth)) 
        xoffset = player.x % 1
        yoffset = player.y % 1

        if not crop:
            #Draw the map straight to the screen
            for x in range(xtiles + 1):
                for y in range(ytiles + 1):
                    tile = world.get(int(floor(player.x + x - xtiles/2)), int(floor(player.y + y - ytiles/2)))
                    screen.blit(tile_images[tile.type], (xorig + tilewidth + (x - xoffset)*tilewidth, 
                                                         yorig + tilewidth + (y - yoffset)*tilewidth))
        else:
            #Draw the map to the buffer
            screenbuffer = pygame.Surface((w, h))
            for x in range(xtiles + 1):
                for y in range(ytiles + 1):
                    tile = world.get(int(floor(player.x + x - xtiles/2)), int(floor(player.y + y - ytiles/2)))
                    screenbuffer.blit(tile_images[tile.type], ((x - xoffset)*tilewidth, 
                                                               (y - yoffset)*tilewidth))

            #Draw from the buffer to the screen
            screen.blit(screenbuffer, (xorig, yorig))
'''
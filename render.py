import pygame
import random
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
    if i[-4:] == ".png":
        try:
            tile_images[int(i[:-4])] = pygame.transform.scale(pygame.image.load("assets/images/" + i).convert(32), (32, 32))
        except ValueError:
            other_images[i[:-4]] = pygame.image.load("assets/images/" + i).convert(32)
        except:
            import traceback
            traceback.print_exc()

class TileTypeException(Exception):
    pass

#This SHOULD be faster than the below draw_world for large chunk sizes
def draw_world(world, player, screen, rect, crop=False):
    world = world
    screen = screen
    xorig, yorig, w, h = rect
    #print "Rect is: %s" % repr(rect)
    #xtiles = int(ceil(w / float(tilewidth))) + 1
    #ytiles = int(ceil(h / float(tilewidth))) + 1

    # Number of tiles on each axis that may be visible in our draw rect (integer)
    xtiles = w / tilewidth + 2
    ytiles = h / tilewidth + 2
    print "DONGS"
    print xtiles, ytiles

    # Offset of the player from the edge of the draw rect, mod 1 (world coords)
    xoffset = (player.x - w / (tilewidth * 2.0)) % 1
    yoffset = (player.y - h / (tilewidth * 2.0)) % 1

    # Offset of the world grid from the edge of the draw rect (pixels)
    rect_xoffset = int((w / 2.0) % 32)
    rect_yoffset = int((h / 2.0) % 32)
    print rect_xoffset, rect_yoffset

    # Offset of the player from the world grid (world coords)
    xoffset = player.x % 1# + ((w/2.0) % 32) / 32.0
    yoffset = player.y % 1# + ((h/2.0) % 32) / 32.0

    print w % 32, h % 32
    print xoffset, yoffset
    print "BUNP"
    print player.y, ytiles
    print int(floor(player.y - ytiles / 2.0))
    world_rect = (int(floor(player.x - xtiles/2.0)), int(floor(player.y - ytiles/2.0)), xtiles, ytiles)
    region = world.get_rect(world_rect, player.z)
    print region
    #print world_rect
    #print "Passing %s to get_rect" % repr(world_rect)
    if not crop:
        #Draw the map straight to the screen
        for x in range(len(region)):
            for y in range(len(region[x])):
                tile = region[x][y]
                tile_type = tile.type if tile is not None else 0
                try:
                    if random.randint(0, 99) == 0:
                        print xoffset
                        print x - xoffset
                        print x - xoffset * tilewidth

                    screen.blit(tile_images[tile_type], 
                                    (xorig + tilewidth + (x - xoffset)*tilewidth + 1/(tilewidth * 2 + 1), 
                                     yorig + tilewidth + (y - yoffset)*tilewidth + 1/(tilewidth * 2 + 1)))
                except KeyError:
                    raise TileTypeException("Attempted to render tile type that did not exist (not found in assets/images/): %s.png not found" % tile_type)

    else:
        # THIS SHIT IS BROKEN APPARENTLY. TWAS WORKING FOR FULL SCREEN SIZE. DOES NOT WORK NOW.
        #Draw the map to the buffer
        screenbuffer = pygame.Surface((w, h))
        #print region
        #sys.exit()
        for x in range(len(region)):
            for y in range(len(region[x])):
                tile = region[x][y]
                try:
                    tile_type = tile.type if tile is not None else 0
                    if random.randint(0, 2999) == 0 and y == 1:
                        print 'dongs'
                        print player.x, player.y
                        print x, y
                        print yoffset
                        print y - yoffset
                        print (y - yoffset) * tilewidth
                        print "DAGS"
                        print xoffset
                        print x - xoffset
                        print (x - xoffset) * tilewidth
                        

                    # RE: the adding of +0.4: The point of this is to scooch the
                    # whole world over by just a bit less than half a pixel The effect of this is
                    # that if you're at world co-ordinate 0.4999 you won't be at a different pixel
                    # co-ordinate to if you were at 0.5001 (by preventing the pixel change from
                    # happening in exactly the centre of the tile). This is important so that
                    # players colliding with objects closer to 0.0 don't see a 1-pixel gap
                    if y == 2:
                        print "breh"
                        print y, yoffset
                        print (y - yoffset) * tilewidth
                        print rect_yoffset
                    screenbuffer.blit(tile_images[tile_type], 
                                        ((x - xoffset)*tilewidth + rect_xoffset + 0.4, 
                                        (y - yoffset)*tilewidth + rect_yoffset + 0.4))
                except KeyError:
                    raise TileTypeException("Attempted to render tile type that did not exist (not found in assets/images/): %s.png not found" % tile_type)

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
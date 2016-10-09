import pygame
import random
from math import floor, ceil
import os
import sys
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

def draw_world(world, player, screen, rect, crop=False):
    draw_x, draw_y, draw_w, draw_h = rect

    # Almost all of this could be precalculated if rect was static
    # Calculate the world x/y at the origin
    world_x = player.x - draw_w/2.0/tilewidth
    world_y = player.y - draw_h/2.0/tilewidth
    # world_w/h is the w/h inclusive of all tiles only partially inside the draw rect
    world_w = int(ceil(float(draw_w) / tilewidth) + 1)
    world_h = int(ceil(float(draw_h) / tilewidth) + 1)

    world_rect = (int(floor(world_x)), int(floor(world_y)), world_w, world_h)
    world_region = world.get_rect(world_rect, player.z)

    if crop:
        screenbuffer = pygame.Surface((draw_w, draw_h))
        surface = screenbuffer
    else:
        surface = screen

    for x in range(world_w):
        for y in range(world_h):
            tile = world_region[x][y]
            tile_type = tile.type if tile is not None else 0
            try:
                tile_image = tile_images[tile_type]
            except KeyError:
                raise TileTypeException("Attempted to render tile type that did not exist (not found in assets/images/): %s.png not found" % tile_type)
            tile_draw_x = (x - world_x % 1) * tilewidth + 0.4
            tile_draw_y = (y - world_y % 1) * tilewidth + 0.4
            if not crop:
                # if we aren't drawing to a buffer we need to add the draw rects position within the screen at this time
                tile_draw_x += draw_x
                tile_draw_y += draw_y
            surface.blit(tile_images[tile_type], (tile_draw_x, tile_draw_y))

    if crop:
        #Draw from the buffer to the screen
        screen.blit(screenbuffer, (draw_x, draw_y))
import pygame
import world as World
import player as Player
#import player as Player
import ConfigParser
from controls import Control
from math import floor
from copy import deepcopy
import editor_actions
import os

worldname = 'test'

class ScreenRegion:
    def __init__(self, image, location, size, layer):
        self.events = {}
        self.image = image
        self.location = location
        self.size = size
        self.layer = layer

    def addEvent(self, event, function, *args):
        self.events[event] = (function, args)

    def doEvent(self, button, event, *args):
        function = self.events[button][0]
        args = self.events[button][1] + args
        function(*args)

def ClickTile(location, world):
    print "Tile at %s in world %d was clicked" % (str(location), world)

def do_input():
    keypresses = pygame.key.get_pressed()
    for key, control in controls.iteritems():
        control.update(keypresses[key], worlds=worlds, cameras=cameras, config=config)

    mpresses = pygame.mouse.get_pressed()
    mpos = pygame.mouse.get_pos()[:]
    for i in range(len(mpresses)):
        index = i+1
        if index in mcontrols:
            mcontrols[index].update(mpresses[i], 
                                    button_num=i+1,
                                    worlds=worlds, 
                                    cameras=cameras, 
                                    config=config, 
                                    screenregions=screenregions,
                                    mpos=mpos)


def render():
    #Render the scene
    '''
    xtiles = windowx / tilewidth
    ytiles = windowy / tilewidth
    for x in range(xtiles + 1):
        for y in range(ytiles + 1):
            tile = world.get(int(floor(player.x + x - xtiles/2)), int(floor(player.y + y - ytiles/2)))
            screen.blit(tile_images[tile.type], ((x - player.x % 1)*tilewidth, (y - player.y % 1)*tilewidth))
    '''

    for region in screenregions:
        if hasattr(region, 'image'):
            screen.blit(region.image, region.location)
    pygame.display.flip()

def redraw():

    #Render mini-world into corner pane (world 1)
    layer = 0
    xtiles = int(windowx * side_panel_width / tilewidth)
    ytiles = int(windowy * bottom_panel_height / tilewidth)
    draw_from = (windowx * (1 - side_panel_width), windowy * (1 - bottom_panel_height))
    for x in range(xtiles + 1):
        for y in range(ytiles + 1):
            world_location = [int(floor(cameras[1].x + x - xtiles/2)), int(floor(cameras[1].y + y - ytiles/2))]
            tile = worlds[1].get(*world_location)
            location = (draw_from[0] + (x - cameras[1].x % 1)*tilewidth, draw_from[1] + (y - cameras[1].y % 1)*tilewidth)
            region = ScreenRegion(tile_images[tile.type], location, (tilewidth, tilewidth), layer)
            #Last args after the first two are given to the ClickTile callback; 
            #the tiles location in the world, and which world it belongs to
            region.addEvent('MBUTTON_1', ClickTile, world_location[:], 1)
            screenregions.append(region)

    #Render main window of tiles (world 0)
    ytiles = int(windowy * (1 - bottom_panel_height) / tilewidth)
    xtiles = int(windowx * (1 - side_panel_width) / tilewidth)
    layer = 1
    draw_from = (0, 0)
    for x in range(xtiles + 1):
        for y in range(ytiles + 1):
            if x == xtiles and y == ytiles:
                #Crop this tile instead of rendering it over the minimap
            world_location = [int(floor(cameras[0].x + x - xtiles/2)), int(floor(cameras[0].y + y - ytiles/2))]
            tile = worlds[0].get(*world_location)
            location = (draw_from[0] + (x - cameras[0].x % 1)*tilewidth, draw_from[1] + (y - cameras[0].y % 1)*tilewidth)

            region = ScreenRegion(tile_images[tile.type], location, (tilewidth, tilewidth), layer)
            #Last args after the first two are given to the ClickTile callback; 
            #the tiles location in the world, and which world it belongs to
            region.addEvent('MBUTTON_1', ClickTile, world_location[:], 0)
            screenregions.append(region)


    #Render sidebars    
    #Bottom panel
    layer = 2
    sidebar = other_images['editor_sidebar']
    location = (0, int(round(windowy * (1 - bottom_panel_height))))
    dimensions = (int(round(windowx * (1- side_panel_width))), int(round(windowy * bottom_panel_height)))
    bottom_panel = pygame.Surface(dimensions)
    pygame.transform.scale(sidebar, dimensions, bottom_panel)
    region = ScreenRegion(bottom_panel, location, dimensions, layer)
    screenregions.append(region)

    #Side bar
    location = (int(round(windowx * (1 - side_panel_width))), 0)  
    dimensions = (int(round(windowx * side_panel_width)), int(round(windowy * (1 - bottom_panel_height))))
    side_panel = pygame.Surface(dimensions)
    pygame.transform.scale(sidebar, dimensions, side_panel)
    region = ScreenRegion(side_panel, location, dimensions, layer)
    screenregions.append(region)

    #Render buttons onto side panes
    layer = 3

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("settings.cfg")
    cameras = [Player.Player([0, 0, 0], config), Player.Player([0, 0, 0], config)]
    bottom_panel_height = 0.4
    side_panel_width = 0.3
    windowx = int(config.get('window', 'x'))
    windowy = int(config.get('window', 'y'))
    tilewidth = 32
    screen = pygame.display.set_mode((windowx, windowy))
    running = True

    worlds = [World.World(), World.World()]

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

    #Load control bindings
    bindings = ConfigParser.ConfigParser()
    bindings.optionxform = str
    bindings.read("bindings.cfg")
    controls = {}
    mcontrols = {}
    for binding in bindings.items('editor_bindings'):
        #Add a Control object with Control.action = actionname, to the dictionary of bound controls
        if binding[0].startswith('K_'):
            controls[getattr(pygame, binding[0])] = Control(getattr(editor_actions, binding[1])())
        elif binding[0].startswith('MBUTTON_'):
            mcontrols[int(binding[0].partition('_')[2])] = Control(getattr(editor_actions, binding[1])())

    screenregions = []
    worlds[0].load(worldname)
    worlds[1].load(worldname)
    redraw()
    for region in screenregions:
        #print region.events
        pass
    while running:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False
        
        do_input()
        render()


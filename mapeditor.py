import pygame
import world as World
import player as Player
#import player as Player
import ConfigParser
from controls import Control
from math import floor, ceil
from copy import deepcopy
import editor_actions
import time
import os

worldname = 'test'
global last_frame_time
last_frame_time = time.clock()

config = ConfigParser.ConfigParser()
config.read("settings.cfg")
cameras = [Player.Player([0.25, 0.25, 0], config), Player.Player([5, 5, 0], config)]
bottom_panel_height = 0.4
side_panel_width = 0.3
windowx = int(config.get('window', 'x'))
windowy = int(config.get('window', 'y'))
tilewidth = 32
layers = 5
screen = pygame.display.set_mode((windowx, windowy))

#This cannot be done until display is initialised
from render import ScreenRegion, draw_world

#Globals for mouse actions that persist between frames
active_world = 0
last_mpos = None
last_frame_time = None
drag_start = None

class WorldRegion(ScreenRegion):
    def __init__(self, image, rect, layer, worldnum):
        self.last_mpos = None
        self.world = worlds[worldnum]
        self.world.selection_start = None
        self.world.selection_end = None
        self.worldnum = worldnum
        self.camera = cameras[worldnum]
        ScreenRegion.__init__(self, image, rect, layer)

    def draw(self, screen):
        draw_world(self.world, self.camera, screen, self.rect, True)

        if self.world.selection_start is not None:
            #Draw the selection area
            start_pos = self.coords_to_pos(self.world.selection_start)
            end_mpos = self.coords_to_pos(self.world.selection_end)
            rect = [
                    end_mpos[0] if end_mpos[0] < start_pos[0] else start_pos[0],
                    end_mpos[1] if end_mpos[1] < start_pos[1] else start_pos[1],
                    abs(end_mpos[0] - start_pos[0]) + tilewidth,
                    abs(end_mpos[1] - start_pos[1]) + tilewidth
                   ]

            local_x = rect[0] - self.rect[0]
            local_y = rect[1] - self.rect[1]
            if local_x < 0:
                #for coordinates that land outside, set it to the edge of the draw area
                rect[0] = self.rect[0]
                #Reduce width to compensate
                rect[2] += local_x
            if local_y < 0:
                rect[1] = self.rect[1]
                rect[3] += local_y

            rect[2] = self.rect[0] + self.rect[2] - rect[0] if rect[0] + rect[2] > self.rect[0] + self.rect[2] else rect[2]
            rect[3] = self.rect[1] + self.rect[3] - rect[1] if rect[1] + rect[3] > self.rect[1] + self.rect[3] else rect[3]

            if rect[2] and rect[3]:
                selection_area = pygame.Surface(rect[2:])
                selection_area.fill((0, 0, 255))
                selection_area.set_alpha(100)
                screen.blit(selection_area, rect[:2])#(xorig, yorig))
            

    #NO TOUCHIE
    """
    def pos_to_coords(self, pos):
        return (int((pos[0] + cameras[self.world].x * tilewidth) / tilewidth - int(self.rect[2] / (2 * tilewidth))) - 1,
                int((pos[1] + cameras[self.world].y * tilewidth) / tilewidth - int(self.rect[3] / (2 * tilewidth))) - 1)

    def coords_to_pos(self, coords):
        return ((coords[0] + 1 + int(self.rect[2] / (2 * tilewidth))) * tilewidth - cameras[self.world].x * tilewidth,
                (coords[1] + 1 + int(self.rect[3] / (2 * tilewidth))) * tilewidth - cameras[self.world].y * tilewidth)
    """

    #Wooh arithmetic
    def pos_to_coords(self, pos):
        return (int((pos[0] + cameras[self.worldnum].x * tilewidth - self.rect[0] % tilewidth) / tilewidth - int(self.rect[2] / (2 * tilewidth))) - 1,
                int((pos[1] + cameras[self.worldnum].y * tilewidth - self.rect[1] % tilewidth) / tilewidth - int(self.rect[3] / (2 * tilewidth))) - 1)

    def coords_to_pos(self, coords):
        return ((coords[0] + 1 + int(self.rect[2] / (2 * tilewidth))) * tilewidth - cameras[self.worldnum].x * tilewidth + self.rect[0] % tilewidth,
                (coords[1] + 1 + int(self.rect[3] / (2 * tilewidth))) * tilewidth - cameras[self.worldnum].y * tilewidth + self.rect[1] % tilewidth)

    def PanWorld(self, button_string, button_event, mpos):
        global last_mpos, last_frame_time
        if button_event == "down":
            self.last_mpos = mpos
            last_frame_time = time.clock()
        else:
            delta = [(self.last_mpos[i] - mpos[i]) / float(tilewidth) for i in range(2)]
            #print delta
            #No dragging for vertical
            delta.append(0)
            cameras[self.worldnum].position = [cameras[self.worldnum].position[i] + delta[i] for i in range(3)]
            #print cameras[self.worldnum].position
            self.last_mpos = mpos
            
            frame_time = time.clock()
            #if frame_time - frame_time % 0.1 != last_frame_time - last_frame_time_time % 0.05:
            #    redraw()
            last_frame_time = frame_time

    def ClickTile(self, button_string, button_event, mpos):
        #Set selection to region between drag start and finish
        if button_event == "down":
            self.world.selection_start = self.pos_to_coords(mpos)
            self.world.selection_end = self.pos_to_coords(mpos)
        else:
            self.world.selection_end = self.pos_to_coords(mpos)
            active_world = self.worldnum

def do_input():
    keypresses = pygame.key.get_pressed()
    total_keys = len(keypresses)
    mpresses = pygame.mouse.get_pressed()
    mpos = pygame.mouse.get_pos()
    keypresses = keypresses + tuple([mpresses[i] for i in range(len(mpresses))])
    for keys, control in controls.iteritems():
        ##TODO
        control.update( all([keypresses[key] for key in keys]), 
                        keys=keys,
                        worlds=worlds, 
                        active_world=active_world,
                        cameras=cameras, 
                        config=config, 
                        screenregions=screenregions,
                        mpos=mpos)

def draw():
    layer = 0
    worldnum = 0
    #Render world 0 to the main window
    map_x = (1 - side_panel_width) * windowx
    map_y = (1 - bottom_panel_height) * windowy
    map_rect = (0, 0, map_x, map_y)
    draw_world(worlds[worldnum], cameras[worldnum], screen, map_rect, True)
    map_region = WorldRegion(None, map_rect, layer, worldnum)
    map_region.addEvent('MBUTTON_1', map_region.ClickTile)
    map_region.addEvent('MBUTTON_3', map_region.PanWorld)
    screenregions.append(map_region)

    #Render world 1 to the corner
    worldnum = 1
    map_x = side_panel_width * windowx
    map_y = bottom_panel_height * windowy
    map_rect = ((1 - side_panel_width) * windowx, (1 - bottom_panel_height) * windowy, map_x, map_y)
    draw_world(worlds[worldnum], cameras[worldnum], screen, map_rect, True)
    map_region = WorldRegion(None, map_rect, layer, worldnum)
    map_region.addEvent('MBUTTON_1', map_region.ClickTile)
    map_region.addEvent('MBUTTON_3', map_region.PanWorld)
    screenregions.append(map_region)
    #Render sidebars    
    #Bottom panel
    sidebar = other_images['editor_sidebar']
    location = (0, int(round(windowy * (1 - bottom_panel_height))))
    dimensions = (int(round(windowx * (1- side_panel_width))), int(round(windowy * bottom_panel_height)))
    bottom_panel = pygame.Surface(dimensions)
    pygame.transform.scale(sidebar, dimensions, bottom_panel)
    region = ScreenRegion(bottom_panel, location+dimensions, layer)
    screenregions.append(region)

    '''
    #Side bar
    location = (int(round(windowx * (1 - side_panel_width))), 0)  
    dimensions = (int(round(windowx * side_panel_width)), int(round(windowy * (1 - bottom_panel_height))))
    side_panel = pygame.Surface(dimensions)
    pygame.transform.scale(sidebar, dimensions, side_panel)
    region = ScreenRegion(side_panel, location, dimensions, layer)

    print "Rendering side panels took %f" % (timer - time.clock())
    timer = time.clock()
    '''
    #Render buttons onto side panes
    layer = 3

def redraw():
    tempregions = screenregions[:]
    for layer in range(layers):
        i = 0
        while i < len(tempregions):
            if tempregions[i].layer == layer:
                tempregions[i].draw(screen)
                poppedregion = tempregions.pop(i)
            else:
                i += 1


if __name__ == "__main__":


    running = True

    #First two worlds are the ones you see on the screen, third is copy buffer
    worlds = [World.World(worldnum = 0),
              World.World(worldnum = 1),
              World.World(worldnum = 2)]

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
    for binding in bindings.items('editor_bindings'):
        #Add a Control object with Control.action = actionname, to the dictionary of bound controls
        keys = []
        for item in binding[0].split('+'):
            if item.startswith('K_'):
                keys.append(getattr(pygame, item))
            elif item.startswith('MBUTTON_'):
                #we treat mouse buttons as keys. Don't know why thats so much to ask.
                keys.append(int(item[-1]) + len(pygame.key.get_pressed()) - 1) 
        keys = tuple(keys)
        print keys
        controls[keys] = Control(getattr(editor_actions, binding[1])())

    screenregions = []
    worlds[0].load(worldname)
    worlds[1].load(worldname)
    draw()
    for region in screenregions:
        #print region.events
        pass
    while running:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False
        
        redraw()
        do_input()
        pygame.display.flip()
        #render()


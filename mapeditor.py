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
screen = pygame.display.set_mode((windowx, windowy))

#This cannot be done until display is initialised
from render import ScreenRegion, draw_world

#Globals for mouse actions that persist between frames
last_mpos = None
last_frame_time = None
drag_start = None

class WorldRegion(ScreenRegion):
    def __init__(self, image, rect, layer, worldnum):
        self.last_mpos = None
        self.world = worldnum
        ScreenRegion.__init__(self, image, rect, layer)

    def draw(self, screen):
        draw_world(worlds[self.world], cameras[self.world], screen, self.rect, True)

#NO TOUCHIE
    def pos_to_coords(self, pos):
        return (int((pos[0] + cameras[self.world].x * tilewidth) / tilewidth - int(self.rect[2] / (2 * tilewidth))) - 1,
                int((pos[1] + cameras[self.world].y * tilewidth) / tilewidth - int(self.rect[3] / (2 * tilewidth))) - 1)

    def coords_to_pos(self, coords):
        return ((coords[0] + 1 + int(self.rect[2] / (2 * tilewidth))) * tilewidth - cameras[self.world].x * tilewidth,
                (coords[1] + 1 + int(self.rect[3] / (2 * tilewidth))) * tilewidth - cameras[self.world].y * tilewidth)

    def PanWorld(self, button_string, button_event, mpos):
        global last_mpos, last_frame_time
        if button_event == "down":
            last_mpos = mpos
            last_frame_time = time.clock()
        else:
            delta = [(last_mpos[i] - mpos[i]) / float(tilewidth) for i in range(2)]
            #No dragging for vertical
            delta.append(0)
            #print "Drag in progress; delta is " + repr(delta)
            #print cameras[world].position
            cameras[self.world].position = [cameras[self.world].position[i] + delta[i] for i in range(3)]
            last_mpos = mpos
            
            frame_time = time.clock()
            #if frame_time - frame_time % 0.1 != last_frame_time - last_frame_time % 0.05:
            #    redraw()
            last_frame_time = frame_time

    def ClickTile(self, button_string, button_event, mpos):
        global drag_start

        #Find the grid alignment offset created by player position mod 1
        player_xoffset = (cameras[self.world].x % 1) * tilewidth
        player_yoffset = (cameras[self.world].y % 1) * tilewidth

        #Set selection to region between drag start and finish
        if button_event == "down":
            ##THIS WORKS AND IS MAGIC
            self.world_drag_start = self.pos_to_coords(mpos)
            print self.world_drag_start
        elif button_event == "held":
            #rect = drag_start + (mpos[0] - drag_start[0], mpos[1] - drag_start[1])
            #pygame.draw.rect(screen, (0, 100, 255), rect, 2)

            start_pos = self.coords_to_pos(self.world_drag_start)
            grid_mpos = self.coords_to_pos(self.pos_to_coords(mpos))

            rect = [
                    grid_mpos[0] if grid_mpos[0] < start_pos[0] else start_pos[0],
                    grid_mpos[1] if grid_mpos[1] < start_pos[1] else start_pos[1],
                    abs(grid_mpos[0] - start_pos[0]) + tilewidth,
                    abs(grid_mpos[1] - start_pos[1]) + tilewidth
                   ]

            selection_area = pygame.Surface(rect[2:])
            selection_area.fill((0, 255, 0))
            selection_area.set_alpha(100)
            screen.blit(selection_area, rect[:2])#(xorig, yorig))
        else:
            #Set selection area for this world
            pass


#on-click event callbacks
#The args are specified on adding the event
#and kwargs passed in from the Activate Action. (button_event, mpos)
def ClickTile(location, world, **kwargs):
    print "Tile at %s in world %d was clicked" % (str(location), world)

def PanWorld(world,  button_event=None, mpos=None, **kwargs):
    print world
    if button_event == 'down':
        global last_mpos
        last_mpos = mpos
        global last_frame_time 
        last_frame_time = time.clock()
        print "Drag started"
    else:
        delta = [(last_mpos[i] - mpos[i]) / float(tilewidth) for i in range(2)]
        #No dragging for vertical
        delta.append(0)
        #print "Drag in progress; delta is " + repr(delta)
        #print cameras[world].position
        cameras[world].position = [cameras[world].position[i] + delta[i] for i in range(3)]
        last_mpos = mpos
        #redraw()

        frame_time = time.clock()
        #print frame_time
        #print frame_time - last_frame_time
        if frame_time - frame_time % 0.1 != last_frame_time - last_frame_time % 0.1:
            redraw()
        last_frame_time = frame_time

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
        if hasattr(region, 'image') and region.image:
            screen.blit(region.image, region.location)



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
    map_region.world = worldnum
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
    map_region.world = worldnum
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
    for region in screenregions:
        region.draw(screen)


if __name__ == "__main__":


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


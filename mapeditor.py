import pygame
import world as World
import player as Player
#import player as Player
import ConfigParser
from controls import Control
from math import floor, ceil
from copy import deepcopy
from render import draw_world, ScreenRegion, screen, windowx, windowy, other_images
from main import App
import editor_actions
import editor_actions as actions
import time
import os


##################################################################
##################################################################
###TODOPANTS
###TODO
###PANTS
###We definitely need to ditch every global variable and create an
###"app" object which contains all those fucking properties we are
###currently passing in like gronks
##################################################################
##################################################################

tilewidth = 32

class WorldRegion(ScreenRegion):
    def __init__(self, rect, app):
        self.rect = rect
        self.world = World.World()
        self.world.load('test')
        self.world.selection_start = None
        self.world.selection_end = None
        self.camera = Player.Player([5, 5, 0], app.config)

        #Keep a reference to the editor on the regions for things like 
        #setting the active Region, when a tile is clicked
        self.app = app

    def draw(self):
        screen = self.app.screen
        draw_world(self.app, self.camera, self.rect, True)

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

            if rect[2] > 0 and rect[3] > 0:
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
        return (int((pos[0] + self.camera.x * tilewidth - self.rect[0] % tilewidth) / tilewidth - int(self.rect[2] / (2 * tilewidth))) - 1,
                int((pos[1] + self.camera.y * tilewidth - self.rect[1] % tilewidth) / tilewidth - int(self.rect[3] / (2 * tilewidth))) - 1)

    def coords_to_pos(self, coords):
        return ((coords[0] + 1 + int(self.rect[2] / (2 * tilewidth))) * tilewidth - self.camera.x * tilewidth + self.rect[0] % tilewidth,
                (coords[1] + 1 + int(self.rect[3] / (2 * tilewidth))) * tilewidth - self.camera.y * tilewidth + self.rect[1] % tilewidth)

    def PanWorld(self, app, button_event):
        if button_event != "down":
            try: 
                delta = [(app.last_mpos[i] - app.mpos[i]) / float(tilewidth) for i in range(2)]
            except:
                #Whoa! What a fuckin' edge case
                self.PanWorld(app, "down")
                return
            #print delta
            #No dragging for vertical
            delta.append(0)
            self.camera.position = [self.camera.position[i] + delta[i] for i in range(3)]
            #print self.camera.position
            
            frame_time = time.clock()
            #if frame_time - frame_time % 0.1 != last_frame_time - last_frame_time_time % 0.05:
            #    redraw()
            last_frame_time = frame_time

    def ClickTile(self, app, button_event):
        #Set selection to region between drag start and finish
        if button_event == "down":
            self.world.selection_start = self.pos_to_coords(app.mpos)
            self.world.selection_end = self.pos_to_coords(app.mpos)
        else:
            self.world.selection_end = self.pos_to_coords(app.mpos)
            self.app.active_world = self

    action1 = ClickTile
    action2 = PanWorld

class MapEditor(App):
    def __init__(self):
        App.__init__(self)
        self.worldname = 'test'
        self.last_frame_time = time.clock()

        self.bottom_panel_height = 0.4
        self.side_panel_width = 0.3
        self.config = ConfigParser.ConfigParser()
        self.config.read("settings.cfg")
        self.windowx = windowx
        self.windowy = windowy
        self.screen = screen
        self.tilewidth = tilewidth

        #Globals for mouse actions that persist between frames
        self.active_world = 0
        
        self.mpos = None
        self.last_mpos = None
        
        self.frame_time = time.clock()
        self.last_frame_time = None

        self.drag_start = None

        #First two worlds are the ones you see on the screen, third is copy buffer
        self.copybuffer = World.World()

        #Import tile images from render.py

        #TODOPANTS
        #We definitely need to reassess how we're doing the bindings (+ combined bindings)
        #Load control bindings
        self.bindings = ConfigParser.ConfigParser()
        self.bindings.optionxform = str
        self.bindings.read("bindings.cfg")
        self.controls = {}
        for binding in self.bindings.items('editor_bindings'):
            #Add a Control object with Control.action = actionname, to the dictionary of bound controls
            keys = []
            for item in binding[0].split('+'):
                if item.startswith('K_'):
                    keys.append(getattr(pygame, item))
                elif item.startswith('MBUTTON_'):
                    #we treat mouse buttons as keys. Don't know why thats so much to ask.
                    keys.append(int(item[-1]) + len(pygame.key.get_pressed()) - 1) 
            keys = tuple(keys)
            self.controls[keys] = Control(getattr(editor_actions, binding[1])())

        self.screenregions = []
        self.draw()
        for region in self.screenregions:
            #print region.events
            pass

    def main(self):
        while self.running:
            #Timing
            self.last_frame_time = self.frame_time
            self.frame_time = time.clock()

            #Check for exit event
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                running = False
            
            self.redraw()
            self.do_input()
            
            #Render to the display
            pygame.display.flip()

    def do_input(self):
        self.last_mpos = self.mpos
        self.mpos = pygame.mouse.get_pos()
        keypresses = pygame.key.get_pressed()
        total_keys = len(keypresses)
        mpresses = pygame.mouse.get_pressed()
        keypresses = keypresses + tuple([mpresses[i] for i in range(len(mpresses))])
        for keys, control in self.controls.iteritems():
            ##TODO
            self.update_control(control, all([keypresses[key] for key in keys]))

    def draw(self):
        #Render world 0 to the main window
        map_x = (1 - self.side_panel_width) * self.windowx
        map_y = (1 - self.bottom_panel_height) * self.windowy
        map_rect = (0, 0, map_x, map_y)
        map_region = WorldRegion(map_rect, self)
        self.screenregions.append(map_region)

        #Render world 1 to the corner
        map_x = self.side_panel_width * self.windowx
        map_y = self.bottom_panel_height * self.windowy
        map_rect = ((1 - self.side_panel_width) * self.windowx, (1 - self.bottom_panel_height) * self.windowy, map_x, map_y)
        map_region = WorldRegion(map_rect, self)
        self.screenregions.append(map_region)
        #Render sidebars    
        #Bottom panel
        sidebar = other_images['editor_sidebar']
        location = (0, int(round(self.windowy * (1 - self.bottom_panel_height))))
        dimensions = (int(round(self.windowx * (1- self.side_panel_width))), int(round(self.windowy * self.bottom_panel_height)))
        bottom_panel = pygame.Surface(dimensions)
        pygame.transform.scale(sidebar, dimensions, bottom_panel)
        region = ScreenRegion(location+dimensions, self, image=bottom_panel)
        self.screenregions.append(region)

        #Side bar
        location = (int(round(self.windowx * (1 - self.side_panel_width))), 0)  
        dimensions = (int(round(self.windowx * self.side_panel_width)), int(round(self.windowy * (1 - self.bottom_panel_height))))
        side_panel = pygame.Surface(dimensions)
        pygame.transform.scale(sidebar, dimensions, side_panel)
        region = ScreenRegion(location+dimensions, self, image=side_panel)
        self.screenregions.append(region)
        
        #Render buttons onto side panes

    def redraw(self):
        for region in self.screenregions:
            region.draw()

if __name__ == "__main__":
    editor = MapEditor()
    editor.main()





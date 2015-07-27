import pygame
import world as World
import player as Player
#import player as Player
import ConfigParser
from controls import load_controls
from math import floor, ceil
from copy import deepcopy
from render import draw_world, screen, windowx, windowy, other_images, tile_images
from ui import ScreenRegion, WorldRegion, TileSelectButton, DropDownMenu
from main import App
import editor_actions
import editor_actions as actions
import time
import os

tilewidth = 32


class MapEditor(App):
    def __init__(self):
        App.__init__(self)
        self.worldname = 'test'
        self.last_frame_time = time.clock()

        self.bottom_panel_height = 0.4
        self.side_panel_width = 0.3
        self.primary_colour = (70, 70, 180)
        self.secondary_colour = (30, 30, 100)
        self.config = ConfigParser.ConfigParser()
        self.config.read("settings.cfg")
        self.pure_bindings = bool(int(self.config.get('editor', 'pure_bindings')))
        self.windowx = windowx
        self.windowy = windowy
        self.screen = screen
        self.tilewidth = tilewidth

        #Globals for mouse actions that persist between frames
        self.active_world = None
        self.frame_time = time.clock()
        self.last_frame_time = None

        self.drag_start = None
        self.selected_tile_type = 0

        #First two worlds are the ones you see on the screen, third is copy buffer
        self.copybuffer = World.World()

        #Import tile images from render.py
        self.controls = load_controls('editor_bindings')


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
        #sidebar = other_images['editor_sidebar']
        location = (0, int(round(self.windowy * (1 - self.bottom_panel_height))))
        dimensions = (int(round(self.windowx * (1- self.side_panel_width))), int(round(self.windowy * self.bottom_panel_height)))
        bottom_panel = pygame.Surface(dimensions)
        bottom_panel.fill(self.secondary_colour)
        #pygame.transform.scale(sidebar, dimensions, bottom_panel)
        region = ScreenRegion(location+dimensions, self, image=bottom_panel)
        self.screenregions.append(region)

        #Side bar
        location = (int(round(self.windowx * (1 - self.side_panel_width))), 0)  
        dimensions = (int(round(self.windowx * self.side_panel_width)), int(round(self.windowy * (1 - self.bottom_panel_height))))
        side_panel = pygame.Surface(dimensions)
        side_panel.fill(self.secondary_colour)
        #pygame.transform.scale(sidebar, dimensions, side_panel)
        sidepane_region = ScreenRegion(location+dimensions, self, image=side_panel)
        self.screenregions.append(sidepane_region)
        
        #Render buttons onto side panes
        base_location = [location[0] + 5, location[1] + 5]
        n_per_line = int(self.windowx * self.side_panel_width % self.tilewidth)
        print n_per_line
        done = False
        i = 0
        while not done:
            for j in range(n_per_line):
                tile_type = i*n_per_line+j
                if tile_type in tile_images:
                    location = [self.tilewidth*j, self.tilewidth*i]
                    dimensions = [self.tilewidth, self.tilewidth]
                    region = TileSelectButton(location+dimensions, self, tile_type)
                    sidepane_region.sub_regions.append(region)
                else:
                    done = True
            i += 1

        ###TODO world save dropdown
        region = DropDownMenu([0, 0, 200, 30], self)
        self.screenregions.append(region)
        #YEAHBOI





    def redraw(self):
        for region in self.screenregions:
            region.draw((0,0))

if __name__ == "__main__":
    editor = MapEditor()
    editor.main()





import player as Player
import world as World
from render import draw_world, tile_images, other_images
import pygame
import time
import os
from util import defaultdict
from actions import LeftActivate, RightActivate
import random
from math import floor, ceil

MOUSE1 = len(pygame.key.get_pressed()) + 1
# Mouse3 is right click. FUCK YOU PYGAME
MOUSE3 = len(pygame.key.get_pressed()) + 3

class ScreenRegion:
    signal_handlers = {}
    def __init__(self, rect, app, image=None, text=None):
        self.image = image
        self.text = text
        self.rect = rect
        self.app = app
        self.clickable = True
        self.sub_regions = []

    def gains_focus(self):
        if self.app.object_with_focus not in [self, None]:
            self.app.object_with_focus.loses_focus()

    def draw(self, offset):
        blit_rect = [self.rect[0] + offset[0], self.rect[1] + offset[1], self.rect[2], self.rect[3]]
        if self.image:
            self.app.screen.blit(self.image, blit_rect)

        if self.text:
            font = pygame.font.Font(None, 36)
            ourtext = font.render(self.text, 1, (255, 255, 255))
            self.app.screen.blit(ourtext, blit_rect)
        
        for region in self.sub_regions:
            region.draw(blit_rect[:2])

    #Used for sending mouse signals recursively down the screenregion heirarchy.
    def signal(self, signal, mpos, button_event):
        #Before comparing to subregions, convert to local coordinates
        mpos = [mpos[0] - self.rect[0], mpos[1] - self.rect[1]]
        #Ascertain which region we have clicked within
        for region in reversed(self.sub_regions):
            if region.clickable\
            and region.rect[0] < mpos[0] < (region.rect[0] + region.rect[2])\
            and region.rect[1] < mpos[1] < (region.rect[1] + region.rect[3]):
                #Pass the signal down to the next region in the heirarchy
                
                region.signal(signal, mpos, button_event)
                return

        #If the click landed within no subregions, it was destined for us
        #Fire the signal handler
        if signal in self.signal_handlers:
            handler, args = self.signal_handlers[signal]
            handler(self, button_event, *args)

class ScreenRegionSignalsParent(ScreenRegion):
    def __init__(self, rect, app, parent, **kwargs):
        ScreenRegion.__init__(self, rect, app, **kwargs)
        self.parent = parent

    #Used for sending mouse signals recursively down the screenregion heirarchy.
    def signal(self, signal, mpos, button_event):
        #Before comparing to subregions, convert to local coordinates
        mpos = [mpos[0] - self.rect[0], mpos[1] - self.rect[1]]
        #Ascertain which region we have clicked within
        for region in reversed(self.sub_regions):
            if region.clickable\
            and region.rect[0] < mpos[0] < (region.rect[0] + region.rect[2])\
            and region.rect[1] < mpos[1] < (region.rect[1] + region.rect[3]):
                #Pass the signal down to the next region in the heirarchy
                
                region.signal(signal, mpos, button_event)
                return

        #If the click landed within no subregions, it was destined for us
        #Fire the signal handler
        if signal in self.signal_handlers:
            handler, args = self.signal_handlers[signal]
            handler(button_event, *args)

class WorldRegion(ScreenRegion):
    def __init__(self, rect, app):
        ScreenRegion.__init__(self, rect, app)
        self.world = World.World()
        self.world.load('test')
        self.world.selection_start = None
        self.world.selection_end = None
        self.camera = Player.Player([5, 5, 0], app.config)

    def draw(self, offset):
        screen = self.app.screen
        blit_rect = [self.rect[0] + offset[0], self.rect[1] + offset[1], self.rect[2], self.rect[3]]
        draw_world(self.world, self.camera, self.app.screen, blit_rect, True)

        if self.world.selection_start is not None:
            #Draw the selection area
            start_pos = self.screen_from_world([floor(value) for value in self.world.selection_start])
            end_mpos = self.screen_from_world([floor(value) for value in self.world.selection_end])

            rect = [
                    end_mpos[0] if end_mpos[0] < start_pos[0] else start_pos[0],
                    end_mpos[1] if end_mpos[1] < start_pos[1] else start_pos[1],
                    abs(end_mpos[0] - start_pos[0]) + self.app.tilewidth,
                    abs(end_mpos[1] - start_pos[1]) + self.app.tilewidth
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

    def screen_from_world(self, coords):
        # calculates screen draw coordinates from world coordinates
        xorig, yorig, w, h = self.rect
        
        # world_*orig == World coordinate at xorig
        # *offset == screen distance between left of world, and left of world render box
        world_xorig = self.camera.x - w / 2.0 / self.app.tilewidth
        xoffset = xorig - world_xorig * self.app.tilewidth
        screen_x = xoffset + coords[0] * self.app.tilewidth


        world_yorig = self.camera.y - h / 2.0 / self.app.tilewidth
        yoffset = yorig - world_yorig * self.app.tilewidth
        screen_y = yoffset + coords[1] * self.app.tilewidth
        return (screen_x, screen_y)

    def world_from_screen(self, coords):
        # Calculate world coordinates from screen coordinates
        xorig, yorig, w, h = self.rect

        # world_*orig == World coordinate at xorig
        # *offset == screen distance between left of world, and left of world render box
        world_xorig = self.camera.x - w / 2.0 / self.app.tilewidth
        world_xoffset = float(xorig) / self.app.tilewidth - world_xorig
        world_x = float(coords[0]) / self.app.tilewidth - world_xoffset

        world_yorig = self.camera.y - h / 2.0 / self.app.tilewidth
        world_yoffset = float(yorig) / self.app.tilewidth - world_yorig
        world_y = float(coords[1]) / self.app.tilewidth - world_yoffset
        return (world_x, world_y)

    def PanWorld(self, button_event):
        if button_event != "down":
            try: 
                delta = [(self.app.last_mpos[i] - self.app.mpos[i]) / float(self.app.tilewidth) for i in range(2)]
            except:
                #Whoa! What a fuckin' edge case
                #....what edge case IS this? how does this fix even work? The above comment is all that existed pertaining to it.
                print "COCKSCOCKSCOCKSCOCKSCOCKS"
                print "COCKSCOCKSCOCKSCOCKSCOCKS"
                print "COCKSCOCKSCOCKSCOCKSCOCKS"
                self.PanWorld("down")
                return
            #print delta
            #No dragging for vertical, append a z delta of 0
            delta.append(0)
            self.camera.position = [self.camera.position[i] + delta[i] for i in range(3)]
            #print self.camera.position
            
            frame_time = time.clock()
            #if frame_time - frame_time % 0.1 != last_frame_time - last_frame_time_time % 0.05:
            #    redraw()
            last_frame_time = frame_time

    def ClickTile(self, button_event):
        self.gains_focus()
        #Set selection to region between drag start and finish
        if button_event == "down":
            self.world.selection_start = self.world_from_screen(self.app.mpos)
            self.world.selection_end = self.world_from_screen(self.app.mpos)
        else:
            self.world.selection_end = self.world_from_screen(self.app.mpos)
            self.app.active_world = self.world

        self.world.selection_z = self.camera.z
        if button_event == "up":
            print "This is selection start/end"
            print self.world.selection_start
            print self.world.selection_end
        #print self.world.selection_start

    signal_handlers = {1:(ClickTile, ()), 3:(PanWorld, ())}

class TileSelectButton(ScreenRegion):
    def __init__(self, rect, app, tile_type):
        ScreenRegion.__init__(self, rect, app)
        self.image=tile_images[tile_type]
        self.tile_type = tile_type

    def SelectTileType(self, button_event):
        self.gains_focus()
        self.app.selected_tile_type = self.tile_type
        print self.app.selected_tile_type
    signal_handlers = {1:(SelectTileType,())}

class DropDownMenu(ScreenRegion):
    def __init__(self, rect, app, items=[]):
        ScreenRegion.__init__(self, rect, app)
        self.collapsed_rect = self.rect[:]
        self.items = items
        #TODO: REMOVE
        self.items = ['Honk', 'Badonkadonk']
        self.deployed = False
        self.max_simultaneous = 5
        #Create the collapsed image for the dropdown
        self.collapsed_image = pygame.Surface(rect[2:])
        self.collapsed_image.fill(self.app.primary_colour)
        self.image = self.collapsed_image

        #Create the deploy button
        rect = [5, 5, self.rect[3] - 10, self.rect[3] - 10]
        rect = [self.rect[2] - (self.rect[3] - 5), 5, self.rect[3] - 10, self.rect[3] - 10]
        dropdown_button_image = pygame.Surface(rect[2:])
        #dropdown_button_image.fill(self.app.primary_colour)
        dropdown_button_image.fill((155, 155, 155))
        self.dropdown_button_image = dropdown_button_image
        self.dropdown_button = ScreenRegionSignalsParent(rect, self.app, self, image=dropdown_button_image)
        self.dropdown_button.signal_handlers = {1:(self.toggle_deploy, ())}
        self.sub_regions = [self.dropdown_button]

        self.update()

    #To be called externally whenever the contents of the menu needs to be updated. Intended to be overridden
    def update(self):
        pass

    def add_item(self, item):
        self.items.append(item)
        self.refresh()

    def remove_item(self, item):
        self.items.remove(item)
        self.refresh()

    def toggle_deploy(self, button_event):
        self.gains_focus()
        if button_event == "up":
            print "BADONKADONK"
            if self.deployed:
                print "Deployed: collapsing"
                self.rect = self.collapsed_rect
                self.sub_regions = [self.dropdown_button]
            else:
                print "Not deployed: Deploying"
                #Add the buttons for each item, and expand the rect to house all the new entries
                self.rect = self.collapsed_rect[:]
                self.rect[3] = self.rect[3] * (len(self.items) + 1)
                for i in range(len(self.items)):
                    item = self.items[i]
                    screenregion = ScreenRegionSignalsParent([0, (i+1)*self.collapsed_rect[3], self.collapsed_rect[2], self.collapsed_rect[3]], self.app, self, image=self.image, text=item)
                    screenregion.signal_handlers = {1:(self.select_item, (item,))}
                    self.sub_regions.append(screenregion)

            self.deployed = not self.deployed

    def loses_focus(self):
        self.deployed = False

    def select_item(self, button_event, item):
        if button_event == "up":
            print item
            self.selected_item = item
            self.text = item
            self.toggle_deploy(button_event)
        
class ListDirDropDownMenu(DropDownMenu):
    def __init__(self, rect, app, target_dir):
        self.target_dir = target_dir
        DropDownMenu.__init__(self, rect, app, items=[])
    def update(self):
        self.items = os.listdir(self.target_dir)
    

class TextField(ScreenRegion):
    def __init__(self, *args, **kwargs):
        ScreenRegion.__init__(self, *args, **kwargs)
        self.textbox_controls = {}
        for mod_combo in [(False, False, False), (False, False, True)]:
            self.textbox_controls[mod_combo] = defaultdict(lambda key: self.type_key)
            self.textbox_controls[mod_combo][MOUSE1] = LeftActivate
            self.textbox_controls[mod_combo][MOUSE3] = RightActivate
        self.text = "dongs"

    def gains_focus(self):
        # Should probably standardise the superclass calls :| I think i started this project before i knew about super()
        super(TextField, self).gains_focus()
        self.app_controls = self.app.controls
        self.app_pure_bindings = self.app.pure_bindings
        
        self.app.pure_bindings = False
        self.app.controls = self.textbox_controls

    def type_key(self, inkey):
        if inkey == K_BACKSPACE:
          current_string = current_string[0:-1]
        elif inkey == K_RETURN:
          return # Later textfields will "submit" on ENTER
        elif inkey == K_MINUS:
          current_string.append("_")
        elif inkey <= 127:
          current_string.append(chr(inkey))
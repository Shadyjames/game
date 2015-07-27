import player as Player
import world as World
from render import draw_world, tile_images, other_images
import pygame
import time

class ScreenRegion:
    signal_handlers = {}
    def __init__(self, rect, app, image=None):
        self.image = image
        self.rect = rect
        self.app = app
        self.clickable = True
        self.sub_regions = []

    def draw(self, offset):
        blit_rect = [self.rect[0] + offset[0], self.rect[1] + offset[1], self.rect[2], self.rect[3]]
        if self.image:
            self.app.screen.blit(self.image, blit_rect)
        
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
            self.signal_handlers[signal](self, button_event)

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
            start_pos = self.coords_to_pos(self.world.selection_start)
            end_mpos = self.coords_to_pos(self.world.selection_end)
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
            

    #NO TOUCHIE
    """
    #Wooh arithmetic
    def pos_to_coords(self, pos):
        return (int((pos[0] + self.camera.x * self.app.tilewidth - self.rect[0]) / self.app.tilewidth - int(self.rect[2] / (2 * self.app.tilewidth))) - 1,
                int((pos[1] + self.camera.y * self.app.tilewidth - self.rect[1]) / self.app.tilewidth - int(self.rect[3] / (2 * self.app.tilewidth))) - 1)

    def coords_to_pos(self, coords):
        return ((coords[0] + 1 + int(self.rect[2] / (2 * self.app.tilewidth))) * self.app.tilewidth - self.camera.x * self.app.tilewidth + self.rect[0],
                (coords[1] + 1 + int(self.rect[3] / (2 * self.app.tilewidth))) * self.app.tilewidth - self.camera.y * self.app.tilewidth + self.rect[1])
    """

    #Wooh arithmetic
    def pos_to_coords(self, pos):
        return (int((pos[0] + self.camera.x * self.app.tilewidth - self.rect[0]) / self.app.tilewidth - int(self.rect[2] / (2 * self.app.tilewidth))) - 1,
                int((pos[1] + self.camera.y * self.app.tilewidth - self.rect[1]) / self.app.tilewidth - int(self.rect[3] / (2 * self.app.tilewidth))) - 1)

    def coords_to_pos(self, coords):
        return ((coords[0] + 1 + int(self.rect[2] / (2 * self.app.tilewidth))) * self.app.tilewidth - self.camera.x * self.app.tilewidth + self.rect[0],
                (coords[1] + 1 + int(self.rect[3] / (2 * self.app.tilewidth))) * self.app.tilewidth - self.camera.y * self.app.tilewidth + self.rect[1])

    def PanWorld(self, button_event):
        if button_event != "down":
            try: 
                delta = [(self.app.last_mpos[i] - self.app.mpos[i]) / float(self.app.tilewidth) for i in range(2)]
            except:
                #Whoa! What a fuckin' edge case
                #....what edge case IS this? how does this fix even work?
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
        #Set selection to region between drag start and finish
        if button_event == "down":
            self.world.selection_start = self.pos_to_coords(self.app.mpos)
            self.world.selection_end = self.pos_to_coords(self.app.mpos)
        else:
            self.world.selection_end = self.pos_to_coords(self.app.mpos)
            self.app.active_world = self.world

        self.world.selection_z = self.camera.z
        #print self.world.selection_start
        #print self.world.selection_end
        #print self.world.selection_start

    signal_handlers = {1:ClickTile, 3:PanWorld}

class TileSelectButton(ScreenRegion):
    def __init__(self, rect, app, tile_type):
        ScreenRegion.__init__(self, rect, app)
        self.image=tile_images[tile_type]
        self.tile_type = tile_type

    def SelectTileType(self, button_event):
        self.app.selected_tile_type = self.tile_type
        print self.app.selected_tile_type
    signal_handlers = {1:SelectTileType}

class DropDownMenu(ScreenRegion):
    def __init__(self, rect, app, items=[]):
        ScreenRegion.__init__(self, rect, app)
        self.items = items
        self.deployed = False
        self.max_simultaneous = 5
        #Create the collapsed image for the dropdown
        self.collapsed_image = pygame.Surface(rect[2:])
        self.collapsed_image.fill(self.app.secondary_colour)
        self.image = self.collapsed_image

        #Create the deploy button
        rect = [5, 5, self.rect[3] - 10, self.rect[3] - 10]
        dropdown_button_image = pygame.Surface(rect[2:])
        dropdown_button_image.fill(self.app.primary_colour)
        self.dropdown_button = ScreenRegion(rect, self.app, image=dropdown_button_image)

        self.refresh_items()

    def refresh_items(self):
        #And also adjust our own self.image and self.rect depending on deployed state in deploy_toggle()
        #Create our sub_regions list for deployed, and not deployed.
        ###LEFT OFF HERE

        self.sub_regions = [region]

    def add_item(self, item):
        self.items.append(item)
        self.refresh_items()


    def remove_item(self, item):
        self.items.remove(item)
        self.refresh_items()

    '''
    def draw(self, offset):
        print "COCKS"
        screen = self.app.screen
        blit_rect = [self.rect[0] + offset[0], self.rect[1] + offset[1], self.rect[2], self.rect[3]]
    '''
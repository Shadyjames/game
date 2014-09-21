#Main file for mah game.
import pygame
import time
import world as World
import player as Player
#import player as Player
import ConfigParser
from controls import Control
from render import screen, draw_world, windowx, windowy
from math import floor
import actions
import os

last_time = time.clock()


class App:
    def __init__(self):
        self.running = True
        self.last_time = time.clock()
        self.config = ConfigParser.ConfigParser()
        self.config.read("settings.cfg")
        self.player = Player.Player([20, 12, 0], self.config)
        self.windowx = windowx
        self.windowy = windowy
        self.tilewidth = 32
        self.screen = screen
        
        self.world = World.World(x=int(self.config.get('world', 'x')), y=int(self.config.get('world', 'y')), z=10)
        #world.load()

        #Load control bindings
        self.bindings = ConfigParser.ConfigParser()
        self.bindings.optionxform = str
        self.bindings.read("bindings.cfg")
        self.controls = {}

        #Load tile images
        self.tile_images = {}
        self.other_images = {}
        files = os.listdir("assets/images")
        for i in files:
            if i[-4:] == ".jpg":
                try:
                    self.tile_images[int(i[:-4])] = pygame.image.load("assets/images/" + i).convert(32)
                except:
                    self.other_images[i[:-4]] = pygame.image.load("assets/images/" + i).convert(32)


    def update_control(self, control, state):
        if control.time_to_ready > 0:
            control.state = state
            return
        if control.state == False and state == True:
            print control.action
            control.action.go('down', self)
        elif control.state == True and state == False:
            control.action.go('up', self)
        elif state == True:
            control.action.go('held', self)
        control.time_to_ready  = getattr(control.action, 'cooldown', 0)
        control.state = state

    def do_input(self):
        self.last_mpos = self.mpos
        self.mpos = pygame.mouse.get_pos()
        keypresses = pygame.key.get_pressed()
        total_keys = len(keypresses)
        mpresses = pygame.mouse.get_pressed()
        keypresses = keypresses + tuple([mpresses[i] for i in range(len(mpresses))])
        if self.pure_bindings:
            for key, control in self.controls.iteritems():
                self.update_control(control, keypresses[key])
        else:
            mods = tuple\
                    ([
                        any([keypresses[pygame.K_LCTRL], keypresses[pygame.K_RCTRL]]),
                        any([keypresses[pygame.K_LALT], keypresses[pygame.K_RALT]]),
                        any([keypresses[pygame.K_LSHIFT], keypresses[pygame.K_RSHIFT]])
                    ])
            primary_controls = self.controls.get(mods, {})
            secondary_controls = self.controls[(False, False, False)]
            for key, control in primary_controls.iteritems():
                self.update_control(control, keypresses[key])
            #If there's modifier keys held down, don't halt all activity on keys that use non-modifier bindings
            for key, control in secondary_controls.iteritems():
                if key not in primary_controls:
                    self.update_control(control, keypresses[key])

class Game(App):
    def __init__(self):
        App.__init__(self)
        self.pure_bindings = bool(int(self.config.get('game', 'pure_bindings')))
        self.controls = load_controls('bindings', pure=self.pure_bindings)
    def main(self):
        while self.running:
            #print("WOOT SDFHJSDGJHDFJKAHGHJASFCD VASFCV DGB")
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                self.running = False

            draw_world(self, (45, 45, 640, 480), crop=True)
            pygame.display.flip()
            self.do_input()
            self.translate()
            self.timer()
            self.collide()

        pygame.quit()


    def translate(self):
        self.player.update()
        #Move everything
        #dicks
        pass

    def collide(self):
        #Check projectiles for collisions
        pass

    def timer(self):
        #Check timed objects against the global timer
        global last_time
        print str(1.0 / (time.clock() - last_time)) + " FPS"
        last_time = time.clock()

    def render(self):
        #Render the scene
        xtiles = self.windowx / self.tilewidth
        ytiles = self.windowy / self.tilewidth
        for x in range(xtiles + 1):
            for y in range(ytiles + 1):
                tile = self.world.get(int(floor(self.player.x + x - xtiles/2)), int(floor(self.player.y + y - ytiles/2)))
                self.screen.blit(self.tile_images[tile.type], ((x - player.x % 1)*tilewidth, (y - player.y % 1)*tilewidth))
        pygame.display.flip()


'''
window = etc.Window()
'''

if __name__ == "__main__":
    game = Game()
    game.main()